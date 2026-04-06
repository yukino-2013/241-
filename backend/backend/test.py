#!/usr/bin/env python3
"""
智能运维助手 - 全面测试脚本
测试完整LangChain增强版智能体的所有功能
"""

import os
import sys
import time
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

def test_basic_tools():
    """测试基础工具函数"""
    print("=" * 60)
    print("测试基础工具函数")
    print("=" * 60)
    
    try:
        from tools import get_cpu_usage, get_memory_usage
        
        # 测试CPU使用率
        print("1. 测试CPU使用率:")
        cpu_usage = get_cpu_usage()
        print(f"   结果类型: {type(cpu_usage)}, 值: {cpu_usage}")
        assert isinstance(cpu_usage, float), "CPU使用率应该返回浮点数"
        assert 0 <= cpu_usage <= 100, f"CPU使用率应该在0-100%之间，实际值: {cpu_usage}"
        print("   [OK] CPU使用率测试通过")
        
        # 测试内存使用情况
        print("\n2. 测试内存使用情况:")
        memory_info = get_memory_usage()
        print(f"   结果类型: {type(memory_info)}, 键: {list(memory_info.keys())}")
        assert isinstance(memory_info, dict), "内存使用情况应该返回字典"
        required_keys = ["used_gb", "total_gb", "percent"]
        for key in required_keys:
            assert key in memory_info, f"内存信息缺少键: {key}"
        print("   [OK] 内存使用情况测试通过")
        
        return True
    except Exception as e:
        print(f"   [FAIL] 基础工具测试失败: {e}")
        return False

def test_full_langchain_agent():
    """测试完整LangChain智能体"""
    print("\n" + "=" * 60)
    print("测试完整LangChain增强版智能体")
    print("=" * 60)
    
    try:
        from agent import FullLangChainAgent
        
        # 初始化智能体
        print("初始化智能体...")
        agent = FullLangChainAgent(show_init_info=False)
        info = agent.get_info()
        
        print(f"智能体类型: {info['agent_type']}")
        print(f"工具数量: {info['tools_count']}")
        print(f"支持LangChain智能体: {info['has_langchain_agent']}")
        print(f"支持对话记忆: {info['has_memory']}")
        
        # 测试简单查询
        print("\n测试简单查询:")
        test_queries = [
            ("CPU使用率是多少？", "cpu"),
            ("内存使用情况怎么样？", "内存"),
            ("显示系统信息", "系统"),
            ("分析系统健康状况", "健康")
        ]
        
        all_passed = True
        for query, expected_keyword in test_queries:
            print(f"\n查询: {query}")
            try:
                response = agent.ask(query)
                print(f"响应: {response[:100]}..." if len(response) > 100 else f"响应: {response}")
                
                if "失败" in response or "错误" in response.lower():
                    print("   [WARN] 查询可能失败")
                elif expected_keyword.lower() not in response.lower():
                    print(f"   [WARN] 响应中可能不包含关键词'{expected_keyword}'")
                else:
                    print("   [OK] 查询成功")
            except Exception as e:
                print(f"   [FAIL] 查询失败: {e}")
                all_passed = False
        
        # 测试多轮对话（如果支持）
        if info['has_memory']:
            print("\n" + "-" * 40)
            print("测试多轮对话记忆:")
            
            # 第一轮：提供信息
            print("第一轮: '我的名字是张三'")
            response1 = agent.ask("我的名字是张三", use_thread_id="test_user_001")
            print(f"响应: {response1[:80]}..." if len(response1) > 80 else f"响应: {response1}")
            
            # 第二轮：验证记忆
            print("第二轮: '我刚才说我叫什么名字？'")
            response2 = agent.ask("我刚才说我叫什么名字？", use_thread_id="test_user_001")
            print(f"响应: {response2[:80]}..." if len(response2) > 80 else f"响应: {response2}")
            
            # 检查是否记得信息
            if "张三" in response2:
                print("   [OK] 对话记忆功能正常")
            else:
                print("   [WARN] 对话记忆可能未正常工作")
        else:
            print("\n[WARN] 当前智能体不支持对话记忆")
        
        return all_passed
    except Exception as e:
        print(f"[FAIL] 完整LangChain智能体测试失败: {e}")
        return False

def test_service_check():
    """测试服务状态检查"""
    print("\n" + "=" * 60)
    print("测试服务状态检查")
    print("=" * 60)
    
    try:
        from tools import check_service_status
        
        # 测试常见服务
        test_services = ["nginx", "sshd", "mysql", "python"]
        
        for service in test_services:
            print(f"\n检查服务: {service}")
            try:
                status = check_service_status(service)
                print(f"状态: {status}")
                print("   [OK] 服务检查完成")
            except Exception as e:
                print(f"   [WARN] 服务检查失败: {e}")
        
        return True
    except Exception as e:
        print(f"[FAIL] 服务检查测试失败: {e}")
        return False

def test_performance():
    """测试性能"""
    print("\n" + "=" * 60)
    print("测试响应性能")
    print("=" * 60)
    
    try:
        from agent import FullLangChainAgent
        
        agent = FullLangChainAgent(show_init_info=False)
        
        # 测试CPU查询的响应时间
        print("测试CPU查询响应时间:")
        start_time = time.time()
        response = agent.ask("CPU使用率")
        end_time = time.time()
        
        response_time = end_time - start_time
        print(f"响应内容: {response[:50]}..." if len(response) > 50 else f"响应内容: {response}")
        print(f"响应时间: {response_time:.2f}秒")
        
        if response_time < 3:
            print("   [OK] 响应性能良好")
        elif response_time < 5:
            print("   [WARN] 响应速度一般")
        else:
            print("   [WARN] 响应速度较慢")
        
        return True
    except Exception as e:
        print(f"[FAIL] 性能测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("智能运维助手 - 全面功能测试")
    print("=" * 60)
    
    # 检查API密钥
    api_key = os.getenv("ZHIPUAI_API_KEY")
    if not api_key:
        print("[WARN] 警告: 未找到ZHIPUAI_API_KEY环境变量")
        print("请在.env文件中配置API密钥")
        # 继续测试基础功能
    
    test_results = []
    
    # 运行所有测试
    test_results.append(("基础工具函数", test_basic_tools()))
    test_results.append(("完整LangChain智能体", test_full_langchain_agent()))
    test_results.append(("服务状态检查", test_service_check()))
    test_results.append(("响应性能", test_performance()))
    
    # 输出测试总结
    print("\n" + "=" * 60)
    print("测试总结")
    print("=" * 60)
    
    passed_count = 0
    total_count = len(test_results)
    
    for test_name, result in test_results:
        status = "[OK] 通过" if result else "[FAIL] 失败"
        print(f"{test_name}: {status}")
        if result:
            passed_count += 1
    
    success_rate = (passed_count / total_count) * 100
    
    print(f"\n总测试项: {total_count}")
    print(f"通过项: {passed_count}")
    print(f"失败项: {total_count - passed_count}")
    print(f"成功率: {success_rate:.1f}%")
    
    if passed_count == total_count:
        print("\n[SUCCESS] 所有测试通过！智能运维助手功能正常。")
        return True
    else:
        print(f"\n[WARN]  {total_count - passed_count} 项测试失败，请检查相关功能。")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)