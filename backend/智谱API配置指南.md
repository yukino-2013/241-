# 智谱API配置指南

## ✅ 已完成修改的文件

### 1. `.env` 文件
**修改内容**：将OpenAI配置改为智谱API配置
```ini
# 智谱API配置
ZHIPUAI_API_KEY=你的智谱API_Key_这里
ZHIPUAI_MODEL=glm-4  # 可选：glm-4, glm-4v, glm-3-turbo, charglm-3
```

### 2. `.env.example` 文件
**修改内容**：同步更新示例配置

### 3. `backend/agent.py` 文件
**修改内容**：
- `initialize_ai_model()` 函数改为智谱API版本
- 使用智谱API的API地址：`https://open.bigmodel.cn/api/paas/v4`
- 更新错误提示信息

### 4. `requirements.txt` 文件
**修改内容**：
- 添加 `zhipuai==2.1.5.20250825`
- 添加 `sniffio==1.3.1`
- 保留 `langchain`（因为智谱API兼容OpenAI格式）

### 5. `README.md` 文件
**修改内容**：更新智谱API配置说明和获取步骤

## 🚀 快速启动步骤

### 1. 获取智谱API Key
1. 访问 https://open.bigmodel.cn/
2. 注册并登录
3. 在控制台创建API Key（有免费额度）

### 2. 配置项目
```bash
# 编辑.env文件，填入你的API Key
ZHIPUAI_API_KEY=你的实际API_Key
```

### 3. 测试配置
```bash
# 运行测试脚本
python test_zhipuai_simple.py
```

### 4. 启动服务
```bash
# 启动后端API
cd backend
python main.py
# 或使用简化版（如果完整版有依赖问题）
python main_simple.py
```

## 🔧 技术原理

### 智谱API与LangChain集成
1. 智谱API兼容OpenAI API格式
2. 使用 `langchain_openai.ChatOpenAI` 类
3. 指定 `openai_api_base="https://open.bigmodel.cn/api/paas/v4"`
4. 使用智谱的API Key和模型名称

### 为什么选择智谱API
1. **国内服务**：无需翻墙，访问稳定
2. **免费额度**：新用户有免费使用量
3. **中文优化**：对中文支持更好
4. **API兼容**：兼容OpenAI格式，代码改动最小

## 📞 遇到问题？

### 常见问题
1. **API Key错误**：确认.env文件中配置正确
2. **网络连接失败**：检查防火墙和代理设置
3. **余额不足**：在智谱控制台查看余额
4. **依赖安装失败**：尝试 `pip install --upgrade zhipuai`

### 测试工具
已创建测试脚本：
- `test_zhipuai_simple.py` - 测试智谱API连接
- 运行后根据提示调试

## 🎯 项目状态
- ✅ 后端核心功能（工具函数）正常
- ✅ 智谱API集成完成
- ✅ API服务可正常启动
- ✅ 文档更新完成

现在你可以使用智谱API运行智能运维助手了！