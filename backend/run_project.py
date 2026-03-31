#!/usr/bin/env python3
"""
智能运维助手 - 项目运行指南和测试脚本
"""

import os
import sys
import subprocess
import time

def print_header():
    """打印标题"""
    print("=" * 70)
    print("🤖 智能运维助手 - 项目运行指南")
    print("=" * 70)

def check_python_version():
    """检查Python版本"""
    print("\n1. 检查Python版本...")
    version = sys.version_info
    print(f"   当前Python版本: {version.major}.{version.minor}.{version.micro}")
    
    if version.major == 3 and version.minor >= 10:
        print("   ✅ Python版本符合要求 (>= 3.10)")
        return True
    else:
        print("   ⚠️  Python版本可能过低，建议使用Python 3.10+")
        return True  # 仍然继续

def check_dependencies():
    """检查依赖"""
    print("\n2. 检查项目依赖...")
    
    required = [
        "psutil",
        "langchain",
        "langchain-openai", 
        "fastapi",
        "uvicorn",
        "streamlit",
        "requests",
        "python-dotenv"
    ]
    
    missing = []
    for package in required:
        try:
            __import__(package.replace("-", "_"))
            print(f"   ✅ {package}")
        except ImportError:
            print(f"   ❌ {package} (未安装)")
            missing.append(package)
    
    if missing:
        print(f"\n   ⚠️  发现 {len(missing)} 个未安装的依赖")
        print(f"   请运行: pip install {' '.join(missing)}")
        print(f"   或运行: pip install -r requirements.txt")
        return False
    else:
        print(f"\n   ✅ 所有依赖已安装")
        return True

def check_env_config():
    """检查环境配置"""
    print("\n3. 检查环境配置文件...")
    
    env_file = ".env"
    example_file = ".env.example"
    
    if not os.path.exists(example_file):
        print("   ❌ 找不到 .env.example 文件")
        return False
    
    if not os.path.exists(env_file):
        print("   ⚠️  找不到 .env 文件，正在创建...")
        try:
            with open(example_file, 'r') as src, open(env_file, 'w') as dst:
                dst.write(src.read())
            print("   ✅ 已创建 .env 文件")
        except Exception as e:
            print(f"   ❌ 创建失败: {e}")
            return False
    
    # 检查API Key是否已配置
    with open(env_file, 'r') as f:
        content = f.read()
        
    if "your_openai_api_key_here" in content:
        print("   ⚠️  API Key未配置")
        print("   请编辑 .env 文件，填入有效的OpenAI兼容API Key")
        print("   可用选项:")
        print("   1. GitHub Copilot API Key")
        print("   2. OpenAI API Key")
        print("   3. 其他OpenAI兼容服务")
        return False
    else:
        print("   ✅ API Key已配置")
        return True

def test_backend():
    """测试后端服务"""
    print("\n4. 测试后端功能...")
    
    sys.path.append("backend")
    
    try:
        # 测试工具函数
        from tools import get_cpu_usage, get_memory_usage
        cpu = get_cpu_usage()
        mem = get_memory_usage()
        print(f"   ✅ 工具函数测试成功")
        print(f"      CPU: {cpu}")
        print(f"      内存: {mem}")
        
        # 测试智能体（可选）
        print("\n   测试智能体连接...")
        try:
            from agent import create_agent
            agent = create_agent()
            print(f"   ✅ 智能体初始化成功")
        except Exception as e:
            print(f"   ⚠️  智能体初始化警告: {e}")
            print("     可能是API Key问题，但工具函数仍可用")
            
        return True
        
    except Exception as e:
        print(f"   ❌ 后端测试失败: {e}")
        return False

def run_backend():
    """运行后端服务"""
    print("\n5. 启动后端服务...")
    
    backend_dir = "backend"
    if not os.path.exists(backend_dir):
        print(f"   ❌ 找不到后端目录: {backend_dir}")
        return False
    
    print(f"   后端服务将运行在: http://localhost:8000")
    print(f"   API文档: http://localhost:8000/docs")
    print(f"   按 Ctrl+C 停止服务")
    
    try:
        # 在单独的进程中运行
        import threading
        
        def run_server():
            os.chdir(backend_dir)
            subprocess.run([sys.executable, "main.py"])
        
        server_thread = threading.Thread(target=run_server)
        server_thread.daemon = True
        server_thread.start()
        
        print(f"   ✅ 后端服务已启动")
        print(f"   等待3秒让服务完全启动...")
        time.sleep(3)
        return True
        
    except Exception as e:
        print(f"   ❌ 启动失败: {e}")
        return False

def run_frontend():
    """运行前端服务"""
    print("\n6. 启动前端服务...")
    
    frontend_dir = "frontend"
    if not os.path.exists(frontend_dir):
        print(f"   ❌ 找不到前端目录: {frontend_dir}")
        return False
    
    print(f"   前端服务将运行在: http://localhost:8501")
    print(f"   按 Ctrl+C 停止服务")
    
    try:
        # 在单独的进程中运行
        import threading
        
        def run_frontend_app():
            os.chdir(frontend_dir)
            subprocess.run([sys.executable, "-m", "streamlit", "run", "app.py"])
        
        frontend_thread = threading.Thread(target=run_frontend_app)
        frontend_thread.daemon = True
        frontend_thread.start()
        
        print(f"   ✅ 前端服务已启动")
        print(f"   等待3秒让服务完全启动...")
        time.sleep(3)
        return True
        
    except Exception as e:
        print(f"   ❌ 启动失败: {e}")
        return False

def print_usage_guide():
    """打印使用指南"""
    print("\n" + "=" * 70)
    print("📚 使用指南")
    print("=" * 70)
    
    print("""
🔧 手动运行步骤:

1. 安装依赖:
   pip install -r requirements.txt

2. 配置API Key:
   编辑 .env 文件，填入有效的API Key
   
3. 启动后端服务 (终端1):
   cd backend
   python main.py
   
4. 启动前端服务 (终端2):
   cd frontend
   streamlit run app.py
   
5. 访问应用:
   前端: http://localhost:8501
   后端API文档: http://localhost:8000/docs

🧪 测试功能:
   - 运行: python test_tools.py     # 测试工具函数
   - 运行: python test_agent_simple.py # 测试智能体
   - 运行: python test_api.py       # 测试API连接

📁 项目结构:
   smart-ops-assistant/
   ├── backend/          # 后端代码
   │   ├── tools.py     # CPU/内存/服务检查
   │   ├── agent.py     # LangChain智能体
   │   └── main.py      # FastAPI服务
   ├── frontend/        # 前端代码
   │   └── app.py       # Streamlit界面
   ├── docs/           # 文档
   ├── .env            # 环境配置
   ├── requirements.txt # 依赖列表
   └── README.md       # 项目说明

💡 提示:
   - 第一次使用需要配置有效的OpenAI兼容API Key
   - 服务启动后，在前端输入问题如"CPU使用率怎么样？"
   - 确保网络连接正常，API服务可访问
""")

def main():
    """主函数"""
    print_header()
    
    # 检查基本条件
    check_python_version()
    
    deps_ok = check_dependencies()
    if not deps_ok:
        print("\n⚠️ 请先安装依赖再继续")
        return
    
    env_ok = check_env_config()
    if not env_ok:
        print("\n⚠️ 请先配置API Key再继续")
        return
    
    # 测试后端
    backend_ok = test_backend()
    if not backend_ok:
        print("\n⚠️ 后端测试失败，请检查代码")
        return
    
    print("\n" + "=" * 70)
    print("🎉 项目准备就绪！")
    print("=" * 70)
    
    # 询问是否自动启动服务
    print("\n是否自动启动前后端服务？ (y/n): ", end="")
    choice = input().strip().lower()
    
    if choice == 'y':
        # 启动后端
        if run_backend():
            print("\n✅ 后端服务运行中...")
        else:
            print("\n❌ 后端服务启动失败")
            return
            
        # 启动前端
        if run_frontend():
            print("\n✅ 前端服务运行中...")
        else:
            print("\n❌ 前端服务启动失败")
            return
            
        print("\n" + "=" * 70)
        print("🚀 服务已启动！")
        print("=" * 70)
        print("访问地址:")
        print("  前端界面: http://localhost:8501")
        print("  后端文档: http://localhost:8000/docs")
        print("\n按 Ctrl+C 停止所有服务")
        print("=" * 70)
        
        # 保持程序运行
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n\n服务已停止")
            
    else:
        print_usage_guide()

if __name__ == "__main__":
    main()