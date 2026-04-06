#!/usr/bin/env python3
"""
OpenCALW集成示例
展示如何将高级自动化运维工具集成到智能运维助手中
"""

import os
import sys
from typing import Dict, Any, List, Optional
import subprocess
import json
import time
from dataclasses import dataclass
from enum import Enum

# 添加backend目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

# 模拟OpenCALW功能（实际项目中会导入真实库）
class OpenCALWSimulator:
    """
    OpenCALW模拟器
    在实际项目中，这里会导入真实的OpenCALW库
    """
    
    class OperationType(Enum):
        """操作类型枚举"""
        FILE_OPERATION = "file_operation"
        PROCESS_MANAGEMENT = "process_management"
        NETWORK_CONFIG = "network_config"
        SECURITY_CHECK = "security_check"
        BACKUP_RESTORE = "backup_restore"
    
    @dataclass
    class OperationResult:
        """操作结果"""
        success: bool
        message: str
        data: Optional[Dict[str, Any]] = None
        execution_time: float = 0.0
    
    def __init__(self):
        self.operations_log = []
    
    def execute_operation(self, operation_type: OperationType, params: Dict[str, Any]) -> OperationResult:
        """执行OpenCALW操作"""
        start_time = time.time()
        
        try:
            if operation_type == self.OperationType.FILE_OPERATION:
                result = self._file_operation(params)
            elif operation_type == self.OperationType.PROCESS_MANAGEMENT:
                result = self._process_management(params)
            elif operation_type == self.OperationType.NETWORK_CONFIG:
                result = self._network_config(params)
            elif operation_type == self.OperationType.SECURITY_CHECK:
                result = self._security_check(params)
            elif operation_type == self.OperationType.BACKUP_RESTORE:
                result = self._backup_restore(params)
            else:
                result = self.OperationResult(
                    success=False,
                    message=f"未知操作类型: {operation_type}"
                )
            
            # 记录操作
            self.operations_log.append({
                "timestamp": time.time(),
                "operation": operation_type.value,
                "params": params,
                "result": result.success,
                "message": result.message
            })
            
            result.execution_time = time.time() - start_time
            return result
            
        except Exception as e:
            execution_time = time.time() - start_time
            return self.OperationResult(
                success=False,
                message=f"操作执行失败: {str(e)}",
                execution_time=execution_time
            )
    
    def _file_operation(self, params: Dict[str, Any]) -> OperationResult:
        """文件操作"""
        action = params.get("action", "")
        path = params.get("path", "")
        
        if action == "list":
            try:
                import os
                files = os.listdir(path)
                return self.OperationResult(
                    success=True,
                    message=f"列出目录 {path} 成功",
                    data={"files": files, "count": len(files)}
                )
            except Exception as e:
                return self.OperationResult(
                    success=False,
                    message=f"列出目录失败: {str(e)}"
                )
        
        elif action == "clean":
            # 模拟清理操作
            return self.OperationResult(
                success=True,
                message=f"清理 {path} 完成，释放了约 500MB 空间",
                data={"space_freed_mb": 500}
            )
        
        else:
            return self.OperationResult(
                success=False,
                message=f"不支持的文件操作: {action}"
            )
    
    def _process_management(self, params: Dict[str, Any]) -> OperationResult:
        """进程管理"""
        action = params.get("action", "")
        process_name = params.get("process_name", "")
        
        if action == "list":
            try:
                import psutil
                processes = []
                for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
                    try:
                        processes.append(proc.info)
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        pass
                
                return self.OperationResult(
                    success=True,
                    message="获取进程列表成功",
                    data={"processes": processes[:10], "total": len(processes)}  # 只返回前10个
                )
            except Exception as e:
                return self.OperationResult(
                    success=False,
                    message=f"获取进程列表失败: {str(e)}"
                )
        
        elif action == "restart":
            # 模拟重启进程
            return self.OperationResult(
                success=True,
                message=f"重启进程 {process_name} 成功",
                data={"process": process_name, "status": "restarted"}
            )
        
        else:
            return self.OperationResult(
                success=False,
                message=f"不支持的进程操作: {action}"
            )
    
    def _network_config(self, params: Dict[str, Any]) -> OperationResult:
        """网络配置"""
        action = params.get("action", "")
        
        if action == "check":
            try:
                import socket
                import psutil
                
                # 获取网络信息
                net_io = psutil.net_io_counters()
                addrs = psutil.net_if_addrs()
                
                return self.OperationResult(
                    success=True,
                    message="网络检查完成",
                    data={
                        "bytes_sent": net_io.bytes_sent,
                        "bytes_recv": net_io.bytes_recv,
                        "interfaces": len(addrs),
                        "hostname": socket.gethostname()
                    }
                )
            except Exception as e:
                return self.OperationResult(
                    success=False,
                    message=f"网络检查失败: {str(e)}"
                )
        
        else:
            return self.OperationResult(
                success=False,
                message=f"不支持的网络操作: {action}"
            )
    
    def _security_check(self, params: Dict[str, Any]) -> OperationResult:
        """安全检查"""
        # 模拟安全检查
        checks = [
            {"name": "防火墙状态", "status": "正常", "risk": "低"},
            {"name": "SSH配置", "status": "正常", "risk": "低"},
            {"name": "用户权限", "status": "警告", "risk": "中", "details": "存在普通用户拥有sudo权限"},
            {"name": "系统更新", "status": "异常", "risk": "高", "details": "100个安全更新未安装"},
        ]
        
        return self.OperationResult(
            success=True,
            message="安全检查完成",
            data={
                "checks": checks,
                "total_checks": len(checks),
                "high_risk_count": sum(1 for c in checks if c["risk"] == "高"),
                "medium_risk_count": sum(1 for c in checks if c["risk"] == "中"),
                "low_risk_count": sum(1 for c in checks if c["risk"] == "低"),
            }
        )
    
    def _backup_restore(self, params: Dict[str, Any]) -> OperationResult:
        """备份恢复"""
        action = params.get("action", "")
        target = params.get("target", "")
        
        if action == "backup":
            # 模拟备份
            backup_id = f"backup_{int(time.time())}"
            return self.OperationResult(
                success=True,
                message=f"备份 {target} 成功",
                data={
                    "backup_id": backup_id,
                    "target": target,
                    "timestamp": time.time(),
                    "size_mb": 250
                }
            )
        
        elif action == "restore":
            # 模拟恢复
            return self.OperationResult(
                success=True,
                message=f"恢复 {target} 成功",
                data={
                    "target": target,
                    "restored_files": 42,
                    "duration_seconds": 15.3
                }
            )
        
        else:
            return self.OperationResult(
                success=False,
                message=f"不支持的备份操作: {action}"
            )
    
    def get_logs(self, limit: int = 10) -> List[Dict[str, Any]]:
        """获取操作日志"""
        return self.operations_log[-limit:] if self.operations_log else []


class OpenCALWIntegration:
    """
    OpenCALW集成类
    将OpenCALW功能包装成智能运维助手的工具
    """
    
    def __init__(self):
        self.opencalw = OpenCALWSimulator()
        self.tools = self._create_tools()
    
    def _create_tools(self) -> List[Dict[str, Any]]:
        """创建OpenCALW工具列表"""
        return [
            {
                "name": "opencalw_file_operation",
                "func": self.file_operation,
                "description": "执行文件操作，如列出目录、清理空间等。参数示例: {'action': 'list', 'path': '/var/log'} 或 {'action': 'clean', 'path': '/tmp'}"
            },
            {
                "name": "opencalw_process_management", 
                "func": self.process_management,
                "description": "管理进程，如列出所有进程、重启进程等。参数示例: {'action': 'list'} 或 {'action': 'restart', 'process_name': 'nginx'}"
            },
            {
                "name": "opencalw_network_config",
                "func": self.network_config,
                "description": "网络配置和检查。参数示例: {'action': 'check'}"
            },
            {
                "name": "opencalw_security_check",
                "func": self.security_check,
                "description": "执行系统安全检查。参数示例: {'action': 'check'}"
            },
            {
                "name": "opencalw_backup_restore",
                "func": self.backup_restore,
                "description": "备份和恢复操作。参数示例: {'action': 'backup', 'target': '/home'} 或 {'action': 'restore', 'target': 'backup_1234567890'}"
            },
            {
                "name": "opencalw_get_logs",
                "func": self.get_logs,
                "description": "获取OpenCALW操作日志。参数示例: {'limit': 5}"
            }
        ]
    
    def file_operation(self, params: Dict[str, Any]) -> str:
        """文件操作工具"""
        result = self.opencalw.execute_operation(
            OpenCALWSimulator.OperationType.FILE_OPERATION,
            params
        )
        return self._format_result(result)
    
    def process_management(self, params: Dict[str, Any]) -> str:
        """进程管理工具"""
        result = self.opencalw.execute_operation(
            OpenCALWSimulator.OperationType.PROCESS_MANAGEMENT,
            params
        )
        return self._format_result(result)
    
    def network_config(self, params: Dict[str, Any]) -> str:
        """网络配置工具"""
        result = self.opencalw.execute_operation(
            OpenCALWSimulator.OperationType.NETWORK_CONFIG,
            params
        )
        return self._format_result(result)
    
    def security_check(self, params: Dict[str, Any]) -> str:
        """安全检查工具"""
        result = self.opencalw.execute_operation(
            OpenCALWSimulator.OperationType.SECURITY_CHECK,
            params
        )
        return self._format_result(result)
    
    def backup_restore(self, params: Dict[str, Any]) -> str:
        """备份恢复工具"""
        result = self.opencalw.execute_operation(
            OpenCALWSimulator.OperationType.BACKUP_RESTORE,
            params
        )
        return self._format_result(result)
    
    def get_logs(self, params: Dict[str, Any]) -> str:
        """获取日志工具"""
        limit = params.get("limit", 5)
        logs = self.opencalw.get_logs(limit)
        
        if not logs:
            return "暂无操作日志"
        
        log_text = f"最近 {len(logs)} 条OpenCALW操作日志:\n"
        for log in logs:
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(log["timestamp"]))
            log_text += f"\n[{timestamp}] {log['operation']}: {log['message']} (成功: {log['result']})"
        
        return log_text
    
    def _format_result(self, result: OpenCALWSimulator.OperationResult) -> str:
        """格式化操作结果"""
        if result.success:
            message = f"✅ {result.message}"
            if result.data:
                # 简化数据展示
                data_str = json.dumps(result.data, ensure_ascii=False, indent=2)
                if len(data_str) > 200:
                    data_str = data_str[:200] + "..."
                message += f"\n📊 数据: {data_str}"
        else:
            message = f"❌ {result.message}"
        
        message += f"\n⏱️ 执行时间: {result.execution_time:.2f}秒"
        
        return message
    
    def get_tool_names(self) -> List[str]:
        """获取工具名称列表"""
        return [tool["name"] for tool in self.tools]
    
    def get_tools(self) -> List[Dict[str, Any]]:
        """获取所有工具"""
        return self.tools


# 集成测试
def test_opencalw_integration():
    """测试OpenCALW集成"""
    print("=" * 60)
    print("🔧 OpenCALW集成测试")
    print("=" * 60)
    
    integration = OpenCALWIntegration()
    
    print(f"可用工具: {', '.join(integration.get_tool_names())}")
    print()
    
    # 测试各个工具
    test_cases = [
        ("opencalw_file_operation", {"action": "list", "path": "/tmp"}),
        ("opencalw_process_management", {"action": "list"}),
        ("opencalw_network_config", {"action": "check"}),
        ("opencalw_security_check", {"action": "check"}),
        ("opencalw_backup_restore", {"action": "backup", "target": "/home/user"}),
        ("opencalw_get_logs", {"limit": 3}),
    ]
    
    for tool_name, params in test_cases:
        print(f"测试: {tool_name}")
        print(f"参数: {params}")
        
        # 找到对应的工具函数
        tool_func = None
        for tool in integration.tools:
            if tool["name"] == tool_name:
                tool_func = tool["func"]
                break
        
        if tool_func:
            try:
                result = tool_func(params)
                print(f"结果: {result[:200]}..." if len(result) > 200 else f"结果: {result}")
            except Exception as e:
                print(f"❌ 执行失败: {e}")
        else:
            print(f"❌ 未找到工具: {tool_name}")
        
        print("-" * 40)
    
    print("✅ OpenCALW集成测试完成")


# 演示如何将OpenCALW集成到增强版智能体中
def demonstrate_agent_integration():
    """演示智能体集成"""
    print("\n" + "=" * 60)
    print("🤖 智能体集成演示")
    print("=" * 60)
    
    # 创建OpenCALW集成实例
    opencalw = OpenCALWIntegration()
    
    # 演示如何将工具添加到LangChain智能体
    print("以下是如何将OpenCALW工具集成到增强版智能体中:")
    print()
    
    print("1. 在 agent_enhanced.py 中添加:")
    print("""
    # 导入OpenCALW集成
    from opencalw_integration import OpenCALWIntegration
    
    class EnhancedZhipuAIAgent:
        def __init__(self, show_init_info: bool = True):
            # ... 初始化代码 ...
            
            # 创建OpenCALW集成
            self.opencalw = OpenCALWIntegration()
            
            # 将OpenCALW工具添加到工具列表中
            self._add_opencalw_tools()
    """)
    
    print("\n2. 添加OpenCALW工具的方法:")
    print("""
    def _add_opencalw_tools(self):
        \"""添加OpenCALW工具\"""
        for tool_info in self.opencalw.get_tools():
            tool = Tool(
                name=tool_info["name"],
                func=tool_info["func"],
                description=tool_info["description"]
            )
            self.tools.append(tool)
    """)
    
    print("\n3. 用户可以使用自然语言调用OpenCALW功能:")
    print("""
    用户: "清理一下/tmp目录"
    AI: 调用 opencalw_file_operation({'action': 'clean', 'path': '/tmp'})
    
    用户: "检查系统安全状态"
    AI: 调用 opencalw_security_check({'action': 'check'})
    
    用户: "备份我的home目录"
    AI: 调用 opencalw_backup_restore({'action': 'backup', 'target': '/home'})
    """)
    
    print("\n✅ 集成演示完成")


if __name__ == "__main__":
    # 运行测试
    test_opencalw_integration()
    
    # 运行集成演示
    demonstrate_agent_integration()
    
    print("\n" + "=" * 60)
    print("🎯 OpenCALW集成准备就绪")
    print("=" * 60)
    print("\n下一步:")
    print("1. 安装真实的OpenCALW库（如果可用）")
    print("2. 修改 agent_enhanced.py，集成OpenCALW工具")
    print("3. 测试自然语言调用自动化运维功能")
    print("4. 扩展更多高级运维工具")