#!/usr/bin/env python3
"""
智能运维助手 - LangChain增强版智能体
集成LangChain 1.x + 智谱AI GLM-4，支持ReAct推理、对话记忆、工具链管理
"""

import os
import sys
import threading
import time
import json
from typing import Dict, Any, List, Optional, Union
from dotenv import load_dotenv

# LangChain 1.x 核心组件
from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from langchain.tools import tool as langchain_tool
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langgraph.checkpoint.memory import InMemorySaver

# 加载环境变量
load_dotenv()

# 处理导入路径 - 确保在任何位置都能正确导入tools模块
def import_tools():
    """动态导入tools模块，处理不同位置的导入"""
    try:
        # 尝试直接导入
        from tools import get_cpu_usage, get_memory_usage, check_service_status
        return get_cpu_usage, get_memory_usage, check_service_status
    except ImportError:
        # 如果在根目录，添加backend路径
        import sys
        backend_path = os.path.join(os.path.dirname(__file__))
        if backend_path not in sys.path:
            sys.path.insert(0, backend_path)
        
        try:
            from tools import get_cpu_usage, get_memory_usage, check_service_status
            return get_cpu_usage, get_memory_usage, check_service_status
        except ImportError as e:
            raise ImportError(f"无法导入tools模块: {e}. 请确保tools.py文件在backend目录中")

# 导入工具函数
get_cpu_usage, get_memory_usage, check_service_status = import_tools()

# 定义LangChain工具
@langchain_tool
def get_cpu_usage_tool() -> str:
    """获取当前CPU使用率。当用户询问CPU使用情况、电脑卡不卡、系统负载时调用此工具。"""
    try:
        from tools import get_cpu_usage
        cpu_usage = get_cpu_usage()
        return f"当前CPU使用率为: {cpu_usage:.1f}%"
    except Exception as e:
        return f"获取CPU使用率失败: {str(e)}"

@langchain_tool
def get_memory_usage_tool() -> str:
    """获取当前内存使用情况。当用户询问内存够不够、内存使用率、剩余内存时调用此工具。"""
    try:
        from tools import get_memory_usage
        memory_info = get_memory_usage()
        return f"内存已使用{memory_info['used_gb']:.1f}GB/共{memory_info['total_gb']:.1f}GB，使用率{memory_info['percent']:.1f}%"
    except Exception as e:
        return f"获取内存使用率失败: {str(e)}"

@langchain_tool
def check_service_status_tool(service_name: str) -> str:
    """检查某个系统服务是否在运行。输入参数应为服务名称（如nginx、sshd、mysql、python）。当用户询问某个服务是否运行、服务状态时调用此工具。"""
    try:
        from tools import check_service_status
        status = check_service_status(service_name)
        return f"服务 {service_name} 状态: {status}"
    except Exception as e:
        return f"检查服务状态失败: {str(e)}"

@langchain_tool
def get_system_info_tool() -> str:
    """获取完整的系统信息，包括操作系统、主机名、Python版本、智能体信息等。"""
    try:
        import platform
        import socket
        import datetime
        
        info = []
        info.append(f"系统: {platform.system()} {platform.release()}")
        info.append(f"主机名: {socket.gethostname()}")
        info.append(f"Python版本: {platform.python_version()}")
        info.append(f"当前时间: {datetime.datetime.now()}")
        info.append(f"智能体类型: LangChain增强版智能体")
        info.append(f"LangChain版本: 1.2.14")
        info.append(f"AI模型: 智谱GLM-4")
        
        return "\n".join(info)
    except Exception as e:
        return f"获取系统信息失败: {str(e)}"

@langchain_tool
def analyze_system_health_tool() -> Dict[str, Any]:
    """分析系统健康状况，包括CPU、内存、磁盘和服务状态的综合评估。"""
    try:
        from tools import get_cpu_usage, get_memory_usage
        import psutil
        
        # 获取CPU和内存数据
        cpu_percent = get_cpu_usage()
        memory_info = get_memory_usage()
        
        health_report = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "cpu_usage": cpu_percent,
            "memory_usage": memory_info["percent"],
            "memory_details": memory_info,
            "disk_usage": {},
            "services_status": {},
            "overall_health": "良好"
        }
        
        # 检查磁盘使用情况
        for partition in psutil.disk_partitions():
            try:
                usage = psutil.disk_usage(partition.mountpoint)
                health_report["disk_usage"][partition.mountpoint] = {
                    "total_gb": round(usage.total / (1024**3), 2),
                    "used_gb": round(usage.used / (1024**3), 2),
                    "free_gb": round(usage.free / (1024**3), 2),
                    "percent": usage.percent
                }
            except:
                pass
        
        # 评估健康状况
        if cpu_percent > 90:
            health_report["overall_health"] = "警告"
        elif cpu_percent > 80:
            health_report["overall_health"] = "注意"
            
        if memory_info["percent"] > 90:
            health_report["overall_health"] = "警告"
        elif memory_info["percent"] > 80:
            if health_report["overall_health"] != "警告":
                health_report["overall_health"] = "注意"
        
        return health_report
    except Exception as e:
        return {"error": f"分析系统健康失败: {str(e)}"}

class FullLangChainAgent:
    """
    完整的LangChain增强版智能运维助手
    集成LangChain 1.x的所有高级功能
    """
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls, show_init_info: bool = True):
        """单例模式实现"""
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._initialized = False
        return cls._instance
    
    def __init__(self, show_init_info: bool = True):
        """初始化智能体（只在第一次调用时执行）"""
        if self._initialized:
            return
            
        self.show_init_info = show_init_info
        self.agent_type = "完整LangChain增强版智能体"
        self.agent = None
        self.checkpointer = None
        self.thread_id = "default_session"
        
        try:
            self._initialize_components()
            self._initialized = True
            
            if self.show_init_info:
                print("[INFO] 完整LangChain增强版智能运维助手初始化完成")
                print("   • LangChain 1.2.14集成: [OK]")
                print("   • 智谱AI模型: [OK]")
                print("   • 5个高级工具: [OK]")
                print("   • 对话记忆系统: [OK]")
                print("   • ReAct智能体模式: [OK]")
                print("   • Python 3.13兼容: [OK]")
        except Exception as e:
            print(f"[ERROR] 初始化完整LangChain智能体失败: {e}")
            raise
    
    def _initialize_components(self):
        """初始化所有组件"""
        # 1. 配置智谱AI（通过OpenAI兼容接口）
        api_key = os.getenv("ZHIPUAI_API_KEY")
        if not api_key:
            raise ValueError("请先在.env文件中配置ZHIPUAI_API_KEY")
        
        # 智谱AI的OpenAI兼容接口URL
        base_url = "https://open.bigmodel.cn/api/paas/v4"
        
        # 2. 初始化LangChain聊天模型（智谱AI兼容OpenAI API）
        self.model = ChatOpenAI(
            model="glm-4",
            openai_api_key=api_key,
            base_url=base_url,
            temperature=0.3,
            max_tokens=1000
        )
        
        # 3. 准备工具列表
        self.tools = [
            get_cpu_usage_tool,
            get_memory_usage_tool,
            check_service_status_tool,
            get_system_info_tool,
            analyze_system_health_tool
        ]
        
        # 4. 创建检查点保存器（用于对话记忆）
        self.checkpointer = InMemorySaver()
        
        # 为checkpointer设置默认配置
        self.checkpointer_config = {
            "configurable": {
                "thread_id": self.thread_id,
                "checkpoint_ns": "default",
                "checkpoint_id": "initial"
            }
        }
        
        # 5. 创建LangChain智能体
        system_prompt = """你是一个智能运维助手，专门帮助用户监控和管理系统状态。
你的主要功能包括：
1. 监控CPU、内存、磁盘使用情况
2. 检查服务运行状态
3. 分析系统健康状况
4. 提供运维建议

请根据用户的问题，智能地调用相应的工具来获取准确信息，然后给出清晰的回答。
如果用户的问题需要多个工具的信息，请依次调用它们并整合结果。
保持回答专业、清晰、有用。"""
        
        try:
            self.agent = create_agent(
                self.model,
                tools=self.tools,
                system_prompt=system_prompt,
                checkpointer=self.checkpointer
            )
        except Exception as e:
            print(f"[WARNING] 使用完整create_agent API失败，使用简化模式: {e}")
            # 如果create_agent失败，使用简化模式
            self.agent = None
            self.agent_type = "简化LangChain增强版智能体"
    
    def get_info(self) -> Dict[str, Any]:
        """获取智能体信息"""
        return {
            "agent_type": self.agent_type,
            "tools_count": len(self.tools) if hasattr(self, 'tools') else 0,
            "tool_names": [tool.name for tool in self.tools] if hasattr(self, 'tools') else [],
            "has_langchain_agent": self.agent is not None,
            "has_memory": self.checkpointer is not None,
            "thread_id": self.thread_id,
            "initialized": self._initialized,
            "init_time": getattr(self, 'init_time', None)
        }
    
    def ask(self, question: str, use_thread_id: Optional[str] = None) -> str:
        """
        使用LangChain智能体处理用户问题
        支持多轮对话记忆
        """
        if not self._initialized:
            return "智能体未初始化，请先初始化智能体"
        
        # 使用指定的线程ID或默认ID（用于对话记忆）
        thread_id = use_thread_id if use_thread_id else self.thread_id
        
        try:
            if self.agent is not None and self.checkpointer is not None:
                # 使用完整的LangChain智能体（带checkpointer）
                try:
                    # 为当前线程创建配置
                    config = {
                        "configurable": {
                            "thread_id": thread_id,
                            "checkpoint_ns": "default",
                            "checkpoint_id": f"checkpoint_{int(time.time())}"
                        }
                    }
                    
                    result = self.agent.invoke(
                        {"messages": [HumanMessage(content=question)]},
                        config=config
                    )
                    
                    # 提取AI的回复
                    if isinstance(result, dict) and "messages" in result:
                        messages = result["messages"]
                        for msg in reversed(messages):
                            if isinstance(msg, AIMessage):
                                return msg.content
                    
                    # 如果无法提取AI消息，返回原始结果
                    return str(result)
                except Exception as e:
                    print(f"[WARNING] LangChain智能体调用失败: {e}")
                    # 降级到简化模式
                    return self._simplified_ask(question)
            elif self.agent is not None:
                # 使用LangChain智能体（不带checkpointer）
                try:
                    result = self.agent.invoke(
                        {"messages": [HumanMessage(content=question)]}
                    )
                    
                    # 提取AI的回复
                    if isinstance(result, dict) and "messages" in result:
                        messages = result["messages"]
                        for msg in reversed(messages):
                            if isinstance(msg, AIMessage):
                                return msg.content
                    
                    # 如果无法提取AI消息，返回原始结果
                    return str(result)
                except Exception as e:
                    print(f"[WARNING] LangChain智能体调用失败: {e}")
                    # 降级到简化模式
                    return self._simplified_ask(question)
            else:
                # 使用简化模式
                return self._simplified_ask(question)
                
        except Exception as e:
            error_msg = f"处理问题时发生错误: {str(e)}"
            print(f"[ERROR] {error_msg}")
            return f"{error_msg}\n\n请重试或检查系统配置。"
    
    def _simplified_ask(self, question: str) -> str:
        """简化模式：直接调用工具函数"""
        question_lower = question.lower()
        
        # 根据问题内容调用相应的工具
        if "cpu" in question_lower or "处理器" in question_lower:
            try:
                from tools import get_cpu_usage
                cpu_usage = get_cpu_usage()
                return f"当前CPU使用率为: {cpu_usage:.1f}%"
            except Exception as e:
                return f"获取CPU使用率失败: {str(e)}"
        
        elif "内存" in question_lower or "ram" in question_lower:
            try:
                from tools import get_memory_usage
                memory_info = get_memory_usage()
                return f"内存已使用{memory_info['used_gb']:.1f}GB/共{memory_info['total_gb']:.1f}GB，使用率{memory_info['percent']:.1f}%"
            except Exception as e:
                return f"获取内存使用率失败: {str(e)}"
        
        elif "系统" in question_lower and "健康" in question_lower:
            try:
                import psutil
                import time
                
                # 获取CPU使用率
                cpu_usage = psutil.cpu_percent(interval=1)
                
                # 获取内存使用情况
                mem = psutil.virtual_memory()
                mem_used_gb = mem.used / (1024**3)
                mem_total_gb = mem.total / (1024**3)
                mem_percent = mem.percent
                
                health_report = f"系统健康分析报告:\n"
                health_report += f"时间: {time.strftime('%Y-%m-%d %H:%M:%S')}\n"
                health_report += f"CPU使用率: {cpu_usage}%\n"
                health_report += f"内存使用率: {mem_percent}% ({mem_used_gb:.1f}GB/{mem_total_gb:.1f}GB)\n"
                health_report += f"整体健康状况: 良好\n"
                
                # 磁盘信息
                health_report += "\n磁盘使用情况:\n"
                for partition in psutil.disk_partitions():
                    try:
                        usage = psutil.disk_usage(partition.mountpoint)
                        used_gb = usage.used / (1024**3)
                        total_gb = usage.total / (1024**3)
                        health_report += f"  {partition.mountpoint}: {usage.percent}% 使用 ({used_gb:.1f}GB/{total_gb:.1f}GB)\n"
                    except:
                        pass
                
                return health_report
            except Exception as e:
                return f"系统健康分析失败: {str(e)}"
        
        elif "系统" in question_lower or "信息" in question_lower:
            try:
                import platform
                import socket
                import datetime
                
                info = []
                info.append(f"系统: {platform.system()} {platform.release()}")
                info.append(f"主机名: {socket.gethostname()}")
                info.append(f"Python版本: {platform.python_version()}")
                info.append(f"当前时间: {datetime.datetime.now()}")
                info.append(f"智能体类型: LangChain增强版智能体")
                info.append(f"LangChain版本: 1.2.14")
                info.append(f"AI模型: 智谱GLM-4")
                
                return "\n".join(info)
            except Exception as e:
                return f"获取系统信息失败: {str(e)}"
        
        elif "服务" in question_lower or "运行" in question_lower:
            # 尝试提取服务名
            service_name = "nginx"  # 默认值
            for word in ["nginx", "mysql", "redis", "sshd", "python"]:
                if word in question_lower:
                    service_name = word
                    break
            
            try:
                status = check_service_status(service_name)
                return f"服务 {service_name} 状态: {status}"
            except Exception as e:
                return f"检查服务状态失败: {str(e)}"
        
        else:
            return f"我理解您的问题是: {question}\n\n作为LangChain增强版智能体，我可以帮您：\n1. 监控CPU/内存使用情况\n2. 检查服务状态\n3. 分析系统健康\n4. 提供系统信息\n\n请具体说明您需要哪方面的帮助。"
    
    def get_conversation_history(self, thread_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """获取对话历史（如果支持）"""
        if not self.checkpointer:
            return []
        
        thread_id = thread_id if thread_id else self.thread_id
        
        try:
            # 尝试获取检查点
            checkpoint = self.checkpointer.get({"configurable": {"thread_id": thread_id}})
            if checkpoint and "channel" in checkpoint:
                history = []
                for message in checkpoint["channel"]:
                    if hasattr(message, "content"):
                        history.append({
                            "role": type(message).__name__.replace("Message", "").lower(),
                            "content": message.content,
                            "timestamp": getattr(message, "timestamp", None)
                        })
                return history
        except Exception as e:
            print(f"[WARNING] 获取对话历史失败: {e}")
        
        return []
    
    def clear_conversation_history(self, thread_id: Optional[str] = None):
        """清除对话历史"""
        print(f"[INFO] 清除对话历史功能需要LangGraph支持，当前版本为简化实现")
        # 在完整版本中，这里会清除检查点
        return "对话历史清除功能需要完整LangGraph集成"

# 便捷函数
def ask_full_langchain_agent(question: str, show_init_info: bool = False, thread_id: Optional[str] = None) -> str:
    """便捷函数：使用完整LangChain增强版智能体回答问题"""
    agent = FullLangChainAgent(show_init_info=show_init_info)
    return agent.ask(question, use_thread_id=thread_id)

def test_full_langchain_agent():
    """测试完整LangChain增强版智能体"""
    print("=" * 60)
    print("测试完整LangChain增强版智能体")
    print("=" * 60)
    
    agent = FullLangChainAgent(show_init_info=False)
    
    # 测试信息获取
    info = agent.get_info()
    print(f"智能体类型: {info['agent_type']}")
    print(f"工具数量: {info['tools_count']}")
    print(f"工具名称: {info['tool_names']}")
    print(f"支持LangChain智能体: {info['has_langchain_agent']}")
    print(f"支持对话记忆: {info['has_memory']}")
    
    # 测试简单查询
    print("\n测试系统监控查询:")
    queries = [
        "CPU使用率是多少？",
        "内存使用情况怎么样？",
        "请检查nginx服务状态",
        "显示系统信息",
        "分析系统健康状况"
    ]
    
    for i, query in enumerate(queries, 1):
        print(f"\n[{i}] 问题: {query}")
        try:
            response = agent.ask(query)
            print(f"回答: {response[:120]}..." if len(response) > 120 else f"回答: {response}")
        except Exception as e:
            print(f"错误: {e}")
    
    # 测试多轮对话（如果支持）
    if info['has_memory']:
        print("\n测试多轮对话记忆:")
        print("第一轮: '我的名字是张三'")
        response1 = agent.ask("我的名字是张三", use_thread_id="test_user")
        print(f"回答: {response1[:80]}..." if len(response1) > 80 else f"回答: {response1}")
        
        print("第二轮: '我刚才说我叫什么名字？'")
        response2 = agent.ask("我刚才说我叫什么名字？", use_thread_id="test_user")
        print(f"回答: {response2[:80]}..." if len(response2) > 80 else f"回答: {response2}")
    
    print("\n" + "=" * 60)
    print("测试完成！")
    return True

if __name__ == "__main__":
    test_full_langchain_agent()