"""
service_check.py - 跨平台服务检测工具（基于进程名）
适用于无法使用 systemctl 的环境（Windows/macOS 等）
"""

import psutil
from typing import Optional

def check_service_by_process_name(service_name: str, exact_match: bool = False) -> str:
    """
    基于进程名检查服务是否正在运行（适用于 Windows / macOS 等无 systemctl 的环境）。

    Args:
        service_name (str): 服务名称（例如 'nginx', 'python', 'mysql'）
        exact_match (bool): 是否精确匹配进程名，默认为 False（包含匹配）

    Returns:
        str: 格式为 "服务{service_name}正在运行" 或 "服务{service_name}未运行"
    """
    try:
        for proc in psutil.process_iter(['name']):
            try:
                proc_name = proc.info['name']
                if proc_name is None:
                    continue
                if exact_match:
                    if service_name.lower() == proc_name.lower():
                        return f"服务{service_name}正在运行"
                else:
                    if service_name.lower() in proc_name.lower():
                        return f"服务{service_name}正在运行"
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                # 跳过无法访问或已终止的进程
                continue
        return f"服务{service_name}未运行"
    except Exception as e:
        return f"检查服务{service_name}时出错: {str(e)}"


def check_service_by_pid(pid: int) -> Optional[str]:
    """
    根据进程ID检查服务是否存在并返回进程名（如有需要）

    Args:
        pid (int): 进程ID

    Returns:
        Optional[str]: 如果进程存在返回进程名，否则返回 None
    """
    if psutil.pid_exists(pid):
        try:
            proc = psutil.Process(pid)
            return proc.name()
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            return None
    return None


if __name__ == "__main__":
    # 简单测试
    print(check_service_by_process_name("python"))
    print(check_service_by_process_name("nonexist"))
