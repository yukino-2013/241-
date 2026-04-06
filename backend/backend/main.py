#!/usr/bin/env python3
"""
智能运维助手 - LangChain增强版 API服务
基于LangChain 1.x + 智谱AI GLM-4，支持ReAct智能体、对话记忆、工具链
"""

import os
import sys
import time
import json
from typing import Dict, Any, Optional, List
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

# 确保能找到同目录下的模块
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 导入智能体
from agent import FullLangChainAgent, ask_full_langchain_agent

# 创建FastAPI应用
app = FastAPI(
    title="智能运维助手",
    description="基于LangChain 1.x + 智谱AI GLM-4 的智能运维助手，支持ReAct推理、多轮对话记忆、工具链管理",
    version="2.0.0"
)

# 允许跨域请求
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ──────────────────────────────────────────
# 数据模型
# ──────────────────────────────────────────
class ChatRequest(BaseModel):
    text: str
    thread_id: Optional[str] = None      # 指定会话线程，用于多轮记忆
    show_init_info: bool = False

class ChatResponse(BaseModel):
    response: str
    agent_type: str
    processing_time: float
    thread_id: Optional[str] = None

class AgentInfoResponse(BaseModel):
    agent_type: str
    version: str
    langchain_version: Optional[str] = None
    tools_count: int
    tool_names: List[str]
    has_memory: bool
    supports_react: bool = True
    supports_multiturn: bool = True

class SystemHealthResponse(BaseModel):
    timestamp: str
    cpu_usage: float
    memory_usage: float
    overall_health: str
    disk_usage: Dict[str, Dict[str, Any]]

# ──────────────────────────────────────────
# 全局智能体（单例）
# ──────────────────────────────────────────
agent: Optional[FullLangChainAgent] = None

@app.on_event("startup")
async def startup_event():
    global agent

    print("=" * 60)
    print("智能运维助手 v2.0 启动中...")
    print("=" * 60)

    try:
        agent = FullLangChainAgent(show_init_info=True)
        print("[OK] LangChain增强版智能体初始化完成")
    except Exception as e:
        print(f"[ERROR] 智能体初始化失败: {e}")
        agent = None

    print(f"[OK] API服务: http://localhost:8000")
    print(f"[OK] API文档: http://localhost:8000/docs")
    print("=" * 60)


# ──────────────────────────────────────────
# 接口路由
# ──────────────────────────────────────────
@app.get("/")
async def root():
    """服务根路径"""
    return {
        "service": "智能运维助手",
        "version": "2.0.0",
        "status": "运行中",
        "agent_ready": agent is not None,
        "endpoints": {
            "POST /chat": "与智能体对话（支持多轮记忆）",
            "GET /info":  "查看智能体信息",
            "GET /health": "系统健康检查",
            "GET /tools":  "可用工具列表",
            "GET /conversation/{thread_id}": "获取对话历史",
            "DELETE /conversation/{thread_id}": "清除对话历史",
        }
    }


@app.get("/info", response_model=AgentInfoResponse)
async def get_agent_info():
    """获取智能体详细信息"""
    if agent is None:
        raise HTTPException(status_code=503, detail="智能体未初始化，请检查API密钥配置")

    info = agent.get_info()

    langchain_version = None
    try:
        import langchain
        langchain_version = langchain.__version__
    except Exception:
        pass

    return AgentInfoResponse(
        agent_type=info["agent_type"],
        version="2.0.0",
        langchain_version=langchain_version,
        tools_count=info["tools_count"],
        tool_names=info["tool_names"],
        has_memory=info["has_memory"],
        supports_react=True,
        supports_multiturn=True
    )


@app.post("/chat", response_model=ChatResponse)
async def chat_with_agent(request: ChatRequest, background_tasks: BackgroundTasks = None):
    """
    与智能体对话
    - thread_id: 传入同一 thread_id 可延续多轮对话记忆
    """
    if agent is None:
        raise HTTPException(status_code=503, detail="智能体未初始化，请检查API密钥配置")

    if not request.text.strip():
        raise HTTPException(status_code=400, detail="问题不能为空")

    start_time = time.time()

    try:
        response_text = agent.ask(request.text, use_thread_id=request.thread_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"智能体处理失败: {e}")

    processing_time = round(time.time() - start_time, 3)

    if background_tasks:
        background_tasks.add_task(
            log_request, request.text, response_text[:100], processing_time
        )

    return ChatResponse(
        response=response_text,
        agent_type=agent.agent_type,
        processing_time=processing_time,
        thread_id=request.thread_id
    )


@app.get("/health", response_model=SystemHealthResponse)
async def check_system_health():
    """系统健康检查（直接读取系统数据）"""
    try:
        from tools import get_cpu_usage, get_memory_usage
        import psutil

        cpu_percent = get_cpu_usage()          # float
        memory_info = get_memory_usage()       # dict

        disk_usage = {}
        for partition in psutil.disk_partitions():
            try:
                u = psutil.disk_usage(partition.mountpoint)
                disk_usage[partition.mountpoint] = {
                    "total_gb": round(u.total / (1024 ** 3), 2),
                    "used_gb":  round(u.used  / (1024 ** 3), 2),
                    "free_gb":  round(u.free  / (1024 ** 3), 2),
                    "percent":  u.percent
                }
            except Exception:
                continue

        overall_health = "良好"
        if cpu_percent > 90 or memory_info["percent"] > 90:
            overall_health = "警告"
        elif cpu_percent > 80 or memory_info["percent"] > 80:
            overall_health = "注意"

        return SystemHealthResponse(
            timestamp=time.strftime("%Y-%m-%d %H:%M:%S"),
            cpu_usage=cpu_percent,
            memory_usage=memory_info["percent"],
            overall_health=overall_health,
            disk_usage=disk_usage
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取系统健康信息失败: {e}")


@app.get("/tools")
async def get_available_tools():
    """获取所有可用工具"""
    if agent is None:
        raise HTTPException(status_code=503, detail="智能体未初始化")

    info = agent.get_info()
    return {
        "total_tools": info["tools_count"],
        "tools": [
            {"name": name, "description": "LangChain智能体工具"}
            for name in info["tool_names"]
        ]
    }


@app.get("/conversation/{thread_id}")
async def get_conversation_history(thread_id: str):
    """获取指定会话的对话历史"""
    if agent is None:
        raise HTTPException(status_code=503, detail="智能体未初始化")
    try:
        history = agent.get_conversation_history(thread_id)
        return {"thread_id": thread_id, "history": history, "count": len(history)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取对话历史失败: {e}")


@app.delete("/conversation/{thread_id}")
async def clear_conversation_history(thread_id: str):
    """清除指定会话历史"""
    if agent is None:
        raise HTTPException(status_code=503, detail="智能体未初始化")
    result = agent.clear_conversation_history(thread_id)
    return {"thread_id": thread_id, "message": result, "status": "已处理"}


# ──────────────────────────────────────────
# 工具函数
# ──────────────────────────────────────────
def log_request(question: str, response_preview: str, processing_time: float):
    """后台记录请求日志"""
    entry = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "question": question[:100],
        "response_preview": response_preview,
        "processing_time": processing_time
    }
    print(f"[LOG] {json.dumps(entry, ensure_ascii=False)}")


if __name__ == "__main__":
    print("启动智能运维助手 API 服务...")
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info",
        access_log=True
    )
