#!/usr/bin/env python3
"""
智能运维助手 - Streamlit 前端界面
提供聊天对话界面，调用后端 LangChain 智能体 API
"""

import uuid
import streamlit as st
import requests
import time

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
                "- 🔍 检查系统服务状态\n"
                "- 🏥 分析系统整体健康状况\n"
                "- 💬 支持多轮对话，记住上下文\n\n"
                "请直接输入你的问题！"
            )
        }
    ]

# 每个浏览器会话生成唯一 thread_id，保证多轮记忆
if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(uuid.uuid4())[:8]

# ──────────────────────────────────────────
# 侧边栏
# ──────────────────────────────────────────
with st.sidebar:
    st.header("⚙️ 配置")

    api_base = st.text_input(
        "后端地址",
        value=API_BASE_URL,
        help="FastAPI 服务地址，默认 http://localhost:8000"
    )

    st.divider()

    # 会话 ID 显示与重置
    st.header("💬 会话管理")
    st.caption(f"当前会话 ID：`{st.session_state.thread_id}`")
    st.caption("同一会话 ID 内，智能体会记住上下文。")

    if st.button("新建会话（清除记忆）", type="secondary"):
        st.session_state.thread_id = str(uuid.uuid4())[:8]
        st.session_state.messages = [
            {
                "role": "assistant",
                "content": "已开始新会话，上下文已重置。有什么我可以帮你的？"
            }
        ]
        st.rerun()

    st.divider()

    # 后端状态检查
    st.header("📊 后端状态")
    if st.button("检查连接", type="secondary"):
        try:
            r = requests.get(f"{api_base}/health", timeout=5)
            if r.status_code == 200:
                data = r.json()
                st.success("后端连接正常")
                st.metric("CPU", f"{data.get('cpu_usage', '-')}%")
                st.metric("内存", f"{data.get('memory_usage', '-')}%")
                st.info(f"健康状态：{data.get('overall_health', '未知')}")
            else:
                st.error(f"后端异常：{r.status_code}")
        except requests.exceptions.ConnectionError:
            st.error("无法连接到后端服务")
            st.code("cd backend\npython main.py")
        except Exception as e:
            st.error(f"检查失败：{e}")

    st.divider()

    # 智能体信息
    st.header("🤖 智能体信息")
    if st.button("查看工具列表", type="secondary"):
        try:
            r = requests.get(f"{api_base}/info", timeout=5)
            if r.status_code == 200:
                info = r.json()
                st.info(f"类型：{info.get('agent_type', '未知')}")
                st.info(f"工具数量：{info.get('tools_count', 0)}")
                for tool_name in info.get("tool_names", []):
                    st.caption(f"  • {tool_name}")
            else:
                st.warning("获取智能体信息失败")
        except Exception as e:
            st.error(f"请求失败：{e}")

    st.divider()

    # 使用说明
    st.header("📖 启动说明")
    st.markdown("""
    **后端服务：**
    ```bash
    cd backend
    python main.py
    ```

    **前端界面：**
    ```bash
    cd frontend
    streamlit run app.py
    ```
    """)

# ──────────────────────────────────────────
# 主界面
# ──────────────────────────────────────────
st.title("🤖 智能运维助手")
st.caption(f"会话 ID：`{st.session_state.thread_id}` | 基于 LangChain + 智谱AI GLM-4")

# 显示聊天历史
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 聊天输入
if prompt := st.chat_input("请输入你的问题，例如：CPU使用率怎么样？"):
    # 显示用户消息
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # 调用后端 API
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        message_placeholder.markdown("⏳ 智能体思考中...")

        try:
            with st.spinner("正在分析..."):
                response = requests.post(
                    f"{api_base}/chat",
                    json={
                        "text": prompt,
                        "thread_id": st.session_state.thread_id,   # 传入会话 ID，支持多轮记忆
                        "show_init_info": False
                    },
                    timeout=60   # LangChain 工具链调用可能需要更长时间
                )

            if response.status_code == 200:
                data = response.json()
                answer = data.get("response", "未收到有效回答")    # 字段名为 response
                proc_time = data.get("processing_time", 0)
                agent_type = data.get("agent_type", "")

                # 模拟打字效果
                full_response = ""
                for word in answer.split():
                    full_response += word + " "
                    message_placeholder.markdown(full_response + "▌")
                    time.sleep(0.03)

                message_placeholder.markdown(full_response.strip())
                st.caption(f"处理时间：{proc_time:.2f}s | {agent_type}")
                st.session_state.messages.append({"role": "assistant", "content": full_response.strip()})

            else:
                error_detail = ""
                try:
                    error_detail = response.json().get("detail", "")
                except Exception:
                    pass
                err = f"后端错误 {response.status_code}"
                if error_detail:
                    err += f"：{error_detail}"
                message_placeholder.markdown(f"❌ {err}")
                st.session_state.messages.append({"role": "assistant", "content": f"❌ {err}"})

        except requests.exceptions.ConnectionError:
            msg = "❌ 无法连接到后端服务\n\n请先启动后端：\n```bash\ncd backend\npython main.py\n```"
            message_placeholder.markdown(msg)
            st.session_state.messages.append({"role": "assistant", "content": msg})

        except requests.exceptions.Timeout:
            msg = "⏰ 请求超时（>60s）\n\n请稍后重试，或简化问题。"
            message_placeholder.markdown(msg)
            st.session_state.messages.append({"role": "assistant", "content": msg})

        except Exception as e:
            msg = f"❌ 发生错误：{e}"
            message_placeholder.markdown(msg)
            st.session_state.messages.append({"role": "assistant", "content": msg})

# ──────────────────────────────────────────
# 底部
# ──────────────────────────────────────────
st.divider()
col1, col2 = st.columns([3, 1])
with col1:
    st.caption("**智能运维助手** v2.0 | LangChain ReAct 智能体 + 智谱AI GLM-4")
with col2:
    if st.button("清空聊天", type="secondary", use_container_width=True):
        st.session_state.messages = [
            {
                "role": "assistant",
                "content": "聊天已清空。有什么我可以帮你的？"
            }
        ]
        st.rerun()
