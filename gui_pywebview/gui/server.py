"""
MechForge AI GUI 后端服务器
提供 HTTP API 供前端 JavaScript 调用
"""

import json
import logging
import socket
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

# ── 路径设置 ──────────────────────────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).parent.parent
GUI_DIR      = Path(__file__).parent.resolve()

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# ── FastAPI ───────────────────────────────────────────────────────────────────
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

# ── MechForge Core ────────────────────────────────────────────────────────────
from mechforge_ai.llm_client import LLMClient
from mechforge_ai.rag_engine import RAGEngine
from mechforge_core.config import find_knowledge_path, get_config

# ── 日志 ──────────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("mechforge.server")

# ── 应用 ──────────────────────────────────────────────────────────────────────
app = FastAPI(
    title="MechForge AI GUI Backend",
    description="Backend API for MechForge AI Desktop GUI",
    version="0.5.0",
    docs_url="/docs",
    redoc_url=None,
)

# ── CORS ──────────────────────────────────────────────────────────────────────
# 注意：allow_origins=["*"] 与 allow_credentials=True 不能同时使用
# 解决方法：明确列出所有可能来源
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5000",
        "http://127.0.0.1:5000",
        "http://localhost:8080",
        "http://127.0.0.1:8080",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── 全局状态 ──────────────────────────────────────────────────────────────────
class AppState:
    llm_client:           Optional[LLMClient]    = None
    rag_engine:           Optional[RAGEngine]    = None
    conversation_history: List[Dict[str, str]]   = []
    config                                       = get_config()


state = AppState()


# ── 懒加载工厂 ────────────────────────────────────────────────────────────────
def get_llm_client() -> LLMClient:
    """获取或创建 LLM 客户端（懒加载）"""
    if state.llm_client is None:
        state.llm_client = LLMClient()
        state.llm_client.conversation_history = state.conversation_history
        logger.info("LLM 客户端已初始化")
    return state.llm_client


def get_rag_engine() -> RAGEngine:
    """获取或创建 RAG 引擎（懒加载）"""
    if state.rag_engine is None:
        knowledge_path   = find_knowledge_path()
        state.rag_engine = RAGEngine(
            knowledge_path=knowledge_path,
            top_k=state.config.knowledge.rag.top_k,
        )
        logger.info(f"RAG 引擎已初始化: {knowledge_path}")
    return state.rag_engine


def get_active_provider_config():
    """获取当前激活的 provider 配置，返回 (provider_name, provider_config)"""
    provider_name   = state.config.provider.get_active_provider()
    provider_config = state.config.provider.get_config(provider_name)
    return provider_name, provider_config


# ── 数据模型 ──────────────────────────────────────────────────────────────────
class ChatRequest(BaseModel):
    message: str  = Field(..., min_length=1, description="用户消息")
    rag:     bool = Field(False, description="是否启用 RAG 检索")
    stream:  bool = Field(False, description="是否使用流式响应")


class ChatResponse(BaseModel):
    response:  str
    model:     str
    rag_used:  bool           = False
    context:   Optional[str] = None


class RAGSearchRequest(BaseModel):
    query: str = Field(..., min_length=1)
    limit: int = Field(5, ge=1, le=20)


class RAGSearchResponse(BaseModel):
    results: List[Dict[str, Any]]


class ConfigResponse(BaseModel):
    ai:  Dict[str, Any]
    rag: Dict[str, Any]
    ui:  Dict[str, Any]


# ── 工具函数 ──────────────────────────────────────────────────────────────────
def _should_use_rag(request: ChatRequest) -> bool:
    return request.rag or state.config.knowledge.rag.enabled


def _retrieve_context(message: str) -> tuple[str, bool]:
    """尝试 RAG 检索，返回 (context, rag_used)"""
    try:
        rag = get_rag_engine()
        if rag.is_available and rag.check_trigger(message):
            context = rag.search(message)
            logger.info("RAG 已触发，检索到上下文")
            return context, True
    except Exception as e:
        logger.warning(f"RAG 检索失败，跳过: {e}")
    return "", False


# ═══════════════════════════════════════════════════════════════════════════════
#  健康检查
# ═══════════════════════════════════════════════════════════════════════════════

@app.get("/health", tags=["系统"])
async def health_check():
    return {"status": "healthy", "version": "0.5.0"}


@app.get("/api/status", tags=["系统"])   # 修复：原来是 /status，前端请求 /api/status
async def get_status():
    llm = get_llm_client()
    rag = get_rag_engine()
    return {
        "status":         "ready",
        "version":        "0.5.0",
        "api_type":       llm.get_api_type()           if hasattr(llm, "get_api_type")           else "unknown",
        "model":          llm.get_current_model_name() if hasattr(llm, "get_current_model_name") else "unknown",
        "rag_enabled":    state.config.knowledge.rag.enabled,
        "rag_available":  getattr(rag, "is_available", False),
        "doc_count":      getattr(rag, "doc_count",    0),
        "history_length": len(state.conversation_history),
    }


# ═══════════════════════════════════════════════════════════════════════════════
#  AI 聊天 API
# ═══════════════════════════════════════════════════════════════════════════════

@app.post("/api/chat", response_model=ChatResponse, tags=["聊天"])
async def chat(request: ChatRequest):
    """非流式聊天"""
    llm          = get_llm_client()
    user_message = request.message.strip()

    state.conversation_history.append({"role": "user", "content": user_message})

    context, rag_used = "", False
    if _should_use_rag(request):
        context, rag_used = _retrieve_context(user_message)

    try:
        response_text = llm.call(user_message, context)
    except Exception as e:
        logger.error(f"LLM 调用失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"LLM 调用失败: {e}")

    state.conversation_history.append({"role": "assistant", "content": response_text})

    return ChatResponse(
        response = response_text,
        model    = llm.get_current_model_name() if hasattr(llm, "get_current_model_name") else "unknown",
        rag_used = rag_used,
        context  = context if rag_used else None,
    )


@app.post("/api/chat/stream", tags=["聊天"])
async def chat_stream(request: ChatRequest):
    """流式聊天（SSE）"""
    llm          = get_llm_client()
    user_message = request.message.strip()

    state.conversation_history.append({"role": "user", "content": user_message})

    context, rag_used = "", False
    if _should_use_rag(request):
        context, rag_used = _retrieve_context(user_message)

    # 构建消息列表（最近 10 条历史）
    messages = [{"role": "system", "content": "You are a helpful AI assistant."}]
    messages.extend(state.conversation_history[-10:])
    if context:
        messages[-1]["content"] = f"{user_message}\n\n相关上下文:\n{context}"

    async def generate():
        full_response = ""
        try:
            for chunk in llm.provider.chat(messages, stream=True):
                if chunk:
                    full_response += chunk
                    yield f"data: {json.dumps({'content': chunk})}\n\n"
            yield "data: [DONE]\n\n"
            state.conversation_history.append({"role": "assistant", "content": full_response})
        except Exception as e:
            logger.error(f"流式生成失败: {e}", exc_info=True)
            yield f"data: {json.dumps({'error': str(e)})}\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@app.get("/api/chat/history", tags=["聊天"])
async def get_history():
    return {"history": state.conversation_history}


@app.delete("/api/chat/history", tags=["聊天"])
async def clear_history():
    state.conversation_history.clear()
    logger.info("对话历史已清空")
    return {"success": True, "message": "History cleared"}


# ═══════════════════════════════════════════════════════════════════════════════
#  RAG API
# ═══════════════════════════════════════════════════════════════════════════════

@app.post("/api/rag/search", response_model=RAGSearchResponse, tags=["RAG"])
async def rag_search(request: RAGSearchRequest):
    rag = get_rag_engine()
    if not getattr(rag, "is_available", False):
        return RAGSearchResponse(results=[])

    try:
        context = rag.search(request.query)
    except Exception as e:
        logger.error(f"RAG 检索失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

    results: List[Dict[str, Any]] = []
    if context:
        current: Dict[str, Any] = {}
        for line in context.split("\n"):
            if line.startswith("【参考知识库】"):
                continue
            elif line.startswith("[") and "《" in line:
                if current:
                    results.append(current)
                t_start = line.find("《") + 1
                t_end   = line.find("》")
                if 0 < t_start < t_end:
                    current = {"title": line[t_start:t_end], "content": "",
                               "score": 0.9, "source": "knowledge_base"}
            elif line.startswith("来源:"):
                if current:
                    current["source"] = line[3:].strip()
            elif line and not line.startswith("["):
                if current:
                    current["content"] += line + " "
        if current and current not in results:
            results.append(current)

    return RAGSearchResponse(results=results[: request.limit])


@app.get("/api/rag/status", tags=["RAG"])
async def rag_status():
    rag = get_rag_engine()
    return {
        "enabled":        state.config.knowledge.rag.enabled,
        "available":      getattr(rag, "is_available",   False),
        "doc_count":      getattr(rag, "doc_count",      0),
        "knowledge_path": str(getattr(rag, "knowledge_path", "")) or None,
    }


@app.post("/api/rag/toggle", tags=["RAG"])
async def toggle_rag(body: Dict[str, Any]):
    enabled = bool(body.get("enabled", False))
    state.config.knowledge.rag.enabled = enabled
    logger.info(f"RAG {'已启用' if enabled else '已禁用'}")
    return {"enabled": enabled}


# ═══════════════════════════════════════════════════════════════════════════════
#  配置 API
# ═══════════════════════════════════════════════════════════════════════════════

@app.get("/api/config", response_model=ConfigResponse, tags=["配置"])
async def get_config_api():
    provider_name, provider_config = get_active_provider_config()
    base_url = (getattr(provider_config, "url", None)
                or getattr(provider_config, "base_url", ""))
    model    = getattr(provider_config, "model", "unknown")

    return ConfigResponse(
        ai={
            "provider": provider_name,
            "model":    model,
            "base_url": base_url,
        },
        rag={
            "enabled":         state.config.knowledge.rag.enabled,
            "backend":         "local",
            "top_k":           state.config.knowledge.rag.top_k,
            "embedding_model": state.config.knowledge.rag.embedding_model,
        },
        ui={"theme": "dark", "language": "zh-CN"},
    )


@app.post("/api/config", tags=["配置"])
async def update_config(config: Dict[str, Any]):
    # TODO: 实现配置持久化
    return {"success": True}


@app.get("/api/models", tags=["配置"])
async def get_models():
    """获取可用模型列表，优先从 Ollama 拉取"""
    try:
        import requests
        ollama_url = state.config.provider.ollama.url
        resp = requests.get(f"{ollama_url}/api/tags", timeout=5)
        if resp.status_code == 200:
            return [
                {"name": m["name"], "provider": "ollama", "size": m.get("size", 0)}
                for m in resp.json().get("models", [])
            ]
    except Exception:
        pass

    provider_name, provider_config = get_active_provider_config()
    return [{"name": getattr(provider_config, "model", "unknown"), "provider": provider_name}]


# ═══════════════════════════════════════════════════════════════════════════════
#  静态文件服务（必须在所有 API 路由注册完之后挂载）
# ═══════════════════════════════════════════════════════════════════════════════

@app.get("/", tags=["静态"])
async def serve_index():
    index_file = GUI_DIR / "index.html"
    if index_file.exists():
        return FileResponse(str(index_file), media_type="text/html")
    return HTMLResponse(
        f"<pre>index.html not found.\nGUI_DIR = {GUI_DIR}</pre>",
        status_code=404,
    )

@app.get("/styles.css", tags=["静态"])
async def serve_styles():
    return FileResponse(str(GUI_DIR / "styles.css"), media_type="text/css")

@app.get("/app.js", tags=["静态"])
async def serve_appjs():
    return FileResponse(str(GUI_DIR / "app.js"), media_type="application/javascript")

@app.get("/dj-whale.png", tags=["静态"])
async def serve_whale():
    f = GUI_DIR / "dj-whale.png"
    if f.exists():
        return FileResponse(str(f), media_type="image/png")
    return HTMLResponse("not found", status_code=404)

# core/ 和 services/ 子目录静态挂载
for _mount, _dir in [("core", GUI_DIR / "core"), ("services", GUI_DIR / "services")]:
    if _dir.exists():
        app.mount(f"/{_mount}", StaticFiles(directory=str(_dir)), name=_mount)
    else:
        logger.warning(f"静态目录不存在，跳过挂载: {_dir}")


# ═══════════════════════════════════════════════════════════════════════════════
#  启动入口
# ═══════════════════════════════════════════════════════════════════════════════

def find_free_port(start_port: int = 5000, max_attempts: int = 100) -> int:
    """从 start_port 开始查找第一个可用端口"""
    for port in range(start_port, start_port + max_attempts):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(("127.0.0.1", port))
                return port
        except OSError:
            continue
    raise RuntimeError(f"在 {start_port}~{start_port + max_attempts} 范围内找不到可用端口")


def run_server(host: str = "127.0.0.1", port: int = 5000, reload: bool = False) -> None:
    import uvicorn

    port = find_free_port(port)
    logger.info(f"MechForge AI GUI 后端启动: http://{host}:{port}")
    logger.info(f"GUI 目录: {GUI_DIR}")
    logger.info(f"RAG 启用: {state.config.knowledge.rag.enabled}")

    uvicorn.run(
        "gui.server:app",
        host=host,
        port=port,
        reload=reload,
        log_level="warning",
    )


if __name__ == "__main__":
    run_server()