#!/usr/bin/env python3
"""
智能运维助手 - 快速测试脚本
无需启动服务器，直接测试核心功能
"""

import os
import sys
from dotenv import load_dotenv

# 添加backend目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

def test_environment():
    """测试环境配置"""
    print("=" * 60)
    print("智能运维助手 - 环境测试")
    print("=" * 60)
    
    # 加载环境变量
    load_dotenv()
    
    # 检查智谱API配置
    api_key = os.getenv("ZHIPUAI_API_KEY")
    model = os.getenv("ZHIPUAI_MODEL", "glm-4")
    
    print("[1] 智谱API配置检查:")
    print(f"    API Key: {api_key[:10] if api_key and len(api_key) > 10 else '未配置'}")
    print(f"    模型: {model}")
    
    if api_key and api_key != "your_zhipuai_api_key_here":
        print("    [OK] API Key已配置")
    else:
        print("    [WARN] 请配置真实的智谱API Key")
    
    return api_key, model

def test_tools():
    """测试工具函数"""
    print("\n[2] 工具函数测试:")
    
    try:
        from tools import get_cpu_usage, get_memory_usage, check_service_status
        
        # 测试CPU使用率
        try:
            cpu_result = get_cpu_usage()
            print(f"    CPU使用率: {cpu_result}")
        except Exception as e:
            print(f"    CPU测试失败: {e}")
        
        # 测试内存使用率
        try:
            memory_result = get_memory_usage()
            print(f"    内存使用率: {memory_result}")
        except Exception as e:
            print(f"    内存测试失败: {e}")
        
        # 测试服务状态检查
        try:
            service_result = check_service_status("python")
            print(f"    Python服务状态: {service_result}")
        except Exception as e:
            print(f"    服务状态测试失败: {e}")
            
    except ImportError as e:
        print(f"    [ERROR] 无法导入工具模块: {e}")
        return False
    
    return True

def test_api_direct():
    """直接测试API功能（不启动服务器）"""
    print("\n[3] API功能测试:")
    
    try:
        # 测试简化版API的聊天功能
        from main_simple import create_tools_dict, chat_with_tools
        
        # 获取工具函数
        tools_dict = create_tools_dict()
        print(f"    可用工具: {len(tools_dict)} 个")
        for tool_name in tools_dict:
            print(f"      - {tool_name}")
        
        # 测试简单问题
        test_questions = [
            "CPU使用率怎么样？",
            "内存使用情况如何？",
            "检查python服务状态"
        ]
        
        for question in test_questions:
            try:
                answer = chat_with_tools(question, tools_dict)
                print(f"\n    问题: {question}")
                print(f"    回答: {answer[:100]}...")
            except Exception as e:
                print(f"    问题 '{question}' 处理失败: {e}")
                
    except ImportError as e:
        print(f"    [WARN] 无法导入API模块: {e}")
        print("    这可能是正常的，因为需要启动服务器")
        return False
    
    return True

def main():
    """主测试函数"""
    try:
        # 测试环境
        api_key, model = test_environment()
        
        # 测试工具函数
        tools_ok = test_tools()
        
        # 测试API功能
        api_ok = test_api_direct()
        
        print("\n" + "=" * 60)
        print("测试总结:")
        print("=" * 60)
        
        if api_key and api_key != "your_zhipuai_api_key_here":
            print("[OK] 智谱API配置正确")
        else:
            print("[WARN] 需要配置智谱API Key")
        
        if tools_ok:
            print("[OK] 工具函数正常")
        else:
            print("[ERROR] 工具函数有问题")
        
        print("\n下一步:")
        print("1. 启动API服务器:")
        print("   cd backend")
        print("   python main_simple.py")
        print("\n2. 测试API接口:")
        print("   访问 http://127.0.0.1:8000/docs")
        print("   或运行测试命令:")
        print("   curl http://127.0.0.1:8000/health")
        
    except Exception as e:
        print(f"\n[ERROR] 测试过程中出错: {e}")
    
    print("\n按Enter键退出...")
    input()

if __name__ == "__main__":
    main()