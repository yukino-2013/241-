# MEMORY.md - 项目长期记忆

## 项目：智能运维助手（smart-ops-frontend）

### 基本信息
- **题目：** 智能运维助手设计与实现
- **一句话介绍：** 通过自然语言对话查询服务器状态（CPU、内存、服务运行情况）的AI智能体
- **技术栈：** 后端 Python + LangChain + FastAPI / 前端 Streamlit / 协作 Git + GitHub
- **工作空间：** E:/smart-ops-frontend
- **Python：** 3.13.0，虚拟环境在 venv/

### 分工
- **角色A：** 后端核心（tools.py, agent.py, main.py）
- **角色B：** 前端界面（frontend/app.py）— 当前用户
- **角色C：** 辅助开发 + 测试 + 文档

### 已完成
- 2026-03-30：角色B的前端任务全部完成
  - 创建项目目录结构（frontend/, backend/, docs/）
  - 安装依赖：streamlit 1.55.0, requests
  - 完成 app.py：聊天界面 + 模拟模式 + 真实API模式 + 快捷按钮 + 错误处理
  - Streamlit 服务可正常启动（http://localhost:8501）
- 2026-03-31：生成操作流程Word文档（按天排版）
  - gen_docx.py 改为 Day1~Day5 按天格式
  - 输出文件：D:/Desktop/角色B_前端开发日报.docx

### 运行方式
- 前端：`E:/smart-ops-frontend/venv/Scripts/streamlit.exe run E:/smart-ops-frontend/frontend/app.py`
- 默认模拟模式（USE_MOCK=true），等A后端就绪后设为false
