"""
MechForge Web - FastAPI Web Server

提供:
- RESTful API
- WebSocket 实时通信
- 静态文件服务
- 三种模式: AI Chat / Knowledge / CAE Workbench
- 安全防护: 限流、认证、输入验证
"""

import asyncio
import uuid
from contextlib import asynccontextmanager
from datetime import datetime
from pathlib import Path
from typing import Any

from fastapi import Depends, FastAPI, HTTPException, Query, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field

# 导入 MechForge 核心组件
try:
    from mechforge_ai.llm_client import LLMClient  # noqa: F401
    from mechforge_ai.rag_engine import RAGEngine
    from mechforge_core import get_config, get_database, get_logger
    from mechforge_core.security import RateLimitConfig
    from mechforge_work.cae_core import CAEEngine
except ImportError as e:
    print(f"Warning: Some components not available: {e}")

# 导入安全中间件和依赖
try:
    from mechforge_web.dependencies import (
        get_current_user,
        rate_limit,
        require_auth,
        require_scopes,
    )
    from mechforge_web.middleware import setup_security_middleware
except ImportError:
    setup_security_middleware = None
    get_current_user = None

logger = get_logger("web.main")

# 全局状态
app_state = {
    "llm_client": None,
    "rag_engine": None,
    "cae_engine": None,
    "connections": {},
    "chat_histories": {},
}


# ==================== Pydantic Models ====================


class ChatMessage(BaseModel):
    """聊天消息"""

    role: str = Field(..., description="消息角色: user/assistant/system")
    content: str = Field(..., description="消息内容")
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())
    metadata: dict[str, Any] = Field(default_factory=dict)


class ChatRequest(BaseModel):
    """聊天请求"""

    message: str = Field(..., description="用户消息")
    session_id: str | None = Field(None, description="会话ID")
    use_rag: bool = Field(True, description="是否使用RAG")
    stream: bool = Field(True, description="是否流式输出")


class ChatResponse(BaseModel):
    """聊天响应"""

    message: ChatMessage
    session_id: str
    rag_context: str | None = None


class CAEStatus(BaseModel):
    """CAE 状态"""

    geometry_loaded: bool = False
    mesh_generated: bool = False
    num_nodes: int = 0
    num_elements: int = 0
    solved: bool = False
    max_displacement: float = 0.0
    max_stress: float = 0.0


class CAEJob(BaseModel):
    """CAE 任务"""

    job_type: str = Field(..., description="任务类型: mesh/solve/export")
    params: dict[str, Any] = Field(default_factory=dict)
    status: str = "pending"
    result: str | None = None


# ==================== FastAPI App ====================


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时初始化
    print("[START] MechForge Web starting...")

    _config = get_config()

    # 初始化 LLM
    try:
        app_state["llm_client"] = LLMClient()
        print("[OK] LLM client initialized")
    except Exception as e:
        print(f"[ERROR] LLM client init failed: {e}")

    # 初始化 RAG
    try:
        app_state["rag_engine"] = RAGEngine()
        if app_state["rag_engine"].is_available:
            print(f"[OK] RAG engine initialized ({app_state['rag_engine'].doc_count} docs)")
        else:
            print("[WARN] RAG knowledge base not found")
    except Exception as e:
        print(f"[ERROR] RAG engine init failed: {e}")

    # 初始化 CAE
    try:
        app_state["cae_engine"] = CAEEngine()
        print("[OK] CAE engine initialized")
    except Exception as e:
        print(f"[ERROR] CAE engine init failed: {e}")

    yield

    # 关闭时清理
    print("[STOP] MechForge Web shutting down...")
    app_state.clear()


app = FastAPI(
    title="MechForge Web API",
    description="机械设计 AI 工作台 Web API - 包含安全防护",
    version="0.5.0",
    lifespan=lifespan,
)

# 设置安全中间件
if setup_security_middleware:
    setup_security_middleware(
        app,
        rate_limit_config=RateLimitConfig(
            requests_per_minute=120,
            burst_size=20,
        ),
        enable_cors=True,
        cors_origins=["http://localhost:8765", "http://127.0.0.1:8765", "http://localhost:8080", "http://127.0.0.1:8080"],
    )
    logger.info("Security middleware enabled")
else:
    logger.warning("Security middleware not available")

# 静态文件和模板
templates_dir = Path(__file__).parent / "templates"
static_dir = Path(__file__).parent / "static"

if templates_dir.exists():
    templates = Jinja2Templates(directory=str(templates_dir))

if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")


# ==================== WebSocket 管理 ====================


class ConnectionManager:
    """WebSocket 连接管理器"""

    def __init__(self):
        self.active_connections: dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket, client_id: str):
        await websocket.accept()
        self.active_connections[client_id] = websocket
        print(f"WebSocket 连接: {client_id}")

    def disconnect(self, client_id: str):
        if client_id in self.active_connections:
            del self.active_connections[client_id]
            print(f"WebSocket 断开: {client_id}")

    async def send_message(self, client_id: str, message: dict):
        if client_id in self.active_connections:
            await self.active_connections[client_id].send_json(message)

    async def broadcast(self, message: dict):
        for connection in self.active_connections.values():
            await connection.send_json(message)


manager = ConnectionManager()


# ==================== 页面路由 ====================


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """主页"""
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/chat", response_class=HTMLResponse)
async def chat_page(request: Request):
    """AI 对话页面"""
    return templates.TemplateResponse("chat.html", {"request": request})


@app.get("/knowledge", response_class=HTMLResponse)
async def knowledge_page(request: Request):
    """知识库页面"""
    return templates.TemplateResponse("knowledge.html", {"request": request})


@app.get("/cae", response_class=HTMLResponse)
async def cae_page(request: Request):
    """CAE 工作台页面"""
    return templates.TemplateResponse("cae.html", {"request": request})


# ==================== API 路由 ====================


@app.get("/api/health")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "version": "0.4.0",
        "components": {
            "llm": app_state["llm_client"] is not None,
            "rag": app_state["rag_engine"] is not None and app_state["rag_engine"].is_available,
            "cae": app_state["cae_engine"] is not None,
        },
    }


@app.get("/api/config")
async def get_configuration():
    """获取配置"""
    config = get_config()
    return {
        "provider": config.provider.get_active_provider(),
        "model": (
            config.provider.get_config().model
            if hasattr(config.provider.get_config(), "model")
            else "unknown"
        ),
        "rag_enabled": config.knowledge.rag.enabled,
        "theme": config.ui.theme,
    }


# ==================== 聊天 API ====================


@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """非流式聊天"""
    llm = app_state.get("llm_client")
    if not llm:
        raise HTTPException(status_code=503, detail="LLM 服务不可用")

    session_id = request.session_id or str(uuid.uuid4())

    # RAG 检索
    context = ""
    if request.use_rag and app_state.get("rag_engine"):
        rag = app_state["rag_engine"]
        if rag.is_available and rag.check_trigger(request.message):
            context = rag.search(request.message)

    # 调用 LLM
    try:
        response_content = llm.call(request.message, context, stream=False)

        message = ChatMessage(role="assistant", content=response_content)

        # 保存历史
        if session_id not in app_state["chat_histories"]:
            app_state["chat_histories"][session_id] = []
        app_state["chat_histories"][session_id].append({"role": "user", "content": request.message})
        app_state["chat_histories"][session_id].append(
            {"role": "assistant", "content": response_content}
        )

        return ChatResponse(
            message=message,
            session_id=session_id,
            rag_context=context if context else None,
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@app.websocket("/ws/chat/{client_id}")
async def websocket_chat(websocket: WebSocket, client_id: str):
    """WebSocket 流式聊天"""
    await manager.connect(websocket, client_id)

    llm = app_state.get("llm_client")
    rag = app_state.get("rag_engine")

    try:
        while True:
            # 接收消息
            data = await websocket.receive_json()
            message = data.get("message", "")
            use_rag = data.get("use_rag", True)
            session_id = data.get("session_id", client_id)

            # RAG 检索
            context = ""
            if use_rag and rag and rag.is_available and rag.check_trigger(message):
                await manager.send_message(
                    client_id, {"type": "status", "content": "🔍 检索知识库..."}
                )
                context = rag.search(message)

            # 流式生成
            await manager.send_message(client_id, {"type": "start", "content": ""})

            try:
                # 使用流式生成
                full_response = ""
                for chunk in llm.call(message, context, stream=True):
                    full_response += chunk
                    await manager.send_message(client_id, {"type": "chunk", "content": chunk})
                    await asyncio.sleep(0.01)  # 控制流速

                await manager.send_message(
                    client_id,
                    {
                        "type": "end",
                        "content": full_response,
                        "session_id": session_id,
                    },
                )

                # 保存历史
                if session_id not in app_state["chat_histories"]:
                    app_state["chat_histories"][session_id] = []
                app_state["chat_histories"][session_id].append({"role": "user", "content": message})
                app_state["chat_histories"][session_id].append(
                    {"role": "assistant", "content": full_response}
                )

            except Exception as e:
                await manager.send_message(client_id, {"type": "error", "content": str(e)})

    except WebSocketDisconnect:
        manager.disconnect(client_id)


@app.get("/api/chat/history/{session_id}")
async def get_chat_history(session_id: str):
    """获取聊天历史"""
    history = app_state["chat_histories"].get(session_id, [])
    return {"session_id": session_id, "messages": history}


@app.delete("/api/chat/history/{session_id}")
async def clear_chat_history(session_id: str):
    """清除聊天历史"""
    if session_id in app_state["chat_histories"]:
        del app_state["chat_histories"][session_id]
    return {"status": "ok"}


# ==================== 知识库 API ====================


@app.get("/api/knowledge/search")
async def search_knowledge(
    query: str = Query(..., description="搜索关键词"),
    top_k: int = Query(5, ge=1, le=20),
):
    """知识库搜索"""
    rag = app_state.get("rag_engine")
    if not rag or not rag.is_available:
        raise HTTPException(status_code=503, detail="知识库服务不可用")

    try:
        context = rag.search(query)
        return {"query": query, "results": context, "doc_count": rag.doc_count}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@app.get("/api/knowledge/status")
async def knowledge_status():
    """知识库状态"""
    rag = app_state.get("rag_engine")
    if not rag:
        return {"available": False, "doc_count": 0, "path": None}

    return {
        "available": rag.is_available,
        "doc_count": rag.doc_count,
        "path": str(rag.knowledge_path) if rag.knowledge_path else None,
    }


@app.post("/api/knowledge/reload")
async def reload_knowledge():
    """重新加载知识库"""
    rag = app_state.get("rag_engine")
    if not rag:
        raise HTTPException(status_code=503, detail="知识库服务不可用")

    try:
        rag.reload()
        return {"status": "ok", "doc_count": rag.doc_count}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


# ==================== CAE API ====================


@app.get("/api/cae/status", response_model=CAEStatus)
async def cae_status():
    """CAE 状态"""
    engine = app_state.get("cae_engine")
    if not engine:
        return CAEStatus()

    status = engine.get_status()
    return CAEStatus(
        geometry_loaded=status.get("geometry_loaded", False),
        mesh_generated=status.get("mesh_generated", False),
        num_nodes=engine.mesh.num_nodes if engine.mesh else 0,
        num_elements=engine.mesh.num_elements if engine.mesh else 0,
        solved=status.get("solved", False),
        max_displacement=engine.result.max_displacement if engine.result else 0.0,
        max_stress=engine.result.max_von_mises if engine.result else 0.0,
    )


@app.post("/api/cae/demo")
async def cae_demo():
    """运行 CAE 示例"""
    engine = app_state.get("cae_engine")
    if not engine:
        raise HTTPException(status_code=503, detail="CAE 服务不可用")

    try:
        # 创建悬臂梁示例
        engine.setup_cantilever_beam(
            length=100.0,
            width=10.0,
            height=10.0,
            mesh_size=2.0,
            force=1000.0,
        )

        # 生成网格
        engine.generate_mesh(mesh_size=2.0)

        # 求解
        result = engine.solve()

        if result.success:
            return {
                "status": "success",
                "message": "分析完成",
                "max_displacement": result.max_displacement,
                "max_stress": result.max_von_mises,
            }
        else:
            return {"status": "error", "message": result.message}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@app.post("/api/cae/mesh")
async def cae_mesh(params: dict):
    """生成网格"""
    engine = app_state.get("cae_engine")
    if not engine:
        raise HTTPException(status_code=503, detail="CAE 服务不可用")

    try:
        mesh_size = params.get("size", 5.0)
        mesh = engine.generate_mesh(mesh_size=mesh_size)

        return {
            "status": "success",
            "nodes": mesh.num_nodes,
            "elements": mesh.num_elements,
            "type": mesh.element_type,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@app.post("/api/cae/solve")
async def cae_solve(params: dict):
    """执行求解"""
    engine = app_state.get("cae_engine")
    if not engine:
        raise HTTPException(status_code=503, detail="CAE 服务不可用")

    try:
        result = engine.solve()

        if result.success:
            return {
                "status": "success",
                "max_displacement": result.max_displacement,
                "max_stress": result.max_von_mises,
            }
        else:
            return {"status": "error", "message": result.message}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@app.get("/api/cae/visualization")
async def cae_visualization():
    """获取可视化数据"""
    engine = app_state.get("cae_engine")
    if not engine or not engine.mesh:
        raise HTTPException(status_code=404, detail="无网格数据")

    # 返回网格数据用于前端可视化
    mesh = engine.mesh
    return {
        "nodes": mesh.nodes.tolist() if mesh.nodes is not None else [],
        "elements": mesh.elements.tolist() if mesh.elements is not None else [],
        "element_type": mesh.element_type,
    }


# ==================== 安全 API ====================


@app.get("/api/auth/token", tags=["Security"])
async def generate_token(
    user_id: str,
    expires_in: int = 3600,
    _: None = Depends(rate_limit(5)),  # 每分钟最多5次
):
    """
    生成 API Token

    生产环境应该添加更多验证(如密码、OAuth等)
    """
    from mechforge_core.security import APITokenManager

    token_manager = APITokenManager()
    token = token_manager.generate_token(
        user_id=user_id,
        expires_in=expires_in,
        scopes=["read", "write"],
    )

    logger.info(f"Token generated for user: {user_id}")

    return {
        "token": token,
        "expires_in": expires_in,
        "token_type": "Bearer",
    }


@app.get("/api/auth/verify", tags=["Security"])
async def verify_token(user: dict = Depends(require_auth)):
    """验证 Token 有效性"""
    return {
        "valid": True,
        "user_id": user.get("user_id"),
        "scopes": user.get("scopes"),
        "expires_at": user.get("expires_at"),
    }


@app.get("/api/security/stats", tags=["Security"])
async def security_stats(user: dict = Depends(require_auth)):
    """获取安全统计信息"""
    from mechforge_core import get_cache

    cache = get_cache()
    cache_stats = cache.stats()

    return {
        "cache": {
            "hits": cache_stats.hits,
            "misses": cache_stats.misses,
            "hit_rate": cache_stats.hit_rate,
            "total_entries": cache_stats.total_entries,
        },
        "timestamp": datetime.now().isoformat(),
    }


@app.post("/api/security/rate-limit/reset", tags=["Security"])
async def reset_rate_limit(
    key: str,
    user: dict = Depends(require_auth),
    _: bool = Depends(require_scopes(["admin"])),
):
    """重置指定键的速率限制 (需要 admin 权限)"""
    from mechforge_core import get_security_middleware

    middleware = get_security_middleware()
    middleware.rate_limiter.reset(key)

    logger.info(f"Rate limit reset for key: {key} by user: {user['user_id']}")

    return {"status": "ok", "message": f"Rate limit reset for {key}"}


# ==================== 用户 API ====================


@app.get("/api/user/profile", tags=["User"])
async def get_profile(user: dict = Depends(require_auth)):
    """获取用户资料"""
    return {
        "user_id": user.get("user_id"),
        "scopes": user.get("scopes"),
    }


@app.get("/api/user/sessions", tags=["User"])
async def get_user_sessions(
    user: dict = Depends(require_auth),
    limit: int = Query(50, ge=1, le=100),
):
    """获取用户的会话列表"""
    db = get_database()
    sessions = db.get_all_sessions(limit=limit)

    return {
        "sessions": sessions,
        "total": len(sessions),
    }


# ==================== 启动入口 ====================


def main():
    """启动 Web 服务器"""
    import argparse

    import uvicorn

    parser = argparse.ArgumentParser(description="MechForge Web Server")
    parser.add_argument("--host", default="127.0.0.1", help="绑定地址")
    parser.add_argument("--port", type=int, default=8765, help="端口号 (默认: 8765)")
    parser.add_argument("--reload", action="store_true", help="开发模式热重载")
    args = parser.parse_args()

    print(f"""
    ===========================================

       MechForge Web Server

       Visit: http://{args.host}:{args.port}
       API Docs: http://{args.host}:{args.port}/docs

    ===========================================
    """)

    uvicorn.run(
        "mechforge_web.main:app",
        host=args.host,
        port=args.port,
        reload=args.reload,
    )


if __name__ == "__main__":
    main()
