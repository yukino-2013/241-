#!/usr/bin/env python3
"""
智能运维助手 - Streamlit 前端界面 v2.4
提供聊天对话界面，调用后端 LangChain 智能体 API
功能：对话 + 快捷按钮 + 侧边栏 + 多轮记忆 + 打字效果 + 加载动画
      + 错误处理 + 对话历史 + 思考过程面板 + 可视化面板（v2.4新增）
可视化：系统指标仪表盘 + 服务状态看板 + 对话分析面板
"""

import uuid
import time
import json
import re
from datetime import datetime
import streamlit as st
import requests
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ──────────────────────────────────────────
# 自定义CSS样式
# ──────────────────────────────────────────
st.markdown("""
<style>
/* 加载动画 */
@keyframes fadeIn {
    from { opacity: 0; transform: translateY(10px); }
    to { opacity: 1; transform: translateY(0); }
}
.stChatMessage {
    animation: fadeIn 0.3s ease-in-out;
}

/* 思考中动画 */
@keyframes pulse {
    0%, 100% { opacity: 0.4; }
    50% { opacity: 1; }
}
.thinking-dot {
    animation: pulse 1.5s ease-in-out infinite;
}
.thinking-dot:nth-child(2) { animation-delay: 0.2s; }
.thinking-dot:nth-child(3) { animation-delay: 0.4s; }

/* 快捷按钮样式 */
.stButton > button:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    transition: all 0.2s ease;
}

/* 隐藏 Streamlit 默认元素 */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}

/* 消息时间戳 */
.msg-time {
    font-size: 0.75rem;
    color: #888;
    margin-top: 2px;
}

/* AI回复和用户输入的字体大小 */
.stChatMessage p,
.stChatMessage div,
.stChatMessage span {
    font-size: 1rem !important;
}
.stChatMessage pre,
.stChatMessage code {
    font-size: 0.9rem !important;
}

/* 对话历史卡片 */
.history-card {
    border: 1px solid #ddd;
    border-radius: 8px;
    padding: 10px;
    margin-bottom: 8px;
    cursor: pointer;
    transition: all 0.2s;
}
.history-card:hover {
    border-color: #4CAF50;
    background: #f0f7f0;
}

/* 思考过程面板 */
.tool-step-card {
    background: #f8f9ff;
    border: 1px solid #d0d7ff;
    border-left: 4px solid #6366f1;
    border-radius: 6px;
    padding: 10px 14px;
    margin: 6px 0;
    font-size: 0.88rem;
}
.tool-name {
    color: #6366f1;
    font-weight: 700;
    font-size: 0.92rem;
}
.tool-label {
    color: #666;
    font-size: 0.8rem;
    margin-top: 4px;
}
.tool-value {
    background: #eef0ff;
    border-radius: 4px;
    padding: 4px 8px;
    font-family: monospace;
    word-break: break-all;
    margin-top: 2px;
}
.tool-output-value {
    background: #e8f5e9;
    border-radius: 4px;
    padding: 4px 8px;
    font-family: monospace;
    word-break: break-all;
    margin-top: 2px;
    color: #2e7d32;
}
</style>
""", unsafe_allow_html=True)

# 页面配置
st.set_page_config(
    page_title="智能运维助手",
    page_icon="🤖",
    layout="centered",
    initial_sidebar_state="expanded"
)

# 后端 API 地址
API_BASE_URL = "http://localhost:8000"

# ──────────────────────────────────────────
# 会话状态初始化
# ──────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": (
                "你好！我是**智能运维助手**，基于 LangChain + 智谱AI GLM-4。\n\n"
                "我可以帮你：\n"
                "- 📊 查询 CPU / 内存使用率\n"
                "- 🔍 检查系统服务状态（nginx、mysql、redis）\n"
                "- 💿 查看磁盘使用情况\n"
                "- 🏥 分析系统整体健康状况\n"
                "- 💬 支持多轮对话，记住上下文\n\n"
                "请直接输入你的问题，或点击下方快捷按钮！"
            ),
            "time": datetime.now().strftime("%H:%M")
        }
    ]

# 每个浏览器会话生成唯一 thread_id
if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(uuid.uuid4())[:8]

# 后端会话列表缓存（从 GET /sessions 拉取）
if "session_list" not in st.session_state:
    st.session_state.session_list = []

# 后端连接状态缓存
if "backend_online" not in st.session_state:
    st.session_state.backend_online = None

# 当前提问提取到的指标数据（用于仪表盘显示，只保留当次结果）
if "current_metrics" not in st.session_state:
    st.session_state.current_metrics = None


# ──────────────────────────────────────────
# 渲染函数（需在页面渲染前定义）
# ──────────────────────────────────────────
COLLAPSE_THRESHOLD = 100  # AI 回复超过此字符数时放入可折叠区域


def render_ai_reply(content: str, collapsed: bool = False):
    """渲染 AI 回复内容，长文本可折叠"""
    if len(content) > COLLAPSE_THRESHOLD:
        preview = content.split("\n")[0][:40]
        if len(preview) < len(content.split("\n")[0]):
            preview += "…"
        label = f"💬 {preview}"
        with st.expander(label, expanded=not collapsed):
            st.markdown(content)
    else:
        st.markdown(content)


def render_thinking_steps(steps: list):
    """渲染可折叠的「思考过程」面板"""
    if not steps:
        return
    label = f"🧠 思考过程（调用了 {len(steps)} 个工具）"
    with st.expander(label, expanded=False):
        for idx, step in enumerate(steps, 1):
            tool_name = step.get("tool_name", "未知工具")
            tool_input = step.get("tool_input", {})
            tool_output = step.get("tool_output", "")
            if isinstance(tool_input, dict) and tool_input:
                input_str = json.dumps(tool_input, ensure_ascii=False, indent=None)
            elif tool_input:
                input_str = str(tool_input)
            else:
                input_str = "（无参数）"
            output_str = str(tool_output)
            if len(output_str) > 300:
                output_str = output_str[:300] + "…（已截断）"
            st.markdown(f"""
<div class="tool-step-card">
  <div class="tool-name">🔧 步骤 {idx}：{tool_name}</div>
  <div class="tool-label">📥 传入参数：</div>
  <div class="tool-value">{input_str}</div>
  <div class="tool-label">📤 返回结果：</div>
  <div class="tool-output-value">{output_str}</div>
</div>
""", unsafe_allow_html=True)


def check_backend_status(api_url):
    """检查后端是否在线"""
    try:
        r = requests.get(f"{api_url.rstrip('/')}/", timeout=3)
        return r.status_code == 200
    except Exception:
        return False


def load_sessions_from_backend():
    """从后端加载会话列表，写入 st.session_state.session_list"""
    try:
        r = requests.get(f"{API_BASE_URL.rstrip('/')}/sessions", timeout=5)
        if r.status_code == 200:
            st.session_state.session_list = r.json()
        else:
            st.session_state.session_list = []
    except Exception:
        st.session_state.session_list = []


def load_session_messages(session_id):
    """从后端加载指定会话的消息列表"""
    try:
        r = requests.get(f"{API_BASE_URL.rstrip('/')}/sessions/{session_id}", timeout=5)
        if r.status_code == 200:
            data = r.json()
            return data.get("messages", [])
    except Exception:
        pass
    return None


def save_messages_to_backend(session_id, messages):
    """将消息列表保存到后端（覆盖式）"""
    try:
        payload = []
        for m in messages:
            item = {"role": m["role"], "content": m["content"], "timestamp": m.get("time", "")}
            if m.get("steps"):
                item["steps"] = m["steps"]
            payload.append(item)
        r = requests.post(
            f"{API_BASE_URL.rstrip('/')}/sessions/{session_id}/messages",
            json=payload,
            timeout=5
        )
        return r.status_code == 200
    except Exception:
        return False


def delete_session_on_backend(session_id):
    """在后端删除指定会话"""
    try:
        r = requests.delete(f"{API_BASE_URL.rstrip('/')}/sessions/{session_id}", timeout=5)
        return r.status_code == 200
    except Exception:
        return False


def rename_session_on_backend(session_id, name):
    """在后端重命名会话"""
    try:
        r = requests.put(
            f"{API_BASE_URL.rstrip('/')}/sessions/{session_id}",
            json={"name": name},
            timeout=5
        )
        return r.status_code == 200
    except Exception:
        return False


# ──────────────────────────────────────────
# 可视化功能函数（v2.4 新增）
# ──────────────────────────────────────────

def extract_metrics_from_text(text: str, question: str = ""):
    """
    从 AI 回复文字中提取 CPU / 内存 / 磁盘使用率（支持小数，如 7.5%）
    同时参考提问内容（question）来辅助判断哪个百分比对应哪个指标。
    """
    result = {"cpu": None, "memory": None, "disk": None}

    # 通用：从文本中提取所有百分比数字（支持小数），并记录每个数字前的文字
    # 用更宽松的正则，匹配各种格式：45%、45.5%、使用率45%、45%（磁盘）等
    all_percents = re.findall(r"(\d{1,3}(?:\.\d+)?)\s*%", text)

    # 模式1：指标名在前，如 "CPU使用率 45%" 或 "内存：7.5%"
    cpu_match = re.search(r"CPU[^\d]*?(\d{1,3}(?:\.\d+)?)\s*%", text, re.IGNORECASE)
    mem_match = re.search(r"内存[^\d]*?(\d{1,3}(?:\.\d+)?)\s*%", text, re.IGNORECASE)
    disk_match = re.search(r"磁盘[^\d]*?(\d{1,3}(?:\.\d+)?)\s*%", text, re.IGNORECASE)

    # 模式2：百分比在后，如 "使用率 45%（CPU）"
    if not cpu_match:
        cpu_match = re.search(r"(\d{1,3}(?:\.\d+)?)\s*%[^\n]{0,30}(?:CPU|处理器)", text, re.IGNORECASE)
    if not mem_match:
        mem_match = re.search(r"(\d{1,3}(?:\.\d+)?)\s*%[^\n]{0,30}(?:内存|Memory|RAM)", text, re.IGNORECASE)
    if not disk_match:
        disk_match = re.search(r"(\d{1,3}(?:\.\d+)?)\s*%[^\n]{0,30}(?:磁盘|Disk)", text, re.IGNORECASE)

    # 模式3：更宽松 — "使用率：45%" / "当前 45%" 等，结合提问推断
    if not cpu_match and question:
        q = question.lower()
        if any(w in q for w in ["cpu", "处理器", "processor"]):
            # 找文本中第一个百分比
            if all_percents:
                cpu_match = re.search(r"(\d{1,3}(?:\.\d+)?)\s*%", text)
    if not mem_match and question:
        q = question.lower()
        if any(w in q for w in ["内存", "memory", "ram"]):
            if all_percents:
                mem_match = re.search(r"(\d{1,3}(?:\.\d+)?)\s*%", text)
    if not disk_match and question:
        q = question.lower()
        if any(w in q for w in ["磁盘", "disk", "硬盘"]):
            if all_percents:
                disk_match = re.search(r"(\d{1,3}(?:\.\d+)?)\s*%", text)

    if cpu_match:
        result["cpu"] = float(cpu_match.group(1))
    if mem_match:
        result["memory"] = float(mem_match.group(1))
    if disk_match:
        result["disk"] = float(disk_match.group(1))

    return result


def render_metrics_gauge(metrics: dict):
    """用 Plotly 仪表盘展示 CPU / 内存 / 磁盘使用率"""
    cols = st.columns(3)
    labels = ["CPU", "内存", "磁盘"]
    keys = ["cpu", "memory", "disk"]
    colors = {"safe": "#00CC96", "warn": "#FFA500", "danger": "#EF553B"}

    for i, (label, key) in enumerate(zip(labels, keys)):
        val = metrics.get(key)
        with cols[i]:
            if val is not None:
                # 根据数值决定颜色
                if val < 70:
                    bar_color = colors["safe"]
                    status = "正常"
                elif val < 90:
                    bar_color = colors["warn"]
                    status = "偏高"
                else:
                    bar_color = colors["danger"]
                    status = "告警"
                fig = go.Figure(go.Indicator(
                    mode="gauge+number+delta",
                    value=val,
                    domain={"x": [0, 1], "y": [0, 1]},
                    title={"text": f"{label} 使用率", "font": {"size": 16}},
                    delta={"reference": 80, "position": "top"},
                    gauge={
                        "axis": {"range": [None, 100], "tickwidth": 1},
                        "bar": {"color": bar_color},
                        "steps": [
                            {"range": [0, 70], "color": "lightgray"},
                            {"range": [70, 90], "color": "orange"},
                            {"range": [90, 100], "color": "red"}
                        ],
                        "threshold": {
                            "line": {"color": "red", "width": 4},
                            "thickness": 0.75,
                            "value": 90
                        }
                    }
                ))
                fig.update_layout(
                    height=220,
                    margin={"t": 40, "b": 10, "l": 20, "r": 20},
                    font={"family": "微软雅黑"}
                )
                st.plotly_chart(fig, use_container_width=True)
                if status == "告警":
                    st.error(f"⚠️ {label} 使用率 {val}%！")
                elif status == "偏高":
                    st.warning(f"⚡ {label} 使用率 {val}%，偏高")
                else:
                    st.success(f"✅ {label} 使用率正常 ({val}%)")
            else:
                st.info(f"📊 {label}：暂无数据")


def check_service_status():
    """调用后端工具检查各服务运行状态，返回 {服务名: (状态布尔, 详情字符串)}"""
    results = {}
    services = ["nginx", "mysql", "redis"]
    for svc in services:
        try:
            r = requests.post(
                f"{API_BASE_URL.rstrip('/')}/chat",
                json={"text": f"{svc}是否在运行？", "thread_id": "health-check", "show_init_info": False},
                timeout=10
            )
            if r.status_code == 200:
                answer = r.json().get("response", "")
                # 简单判断：回答中包含"运行"且不包含"未"/"不运行"则为运行中
                is_running = "运行" in answer and not any(w in answer for w in ["未运行", "不运行", "没有运行"])
                results[svc] = (is_running, answer[:80])
            else:
                results[svc] = (False, f"查询失败({r.status_code})")
        except Exception as e:
            results[svc] = (False, f"请求失败：{e}")
    return results


def render_service_dashboard():
    """渲染服务状态 Dashboard（侧边栏或主界面均可调用）"""
    st.subheader("🖥️ 服务状态")
    results = check_service_status()
    for svc, (is_up, detail) in results.items():
        col1, col2 = st.columns([1, 4])
        with col1:
            st.markdown(f"### {'🟢' if is_up else '🔴'}")
        with col2:
            st.markdown(f"**{svc.upper()}**")
            st.caption(detail if not is_up else "运行中")
    st.caption("💡 提示：点击「刷新状态」更新")


def render_conversation_analysis():
    """渲染对话分析面板（侧边栏）"""
    st.subheader("📈 对话分析")
    messages = st.session_state.get("messages", [])
    user_msgs = [m for m in messages if m["role"] == "user"]
    ai_msgs = [m for m in messages if m["role"] == "assistant"]
    total_steps = sum(len(m.get("steps", [])) for m in messages if m.get("steps"))

    col1, col2 = st.columns(2)
    with col1:
        st.metric("用户消息", len(user_msgs))
    with col2:
        st.metric("AI 回复", len(ai_msgs))

    st.metric("工具调用次数", total_steps)

    # 常用工具 Top 统计
    if total_steps > 0:
        tool_counter = {}
        for m in messages:
            for step in m.get("steps", []):
                name = step.get("tool_name", "未知")
                tool_counter[name] = tool_counter.get(name, 0) + 1
        sorted_tools = sorted(tool_counter.items(), key=lambda x: x[1], reverse=True)[:3]
        st.caption("🔧 常用工具 Top3：")
        for name, cnt in sorted_tools:
            st.caption(f"  • {name}（{cnt}次）")

    # 平均响应时间（如果有）
    times = []
    for m in ai_msgs:
        try:
            t = m.get("time", "")
            if t:
                times.append(t)
        except Exception:
            pass
    if len(user_msgs) > 0:
        st.caption(f"💬 对话轮次：{len(user_msgs)} 轮")


# 页面加载时自动检查后端状态 + 加载会话列表
if st.session_state.backend_online is None:
    with st.spinner("正在连接后端服务..."):
        st.session_state.backend_online = check_backend_status(API_BASE_URL)
        if st.session_state.backend_online:
            load_sessions_from_backend()


# ──────────────────────────────────────────
# 侧边栏
# ──────────────────────────────────────────
with st.sidebar:
    # API地址配置
    st.header("⚙️ 配置")
    api_base = st.text_input(
        "后端地址",
        value=API_BASE_URL,
        help="FastAPI 服务地址，默认 http://localhost:8000"
    )

    st.divider()

    # 后端连接状态指示器
    if st.session_state.backend_online:
        st.success("🟢 后端已连接")
    else:
        st.error("🔴 后端未连接")
        st.caption("请先启动后端服务")
        st.code("cd backend && python main.py")

    st.divider()

    # 会话管理
    st.header("💬 会话管理")
    st.caption(f"当前会话：`{st.session_state.thread_id}`")

    # 刷新会话列表
    if st.button("🔄 刷新列表", type="secondary", use_container_width=True):
        with st.spinner("加载中..."):
            load_sessions_from_backend()
        st.rerun()

    # 新建会话（调后端 API）
    if st.button("✨ 新建会话", type="primary", use_container_width=True):
        try:
            r = requests.post(
                f"{API_BASE_URL.rstrip('/')}/sessions",
                json={},
                timeout=5
            )
            if r.status_code == 200:
                data = r.json()
                st.session_state.thread_id = data["id"]
                st.session_state.messages = [
                    {
                        "role": "assistant",
                        "content": "已开始新会话，上下文已重置。有什么我可以帮你的？",
                        "time": datetime.now().strftime("%H:%M")
                    }
                ]
                load_sessions_from_backend()
                st.rerun()
            else:
                st.error("新建会话失败")
        except Exception as e:
            st.error(f"新建会话失败：{e}")

    st.divider()

    # 会话列表（从后端拉取）
    st.header("📜 会话列表")
    if st.session_state.session_list:
        for sess in st.session_state.session_list:
            sid = sess["id"]
            sname = sess.get("name", "新会话")
            updated = sess.get("updated_at", "")

            col1, col2 = st.columns([5, 1])
            with col1:
                if st.button(
                    f"💬 {sname}",
                    key=f"switch_{sid}",
                    use_container_width=True,
                    help=f"最后更新：{updated}"
                ):
                    msgs = load_session_messages(sid)
                    if msgs is not None:
                        st.session_state.thread_id = sid
                        st.session_state.messages = msgs
                        st.rerun()
                    else:
                        st.error("加载会话失败")

            with col2:
                if st.button("🗑️", key=f"del_{sid}", help="删除此会话"):
                    if delete_session_on_backend(sid):
                        if st.session_state.thread_id == sid:
                            st.session_state.thread_id = str(uuid.uuid4())[:8]
                            st.session_state.messages = [
                                {
                                    "role": "assistant",
                                    "content": "会话已删除，已开始新会话。",
                                    "time": datetime.now().strftime("%H:%M")
                                }
                            ]
                        load_sessions_from_backend()
                        st.rerun()
                    else:
                        st.error("删除失败")
    else:
        st.caption("暂无会话，点击「新建会话」开始")

    st.divider()

    # 系统监控（服务状态 Dashboard，默认折叠）
    with st.expander("🖥️ 服务状态", expanded=False):
        if st.button("🔍 检查服务", type="secondary", use_container_width=True, key="check_svc"):
            with st.spinner("检查中..."):
                results = check_service_status()
                for svc, (is_up, detail) in results.items():
                    if is_up:
                        st.success(f"🟢 {svc.upper()}：运行中")
                    else:
                        st.error(f"🔴 {svc.upper()}：{detail[:50]}")
        st.caption("💡 点击按钮检查 nginx / mysql / redis")

    st.divider()

    # 对话分析面板（默认折叠）
    with st.expander("📈 对话分析", expanded=False):
        render_conversation_analysis()

    st.divider()

    # 智能体信息
    st.header("🤖 智能体信息")
    if st.button("📋 查看工具", type="secondary", use_container_width=True):
        try:
            r = requests.get(f"{api_base}/info", timeout=5)
            if r.status_code == 200:
                info = r.json()
                st.info(f"类型：{info.get('agent_type', '未知')}")
                st.info(f"工具数量：{info.get('tools_count', 0)}")
                for tool_name in info.get("tool_names", []):
                    st.caption(f"  • {tool_name}")
            else:
                st.warning("获取失败")
        except Exception as e:
            st.error(f"请求失败：{e}")


# ──────────────────────────────────────────
# 主界面标题
# ──────────────────────────────────────────
st.title("🤖 智能运维助手")
st.caption(f"会话 `{st.session_state.thread_id}` | LangChain + 智谱AI GLM-4 | v2.4")

# ──────────────────────────────────────────
# 显示聊天消息（带时间戳）
# Streamlit 默认：user 在右，assistant 在左
# ──────────────────────────────────────────
for i, message in enumerate(st.session_state.messages):
    is_latest = (i == len(st.session_state.messages) - 1)
    with st.chat_message(message["role"]):
        if message["role"] == "assistant":
            # AI 回复：长文本可折叠（历史消息默认折叠，最新消息直接显示）
            is_history = not is_latest
            render_ai_reply(message["content"], collapsed=is_history)
        else:
            st.markdown(message["content"])
        # 显示时间戳
        if "time" in message:
            st.caption(f"🕐 {message['time']}")
        # 历史消息中也展示思考过程（如有）
        if message["role"] == "assistant" and message.get("steps"):
            render_thinking_steps(message["steps"])



# ──────────────────────────────────────────
# 发送消息并获取回复（含加载动画 + 错误处理）
# ──────────────────────────────────────────

def send_and_get_response(prompt_text):
    """发送消息给后端并获取回复"""
    # 重置仪表盘指标（只显示当前提问相关的指标）
    st.session_state.current_metrics = None
    now = datetime.now().strftime("%H:%M")

    # 显示用户消息
    with st.chat_message("user"):
        st.markdown(prompt_text)
        st.caption(f"🕐 {now}")
    st.session_state.messages.append({"role": "user", "content": prompt_text, "time": now})

    # 自动重命名：用第一条用户消息作为会话名（发消息后立即执行）
    current_sess = next(
        (s for s in st.session_state.session_list if s["id"] == st.session_state.thread_id),
        None
    )
    if current_sess and current_sess.get("name", "") in ("新会话", "", None):
        first_user_msg = next(
            (m["content"] for m in st.session_state.messages if m["role"] == "user"),
            None
        )
        if first_user_msg:
            new_name = first_user_msg[:20] + ("..." if len(first_user_msg) > 20 else "")
            if rename_session_on_backend(st.session_state.thread_id, new_name):
                load_sessions_from_backend()

    # 调用后端 API
    with st.chat_message("assistant"):
        message_placeholder = st.empty()

        # 加载动画：三点跳动的思考中提示
        dots_html = """
        <div style="padding: 8px 0;">
            <span style="font-size: 1.1rem;">🤔 思考中</span>
            <span class="thinking-dot" style="font-size: 1.2rem;">●</span>
            <span class="thinking-dot" style="font-size: 1.2rem;">●</span>
            <span class="thinking-dot" style="font-size: 1.2rem;">●</span>
        </div>
        """
        message_placeholder.markdown(dots_html, unsafe_allow_html=True)

        try:
            response = requests.post(
                f"{api_base}/chat",
                json={
                    "text": prompt_text,
                    "thread_id": st.session_state.thread_id,
                    "show_init_info": False
                },
                timeout=60
            )

            if response.status_code == 200:
                data = response.json()
                answer = data.get("response", "未收到有效回答")
                proc_time = data.get("processing_time", 0)
                agent_type = data.get("agent_type", "")
                # 新后端（DeepAgents）会返回 thread_id，用于多轮对话
                backend_thread_id = data.get("thread_id", "")
                if backend_thread_id:
                    st.session_state.thread_id = backend_thread_id

                # 打字效果（先在 placeholder 里滚动显示）
                full_response = ""
                for word in answer.split():
                    full_response += word + " "
                    message_placeholder.markdown(full_response + "▌")
                    time.sleep(0.03)

                # 打字完成：清掉 placeholder，用 render_ai_reply 正式渲染（默认展开）
                message_placeholder.empty()
                render_ai_reply(full_response.strip(), collapsed=False)
                reply_time = datetime.now().strftime("%H:%M")
                st.caption(f"🕐 {reply_time} | ⏱ {proc_time:.2f}s | {agent_type}")

                # 尝试从 AI 回复中提取系统指标，供仪表盘使用
                # 传入提问内容作为上下文，帮助判断哪个百分比对应哪个指标
                extracted = extract_metrics_from_text(full_response, question=prompt_text)
                if any(v is not None for v in extracted.values()):
                    st.session_state.current_metrics = extracted

                # ✅ 在 AI 回复下方立即显示仪表盘（仅当次提问涉及 CPU/内存/磁盘时显示）
                current_metrics = st.session_state.get("current_metrics", None)
                if current_metrics and any(v is not None for v in current_metrics.values()):
                    st.write("---")
                    st.subheader("📊 系统指标仪表盘")
                    render_metrics_gauge(current_metrics)

                st.session_state.messages.append({
                    "role": "assistant",
                    "content": full_response.strip(),
                    "time": reply_time,
                })
                # 立即将当前会话保存到后端
                save_messages_to_backend(st.session_state.thread_id, st.session_state.messages)

            elif response.status_code == 503:
                msg = "⚠️ **智能体未就绪**\n\n后端服务已启动，但AI智能体初始化失败。\n\n可能原因：\n- API Key 无效或过期\n- 网络无法访问智谱AI\n\n请检查 `.env` 文件中的配置。"
                message_placeholder.markdown(msg)
                st.session_state.messages.append({"role": "assistant", "content": msg, "time": datetime.now().strftime("%H:%M")})

            elif response.status_code == 400:
                msg = "⚠️ **请求无效**\n\n问题内容为空，请输入有效的问题。"
                message_placeholder.markdown(msg)
                st.session_state.messages.append({"role": "assistant", "content": msg, "time": datetime.now().strftime("%H:%M")})

            elif response.status_code == 500:
                error_detail = ""
                try:
                    error_detail = response.json().get("detail", "")
                except Exception:
                    pass
                msg = f"❌ **服务器内部错误**\n\n{error_detail if error_detail else '后端处理请求时发生错误，请查看后端日志。'}"
                message_placeholder.markdown(msg)
                st.session_state.messages.append({"role": "assistant", "content": msg, "time": datetime.now().strftime("%H:%M")})

            else:
                error_detail = ""
                try:
                    error_detail = response.json().get("detail", "")
                except Exception:
                    pass
                msg = f"❌ **请求失败** ({response.status_code})\n\n{error_detail}"
                message_placeholder.markdown(msg)
                st.session_state.messages.append({"role": "assistant", "content": msg, "time": datetime.now().strftime("%H:%M")})

        except requests.exceptions.ConnectionError:
            st.session_state.backend_online = False
            msg = (
                "❌ **无法连接到后端服务**\n\n"
                "请按以下步骤启动后端：\n"
                "```\n"
                "cd E:\\smart-ops-frontend\n"
                "venv\\Scripts\\python.exe backend\\main.py\n"
                "```\n\n"
                "看到 `API服务: http://localhost:8000` 即为成功。"
            )
            message_placeholder.markdown(msg)
            st.session_state.messages.append({"role": "assistant", "content": msg, "time": datetime.now().strftime("%H:%M")})

        except requests.exceptions.Timeout:
            msg = "⏰ **请求超时**（超过60秒）\n\n可能原因：\n- AI模型响应过慢\n- 网络不稳定\n\n请稍后重试，或尝试简化问题。"
            message_placeholder.markdown(msg)
            st.session_state.messages.append({"role": "assistant", "content": msg, "time": datetime.now().strftime("%H:%M")})

        except requests.exceptions.JSONDecodeError:
            msg = "❌ **响应解析失败**\n\n后端返回了无效的数据格式，请检查后端服务是否正常运行。"
            message_placeholder.markdown(msg)
            st.session_state.messages.append({"role": "assistant", "content": msg, "time": datetime.now().strftime("%H:%M")})

        except Exception as e:
            msg = f"❌ **未知错误**\n\n`{type(e).__name__}: {e}`\n\n如果问题持续出现，请检查后端日志。"
            message_placeholder.markdown(msg)
            st.session_state.messages.append({"role": "assistant", "content": msg, "time": datetime.now().strftime("%H:%M")})








# 处理快捷按钮触发（在按钮渲染之前执行，确保同一次运行中处理）
if "quick_prompt" in st.session_state:
    _prompt = st.session_state.quick_prompt
    del st.session_state.quick_prompt
    send_and_get_response(_prompt)

# 聊天输入框（Streamlit 固定在最底部）
if prompt := st.chat_input("请输入你的问题，例如：CPU使用率怎么样？"):
    send_and_get_response(prompt)

# ──────────────────────────────────────────
# 底部：分割线 → 快捷提问 → 版本信息
# ──────────────────────────────────────────
st.divider()

# 快捷提问（在分割线下面，版本信息上面）
def on_quick_click(question):
    st.session_state.quick_prompt = question

with st.expander("💡 快捷提问", expanded=False):
    all_buttons = [
        ("📊 CPU", "CPU使用率怎么样？"),
        ("💾 内存", "内存使用情况如何？"),
        ("💿 磁盘", "磁盘使用情况怎么样？"),
        ("💿 IO", "磁盘IO情况如何？"),
        ("🔧 nginx", "nginx是否在运行？"),
        ("🔧 mysql", "mysql是否在运行？"),
        ("🔧 redis", "redis是否在运行？"),
        ("🔬 服务诊断", "诊断nginx服务故障"),
        ("🔝 进程", "查看占用CPU最高的进程"),
        ("🌐 网络", "检查网络连接状态"),
        ("🌐 摘要", "查看网络摘要"),
        ("🔌 端口", "检查端口 8080 是否开放"),
        ("📋 日志", "查询系统错误日志"),
        ("🔬 CPU诊断", "诊断CPU高使用率原因"),
        ("🔬 内存诊断", "诊断内存高使用率原因"),
    ]
    # 每行4个按钮
    for row_start in range(0, len(all_buttons), 4):
        cols = st.columns(4)
        row_buttons = all_buttons[row_start:row_start + 4]
        for j, (label, question) in enumerate(row_buttons):
            with cols[j]:
                st.button(label, use_container_width=True, key=f"q_{row_start + j}",
                          on_click=on_quick_click, args=(question,))

# 版本信息（最底部）
col1, col2 = st.columns([3, 1])
with col1:
    st.caption("**智能运维助手** v2.4 | 可视化面板 | LangChain + 智谱AI GLM-4")
with col2:
    if st.button("🗑️ 清空当前聊天", type="secondary", use_container_width=True):
        # 同步清空后端消息
        try:
            requests.post(
                f"{API_BASE_URL.rstrip('/')}/sessions/{st.session_state.thread_id}/messages",
                json=[],
                timeout=5
            )
        except Exception:
            pass
        st.session_state.messages = [
            {
                "role": "assistant",
                "content": "聊天已清空。有什么我可以帮你的？",
                "time": datetime.now().strftime("%H:%M")
            }
        ]
        st.rerun()


