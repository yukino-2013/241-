#!/usr/bin/env python3
"""
智能运维助手 - 工具函数模块
提供CPU、内存、服务状态查询功能
"""

import psutil
import subprocess
import platform

def get_cpu_usage() -> float:
    """
    获取CPU使用率
    返回: CPU使用率百分比（浮点数）
    """
    try:
        # 获取CPU使用率，interval=1表示采样1秒
        usage = psutil.cpu_percent(interval=1)
        return float(usage)
    except Exception as e:
        raise Exception(f"获取CPU使用率时出错: {str(e)}")

def get_memory_usage() -> dict:
    """
    获取内存使用情况
    返回: 包含内存使用信息的字典
    """
    try:
        mem = psutil.virtual_memory()
        used_gb = mem.used / (1024**3)  # 转换为GB
        total_gb = mem.total / (1024**3)  # 转换为GB
        percent = mem.percent
        
        return {
            "used_gb": used_gb,
            "total_gb": total_gb,
            "percent": percent,
            "used": mem.used,
            "total": mem.total,
            "available": mem.available,
            "free": mem.free
        }
    except Exception as e:
        raise Exception(f"获取内存使用情况时出错: {str(e)}")

def check_service_status(service_name: str) -> str:
    """
    检查Linux系统服务状态
    参数: service_name - 服务名称，如 nginx, sshd, mysql
    返回格式: "服务{service_name}正在运行" 或 "服务{service_name}未运行"
    """
    try:
        # 检查操作系统类型
        system = platform.system()
        
        if system == "Linux":
            # Linux系统使用systemctl检查服务状态
            result = subprocess.run(
                ["systemctl", "is-active", service_name],
                capture_output=True, 
                text=True, 
                timeout=5
            )
            if result.returncode == 0 and result.stdout.strip() == "active":
                return f"服务 '{service_name}' 正在运行"
            else:
                return f"服务 '{service_name}' 未运行"
        else:
            # 非Linux系统使用进程名检查（备用方案）
            return check_service_by_process_name(service_name)
            
    except FileNotFoundError:
        # systemctl命令不存在，使用备用方案
        return check_service_by_process_name(service_name)
    except subprocess.TimeoutExpired:
        return f"检查服务 '{service_name}' 状态超时"
    except Exception as e:
        return f"检查服务 '{service_name}' 时出错: {str(e)}"

def check_service_by_process_name(service_name: str) -> str:
    """
    基于进程名检查服务（适用于Windows/Mac/Linux备选方案）
    返回格式: "服务{service_name}正在运行" 或 "服务{service_name}未运行"
    """
    try:
        service_found = False
        
        # 遍历所有进程，检查进程名是否包含服务名
        for proc in psutil.process_iter(['name']):
            try:
                proc_name = proc.info['name'].lower()
                if service_name.lower() in proc_name:
                    service_found = True
                    break
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        if service_found:
            return f"服务 '{service_name}' 正在运行（通过进程名检测）"
        else:
            return f"服务 '{service_name}' 未运行（未找到相关进程）"
            
    except Exception as e:
        return f"通过进程名检查服务 '{service_name}' 时出错: {str(e)}"

def test_tools():
    """
    测试所有工具函数
    """
    print("测试工具函数...\n")
    
    # 测试CPU使用率
    print("1. 测试CPU使用率:")
    cpu_result = get_cpu_usage()
    print(f"   {cpu_result}\n")
    
    # 测试内存使用率
    print("2. 测试内存使用情况:")
    mem_result = get_memory_usage()
    print(f"   {mem_result}\n")
    
    # 测试服务状态检查
    print("3. 测试服务状态检查:")
    
    # 测试常见的服务
    test_services = ["nginx", "sshd", "mysql", "redis"]
    for service in test_services:
        service_result = check_service_status(service)
        print(f"   {service}: {service_result}")
    
    print("\n工具函数测试完成！")

if __name__ == "__main__":
    # 直接运行此文件时进行测试
    test_tools()