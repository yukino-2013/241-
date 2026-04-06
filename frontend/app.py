#!/usr/bin/env python3
"""
智能运维助手 - Streamlit 前端界面 v2.1
提供聊天对话界面，调用后端 LangChain 智能体 API
功能：对话 + 快捷按钮 + 侧边栏 + 多轮记忆 + 打字效果 + 加载动画 + 错误处理 + 对话历史
"""

import uuid
import time
import json
from datetime import datetime
import streamlit as st
import requests

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

# 对话历史记录（所有会话）
if "chat_history" not in st.session_state:
    st.session_state.chat_history = {}

# 后端连接状态缓存
if "backend_online" not in st.session_state:
    st.session_state.backend_online = None


def check_backend_status(api_url):
    """检查后端是否在线"""
    try:
        r = requests.get(f"{api_url.rstrip('/')}/", timeout=3)
        return r.status_code == 200
    except Exception:
        return False


def save_to_history(thread_id, messages):
    """保存当前会话到历史记录"""
    if len(messages) > 1:  # 排除只有欢迎语的情况
        st.session_state.chat_history[thread_id] = {
            "messages": messages.copy(),
            "last_time": datetime.now().strftime("%m-%d %H:%M"),
            "msg_count": len(messages)
        }


def get_history_preview(messages, max_len=30):
    """获取对话历史的预览文本"""
    for msg in reversed(messages):
        if msg["role"] == "user":
            text = msg["content"].replace("\n", " ")
            return text[:max_len] + "..." if len(text) > max_len else text
    return "新会话"


# 页面加载时自动检查后端状态
if st.session_state.backend_online is None:
    with st.spinner("正在连接后端服务..."):
        st.session_state.backend_online = check_backend_status(API_BASE_URL)


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

    if st.button("🔄 新建会话", type="secondary", use_container_width=True):
        # 保存当前会话
        save_to_history(st.session_state.thread_id, st.session_state.messages)
        # 新建会话
        st.session_state.thread_id = str(uuid.uuid4())[:8]
        st.session_state.messages = [
            {
                "role": "assistant",
                "content": "已开始新会话，上下文已重置。有什么我可以帮你的？",
                "time": datetime.now().strftime("%H:%M")
            }
        ]
        st.rerun()

    st.divider()

    # 对话历史列表
    st.header("📜 对话历史")
    if st.session_state.chat_history:
        # 按最后活跃时间排序
        sorted_history = sorted(
            st.session_state.chat_history.items(),
            key=lambda x: x[1].get("last_time", ""),
            reverse=True
        )
        for tid, info in sorted_history:
            preview = get_history_preview(info["messages"])
            col1, col2 = st.columns([5, 1])
            with col1:
                if st.button(
                    f"💬 {preview}",
                    key=f"hist_{tid}",
                    use_container_width=True,
                    help=f"会话 {tid} | {info.get('last_time', '')} | {info.get('msg_count', 0)}条消息"
                ):
                    # 保存当前会话
                    save_to_history(st.session_state.thread_id, st.session_state.messages)
                    # 切换到选中的会话
                    st.session_state.thread_id = tid
                    st.session_state.messages = info["messages"]
                    st.rerun()
            with col2:
                if st.button("🗑️", key=f"del_{tid}", help="删除此会话"):
                    del st.session_state.chat_history[tid]
                    st.rerun()
    else:
        st.caption("暂无历史会话")

    if st.session_state.chat_history and st.button("🗑️ 清空所有历史", type="secondary", use_container_width=True):
        st.session_state.chat_history = {}
        st.rerun()

    st.divider()

    # 系统监控
    st.header("📊 系统监控")
    if st.button("🔍 刷新状态", type="secondary", use_container_width=True):
        try:
            r = requests.get(f"{api_base}/health", timeout=5)
            if r.status_code == 200:
                data = r.json()
                st.metric("CPU 使用率", f"{data.get('cpu_usage', '-')}%")
                st.metric("内存使用率", f"{data.get('memory_usage', '-')}%")
                health = data.get("overall_health", "未知")
                if health == "良好":
                    st.info(f"🏥 健康状态：{health}")
                else:
                    st.warning(f"⚠️ 健康状态：{health}")
            else:
                st.error(f"后端异常：{r.status_code}")
        except Exception as e:
            st.error(f"获取失败：{e}")

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
st.caption(f"会话 `{st.session_state.thread_id}` | LangChain + 智谱AI GLM-4")

# ──────────────────────────────────────────
# 显示聊天消息（带时间戳）
# ──────────────────────────────────────────
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        # 显示时间戳
        if "time" in message:
            st.caption(f"🕐 {message['time']}")

# ──────────────────────────────────────────
# 快捷提问按钮
# ──────────────────────────────────────────
st.write("---")
st.write("**💡 快捷提问：**")

quick_buttons = [
    ("📊 CPU", "CPU使用率怎么样？"),
    ("💾 内存", "内存使用情况如何？"),
    ("💿 磁盘", "磁盘使用情况怎么样？"),
    ("📈 负载", "系统负载如何？"),
    ("🔧 nginx", "nginx是否在运行？"),
    ("🔧 mysql", "mysql是否在运行？"),
    ("🔧 redis", "redis是否在运行？"),
]

cols = st.columns(4)
for i, (label, question) in enumerate(quick_buttons):
    with cols[i % 4]:
        if st.button(label, use_container_width=True, key=f"q{i}"):
            st.session_state.quick_prompt = question

st.write("---")

# ──────────────────────────────────────────
# 发送消息并获取回复（含加载动画 + 错误处理）
# ──────────────────────────────────────────

def send_and_get_response(prompt_text):
    """发送消息给后端并获取回复"""
    now = datetime.now().strftime("%H:%M")

    # 显示用户消息
    with st.chat_message("user"):
        st.markdown(prompt_text)
        st.caption(f"🕐 {now}")
    st.session_state.messages.append({"role": "user", "content": prompt_text, "time": now})

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

                # 打字效果
                full_response = ""
                for word in answer.split():
                    full_response += word + " "
                    message_placeholder.markdown(full_response + "▌")
                    time.sleep(0.03)

                message_placeholder.markdown(full_response.strip())
                reply_time = datetime.now().strftime("%H:%M")
                st.caption(f"🕐 {reply_time} | ⏱ {proc_time:.2f}s | {agent_type}")
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": full_response.strip(),
                    "time": reply_time
                })

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


# 处理快捷按钮触发
if "quick_prompt" in st.session_state:
    send_and_get_response(st.session_state.quick_prompt)
    del st.session_state.quick_prompt

# 聊天输入框
if prompt := st.chat_input("请输入你的问题，例如：CPU使用率怎么样？"):
    send_and_get_response(prompt)

# ──────────────────────────────────────────
# 底部
# ──────────────────────────────────────────
st.divider()
col1, col2, col3 = st.columns([2, 1, 1])
with col1:
    st.caption("**智能运维助手** v2.1 | LangChain ReAct + 智谱AI GLM-4")
with col2:
    if st.button("💾 保存会话", type="secondary", use_container_width=True):
        save_to_history(st.session_state.thread_id, st.session_state.messages)
        st.success(f"会话已保存！")
with col3:
    if st.button("🗑️ 清空聊天", type="secondary", use_container_width=True):
        st.session_state.messages = [
            {
                "role": "assistant",
                "content": "聊天已清空。有什么我可以帮你的？",
                "time": datetime.now().strftime("%H:%M")
            }
        ]
        st.rerun()
