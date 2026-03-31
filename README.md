# 241-
yukino
智能运维助手 (Smart Ops Assistant)

项目简介
智能运维助手是一个基于自然语言交互的服务器状态查询工具。用户通过对话提问（如“CPU使用率多少？”），系统自动调用后台工具获取实时系统信息并返回结果。项目采用前后端分离架构，前端提供聊天界面，后端通过 LangChain 智能体调用系统工具，并接入智谱AI大模型进行意图识别与工具调度。

技术栈

| 层级     | 技术选型                          |
|----------|-----------------------------------|
| 前端     | Python 3.10+、Streamlit、requests |
| 后端     | Python 3.10+、FastAPI、uvicorn    |
| 智能体   | LangChain、智谱AI API (glm-4-flash) |
| 系统工具 | psutil、subprocess                |
| 协作工具 | Git、GitHub                       |

人员分工

| 角色     | 姓名 | 主要职责                     |
|----------|------|------------------------------|
| 后端开发 | A    | 实现 tools.py、agent.py、main.py |
| 前端开发 | B    | 实现 app.py 前端界面          |
| 测试与文档 | C   | 编写测试用例、README 及环境配置 |


项目运行说明

环境要求
- Python 3.10 或更高版本
- Git
- 智谱AI API Key（[申请地址](https://open.bigmodel.cn/)）

克隆仓库
```bash
git clone <仓库地址>
cd smart-ops-assistant
