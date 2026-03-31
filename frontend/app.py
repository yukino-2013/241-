"""
智能运维助手 - 前端聊天界面
角色B产出文件：frontend/app.py
"""

import streamlit as st
import requests
import os

# ============================================
# 配置区域
# ============================================

# 后端 API 地址（A 的 FastAPI 服务地址）
API_URL = os.getenv("API_URL", "http://localhost:8000/chat")

# 是否使用模拟模式（后端未就绪时设为 True）
# 等A完成后端后，改为 False 即可切换到真实API
USE_MOCK = os.getenv("USE_MOCK", "true").lower() == "true"

# 模拟数据（后端未就绪时使用）
MOCK_RESPONSES = {
    "cpu": "📊 **CPU 使用率查询结果**\n\n- 使用率：**32.5%**\n- 核心数：8 核\n- 系统负载：1.2 / 8.0\n\n✅ 系统运行正常，CPU 负载较低。",
    "内存": "💾 **内存使用情况**\n\n- 已用：**6.2 GB** / 16 GB（38.7%）\n- 可用：9.8 GB\n- 缓存：2.1 GB\n\n✅ 内存使用健康。",
    "memory": "💾 **内存使用情况**\n\n- 已用：**6.2 GB** / 16 GB（38.7%）\n- 可用：9.8 GB\n- 缓存：2.1 GB\n\n✅ 内存使用健康。",
    "nginx": "🔧 **服务状态检查 - nginx**\n\n- 状态：✅ **运行中**\n- PID：1234\n- 运行时长：5天3小时12分钟\n- 端口：80, 443\n\n✅ nginx 服务正常运行。",
    "mysql": "🔧 **服务状态检查 - MySQL**\n\n- 状态：✅ **运行中**\n- PID：2048\n- 运行时长：12天6小时45分钟\n- 端口：3306\n- 版本：MySQL 8.0.35\n\n✅ MySQL 服务正常运行。",
    "redis": "🔧 **服务状态检查 - Redis**\n\n- 状态：✅ **运行中**\n- PID：3056\n- 运行时长：3天18小时\n- 端口：6379\n- 版本：Redis 7.2.3\n\n✅ Redis 服务正常运行。",
    "磁盘": "💿 **磁盘使用情况**\n\n| 分区 | 总容量 | 已用 | 可用 | 使用率 |\n|------|--------|------|------|--------|\n| C: | 256 GB | 120 GB | 136 GB | 46.9% |\n| D: | 512 GB | 280 GB | 232 GB | 54.7% |\n\n✅ 磁盘空间充足。",
    "disk": "💿 **磁盘使用情况**\n\n| 分区 | 总容量 | 已用 | 可用 | 使用率 |\n|------|--------|------|------|--------|\n| C: | 256 GB | 120 GB | 136 GB | 46.9% |\n| D: | 512 GB | 280 GB | 232 GB | 54.7% |\n\n✅ 磁盘空间充足。",
    "负载": "📈 **系统负载**\n\n- 1分钟平均负载：**0.85**\n- 5分钟平均负载：**1.12**\n- 15分钟平均负载：**0.96**\n- CPU核心数：8\n\n✅ 负载水平正常。",
    "服务": "🔧 **服务状态检查**\n\n请告诉我您想检查哪个服务的状态，例如：\n- `nginx 是否在运行`\n- `检查 mysql 状态`\n- `redis 服务怎么样`",
}

MOCK_FALLBACK = """🤖 我可以帮你查询以下服务器信息：

1. **CPU 使用率** — 输入「CPU怎么样」
2. **内存使用情况** — 输入「内存使用情况如何」
3. **服务运行状态** — 输入「nginx是否在运行」

> 💡 当前为模拟模式，等后端服务就绪后将提供真实数据。"""


# ============================================
# 页面配置
# ============================================

st.set_page_config(
    page_title="智能运维助手",
    page_icon="🤖",
    layout="centered",
)

st.title("🤖 智能运维助手")
st.caption("通过自然语言对话查询服务器状态（CPU、内存、服务运行情况）")

# 显示当前模式
mode_label = "🔴 模拟模式" if USE_MOCK else "🟢 真实模式"
st.info(f"当前运行模式：**{mode_label}** | API地址：`{API_URL}`")


# ============================================
# 模拟回复函数
# ============================================

def get_mock_response(prompt: str) -> str:
    """根据用户输入返回模拟数据"""
    prompt_lower = prompt.lower()
    for keyword, response in MOCK_RESPONSES.items():
        if keyword in prompt_lower:
            return response
    return MOCK_FALLBACK


# ============================================
# 调用后端 API
# ============================================

def call_backend_api(prompt: str) -> str:
    """调用后端 FastAPI 接口"""
    try:
        response = requests.post(
            API_URL,
            json={"text": prompt},
            timeout=15,
        )
        response.raise_for_status()
        data = response.json()
        # 兼容不同的返回格式
        if isinstance(data, dict):
            return data.get("answer", data.get("response", str(data)))
        return str(data)
    except requests.exceptions.ConnectionError:
        return "❌ **无法连接到后端服务**\n\n请确认后端服务已启动：\n```bash\ncd backend\npython main.py\n```\n\n或等待角色A完成后端开发。"
    except requests.exceptions.Timeout:
        return "⏰ **请求超时**\n\n后端服务响应时间过长，请稍后重试。"
    except requests.exceptions.HTTPError as e:
        return f"❌ **服务端错误** (HTTP {e.response.status_code})\n\n{e.response.text[:200]}"
    except Exception as e:
        return f"❌ **发生未知错误**\n\n`{type(e).__name__}: {str(e)}`"


# ============================================
# 获取回复（根据模式选择模拟/API）
# ============================================

def get_response(prompt: str) -> str:
    """根据当前模式获取回复"""
    if USE_MOCK:
        return get_mock_response(prompt)
    return call_backend_api(prompt)


# ============================================
# 初始化聊天历史
# ============================================

if "messages" not in st.session_state:
    st.session_state.messages = []

# 清除历史按钮
col1, col2 = st.columns([6, 1])
with col2:
    if st.button("🗑️ 清除对话", use_container_width=True):
        st.session_state.messages = []
        st.rerun()


# ============================================
# 显示历史消息
# ============================================

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])


# ============================================
# 快捷提问按钮
# ============================================

st.write("---")
st.write("**💡 快捷提问：**")

col1, col2, col3, col4 = st.columns(4)
with col1:
    if st.button("📊 CPU", use_container_width=True, key="q1"):
        prompt = "CPU使用率怎么样？"
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        with st.spinner("🤖 智能体思考中..."):
            answer = get_response(prompt)
        with st.chat_message("assistant"):
            st.markdown(answer)
        st.session_state.messages.append({"role": "assistant", "content": answer})

with col2:
    if st.button("💾 内存", use_container_width=True, key="q2"):
        prompt = "内存使用情况如何？"
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        with st.spinner("🤖 智能体思考中..."):
            answer = get_response(prompt)
        with st.chat_message("assistant"):
            st.markdown(answer)
        st.session_state.messages.append({"role": "assistant", "content": answer})

with col3:
    if st.button("💿 磁盘", use_container_width=True, key="q4"):
        prompt = "磁盘使用情况怎么样？"
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        with st.spinner("🤖 智能体思考中..."):
            answer = get_response(prompt)
        with st.chat_message("assistant"):
            st.markdown(answer)
        st.session_state.messages.append({"role": "assistant", "content": answer})

with col4:
    if st.button("📈 负载", use_container_width=True, key="q5"):
        prompt = "系统负载如何？"
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        with st.spinner("🤖 智能体思考中..."):
            answer = get_response(prompt)
        with st.chat_message("assistant"):
            st.markdown(answer)
        st.session_state.messages.append({"role": "assistant", "content": answer})

col5, col6, col7 = st.columns(3)
with col5:
    if st.button("🔧 nginx", use_container_width=True, key="q3"):
        prompt = "nginx是否在运行？"
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        with st.spinner("🤖 智能体思考中..."):
            answer = get_response(prompt)
        with st.chat_message("assistant"):
            st.markdown(answer)
        st.session_state.messages.append({"role": "assistant", "content": answer})

with col6:
    if st.button("🔧 mysql", use_container_width=True, key="q6"):
        prompt = "mysql是否在运行？"
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        with st.spinner("🤖 智能体思考中..."):
            answer = get_response(prompt)
        with st.chat_message("assistant"):
            st.markdown(answer)
        st.session_state.messages.append({"role": "assistant", "content": answer})

with col7:
    if st.button("🔧 redis", use_container_width=True, key="q7"):
        prompt = "redis是否在运行？"
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        with st.spinner("🤖 智能体思考中..."):
            answer = get_response(prompt)
        with st.chat_message("assistant"):
            st.markdown(answer)
        st.session_state.messages.append({"role": "assistant", "content": answer})

st.write("---")


# ============================================
# 聊天输入框
# ============================================

if prompt := st.chat_input("请输入你的问题（如：CPU怎么样？内存使用情况如何？nginx是否在运行？）"):
    # 显示用户消息
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # 调用并显示AI回复
    with st.spinner("🤖 智能体思考中..."):
        answer = get_response(prompt)

    with st.chat_message("assistant"):
        st.markdown(answer)
    st.session_state.messages.append({"role": "assistant", "content": answer})


# ============================================
# 页脚
# ============================================

st.divider()
st.caption("智能运维助手 v1.0 | 角色：B（前端界面）| 技术栈：Streamlit + Python")
