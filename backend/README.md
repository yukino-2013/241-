# 智能运维助手 (Smart Ops Assistant)

基于 **LangChain 1.x + 智谱AI GLM-4** 的高级智能运维助手，通过自然语言对话进行服务器状态查询，支持多轮记忆、ReAct 推理引擎和自动化运维扩展。

---

## 核心特性

- **LangChain ReAct 智能体**：推理-行动-观察三段式高级模式，真正理解自然语言意图并选择工具
- **多轮对话记忆**：基于 `InMemorySaver`，同一 `thread_id` 内上下文全程保持
- **系统监控工具链**：CPU 使用率、内存使用情况、服务状态检查、系统健康综合评估
- **可扩展架构**：预留 OpenCALW 等自动化运维工具集成接口
- **单例模式优化**：智能体只初始化一次，后续调用无额外开销
- **生产就绪**：完善的错误处理、降级机制、FastAPI 异步服务、Streamlit 前端

---

## 项目结构

```
smart-ops-assistant/
├── backend/
│   ├── agent.py          # LangChain 增强版智能体（核心）
│   ├── main.py           # FastAPI API 服务
│   ├── tools.py          # 底层系统监控工具函数
│   └── test.py           # 完整功能测试套件
├── frontend/
│   └── app.py            # Streamlit 聊天界面
├── docs/                 # 文档目录
├── opencalw_integration.py  # 自动化运维扩展示例（OpenCALW 风格）
├── requirements.txt      # 项目依赖
├── 智谱API配置指南.md    # 智谱 API 申请和配置说明
└── README.md
```

---

## 快速开始

### 1. 安装依赖

```bash
# 建议使用 Python 3.10 ~ 3.12（LangChain 兼容性最佳）
pip install -r requirements.txt
```

### 2. 配置 API Key

在项目根目录创建 `.env` 文件：

```ini
ZHIPUAI_API_KEY=你的智谱API_Key
ZHIPUAI_MODEL=glm-4
```

获取 API Key：https://open.bigmodel.cn/（注册即有免费额度）

详细配置说明见：[智谱API配置指南.md](./智谱API配置指南.md)

### 3. 启动后端服务

```bash
cd backend
python main.py
```

服务启动后访问：
- API 文档：http://localhost:8000/docs
- 根路径：http://localhost:8000

### 4. 启动前端界面（可选）

```bash
cd frontend
streamlit run app.py
```

访问：http://localhost:8501

---

## API 使用

### 对话接口

```bash
POST /chat
```

```json
{
  "text": "CPU使用率怎么样？",
  "thread_id": "user_123"
}
```

`thread_id` 相同则共享对话记忆（支持多轮上下文）。

**响应示例：**

```json
{
  "response": "当前CPU使用率为 12.5%，系统运行正常。",
  "agent_type": "完整LangChain增强版智能体",
  "processing_time": 2.341,
  "thread_id": "user_123"
}
```

### 其他接口

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/info` | 查看智能体信息（工具列表、版本等） |
| GET | `/health` | 系统健康检查（CPU/内存/磁盘） |
| GET | `/tools` | 可用工具列表 |
| GET | `/conversation/{thread_id}` | 获取对话历史 |
| DELETE | `/conversation/{thread_id}` | 清除对话历史 |

### Python 直接调用

```python
from backend.agent import ask_full_langchain_agent

# 单次调用
response = ask_full_langchain_agent("分析系统健康状态")
print(response)

# 多轮对话（相同 thread_id 保留上下文）
ask_full_langchain_agent("我叫张三", thread_id="session_1")
ask_full_langchain_agent("我刚才说我叫什么？", thread_id="session_1")  # 会记住"张三"
```

---

## 核心模块说明

### `backend/agent.py` — LangChain 智能体

- `FullLangChainAgent`：完整 LangChain ReAct 智能体（单例）
- `ask_full_langchain_agent(question, thread_id)`：便捷调用函数
- 内置 5 个工具：CPU 监控、内存监控、服务状态、系统信息、健康分析
- 使用 `InMemorySaver` 维护多轮对话上下文

### `backend/tools.py` — 底层工具函数

- `get_cpu_usage() -> float`：返回 CPU 使用率（%）
- `get_memory_usage() -> dict`：返回内存详情（used_gb, total_gb, percent 等）
- `check_service_status(service_name) -> str`：检查服务/进程是否运行

### `backend/main.py` — FastAPI 服务

- 所有路由均基于完整 LangChain 智能体
- 支持后台日志记录、CORS 跨域、Pydantic 数据校验

### `opencalw_integration.py` — 扩展示例

展示如何将 **自动化运维工具**（文件操作、定时任务、自动修复）集成进 LangChain 工具链。参考此文件开发新工具，然后注册到 `agent.py` 的工具列表即可。

---

## 扩展开发（添加新工具）

1. 在 `tools.py` 或新文件中实现底层函数
2. 在 `agent.py` 中用 `@langchain_tool` 装饰器包装
3. 添加到 `FullLangChainAgent._initialize_components()` 的 `self.tools` 列表
4. 在 `test.py` 中添加测试用例

```python
# 示例：添加磁盘清理工具
from langchain.tools import tool as langchain_tool

@langchain_tool
def clean_temp_files_tool() -> str:
    """清理系统临时文件，释放磁盘空间。"""
    # 实现清理逻辑
    ...
```

---

## 测试

```bash
cd backend
python test.py
```

测试内容包括：工具函数、智能体初始化、系统监控查询、多轮对话记忆。

---

## 故障排除

### 智能体初始化失败

检查 `.env` 文件中的 `ZHIPUAI_API_KEY` 是否填写且有效。

### LangChain / langgraph 版本问题

```bash
pip install --upgrade langchain langchain-openai langgraph
```

### Python 版本

推荐 **Python 3.10 ~ 3.12**。如使用 Python 3.13，确保 `numpy>=2.0.0`。

---

## 技术栈

| 组件 | 版本要求 | 用途 |
|------|---------|------|
| Python | 3.10+ | 运行环境 |
| LangChain | >=0.1.0 | AI 智能体框架 |
| LangGraph | >=0.1.0 | ReAct + 对话记忆 |
| langchain-openai | >=0.0.5 | OpenAI 兼容接口 |
| 智谱 GLM-4 | - | 大语言模型 |
| FastAPI | >=0.104 | API 服务框架 |
| Streamlit | >=1.29 | 前端界面 |
| psutil | >=5.9 | 系统监控 |

---

**项目状态**: 生产就绪 | **AI 框架**: LangChain 增强版 | **扩展性**: 支持 OpenCALW 等自动化工具
