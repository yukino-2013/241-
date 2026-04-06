# 241-
yukino
智能运维助手 (Smart Ops Assistant)

项目简介

  智能运维助手是一个基于自然语言交互的服务器状态查询工具。用户通过对话提问,如:"CPU使用率是多少"，系统自动调用后台工具获取实时系统信息并返回结果。项目采用前后端分离架构，前端提供聊天界面，后端通过 LangChain 智能体调用系统工具，并接入智谱AI大模型进行意图识别与工具调度。

技术栈

| 层级     | 技术选型                          |
|----------|-----------------------------------|
| 前端     | Python 3.10+、Streamlit |
| 后端     | Python 3.10+、FastAPI、智谱AI API   |
| 智能体   | LangChain、智谱AI API (glm-4-flash) |
| 系统工具 | psutil、subprocess                |
| 协作工具 | Git、GitHub                       |



核心特性

  真正的AI智能体：理解自然语言，智能调用工具
  
  优化输出：减少冗余信息，简洁高效
  
  单例模式：智能体只初始化一次，避免重复启动信息
  
  生产就绪：代码优化，文档完整


人员分工

| 角色     | 姓名 | 主要职责                     |
|----------|------|------------------------------|
| 后端开发 | A    | 实现 tools.py、agent.py、main.py   后端核心 - 工具函数、智能体封装、API接口 |
| 前端开发 | B    | 实现 app.py 前端界面    前端界面 - Streamlit聊天界面 |
| 测试与文档 | C   | 编写测试用例、README 及环境配置   辅助开发 + 测试 + 文档 |


项目运行说明

1.环境要求
- Python 3.10 或更高版本
- Git
- 智谱AI API Key（[申请地址](https://open.bigmodel.cn/)）

2.克隆仓库
```bash
git clone <仓库地址>
cd smart-ops-assistant

创建虚拟环境
python -m venv venv
Windows激活
venv\Scripts\activate
Linux/Mac激活
source venv/bin/activate

安装依赖
pip install -r requirements.txt

2. 配置智谱API Key
（1）获取智谱API Key：
   - 访问智谱AI开放平台：https://open.bigmodel.cn/
   - 注册账号并登录
   - 在控制台创建API Key，可获得免费额度

（2） 配置项目：
bash
复制环境变量模板
cp .env.example .env

（3） 编辑.env文件，填入你的智谱API配置：
ini
智谱API配置
ZHIPUAI_API_KEY=你的智谱API_Key_这里
ZHIPUAI_MODEL=glm-4  # 可选：glm-4, glm-4v, glm-3-turbo, charglm-3

（4） 验证配置：
bash
python 快速测试.py
```
3. 启动服务

方法一：优化版AI智能体（使用智谱API）
```bash
# 启动优化版AI智能体服务
cd backend
python main_zhipuai.py
# 服务运行在 http://localhost:8000
# API文档：http://localhost:8000/docs
```
方法二：简化版（无AI依赖）
```bash
# 启动简化版服务（无AI智能体）
cd backend
python main_simple.py
# 服务运行在 http://localhost:8001
```
方法三：快速启动（Windows）
```bash
# 双击运行 快速启动.bat
```
方法四：前端服务
```bash
# 启动前端服务（新终端）
cd frontend
streamlit run app.py
# 服务运行在 http://localhost:8501
```
项目结构（优化后）
```
smart-ops-assistant/
├── backend/                  # 后端代码
│   ├── agent_zhipuai.py     # 智谱AI智能体（优化版）
│   ├── main_zhipuai.py      # AI智能体API服务（优化版）
│   ├── main_simple.py       # 简化版API服务（备选）
│   └── tools.py             # 工具函数模块
├── frontend/                # 前端代码
│   └── app.py              # Streamlit聊天界面
├── docs/                   # 文档目录
├── .env                   # 环境变量配置
├── .env.example           # 环境变量模板
├── requirements.txt       # 项目依赖
├── README.md             # 项目说明
├── 快速启动.bat           # Windows一键启动
├── 快速测试.py           # 快速测试脚本
├── 手动测试指南.md        # 详细测试文档
├── 智谱API配置指南.md     # API配置说明
├── 项目架构与修改总结.md   # 架构设计文档
└── 依赖检查和项目状态报告.md # 项目状态报告
```

已清理的冗余文件
- `test_agent_simple.py`, `test_api.py`, `test_tools.py`
- `test_zhipuai_simple.py`, `start_test.py`
- `backend/agent.py`, `backend/main.py`
- `测试智谱AI智能体.py`

核心文件说明
1. **`agent_zhipuai.py`** - 真正的AI智能体，支持自然语言理解
2. **`main_zhipuai.py`** - 优化API服务，减少冗余输出
3. **`tools.py`** - 服务器监控工具函数
4. **`快速测试.py`** - 无需启动服务器的完整功能测试















