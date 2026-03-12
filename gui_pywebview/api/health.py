"""
健康检查 API 路由
"""

from fastapi import APIRouter

from .state import state

router = APIRouter(tags=["系统"])


@router.get("/health")
async def health_check() -> dict:
    """健康检查端点"""
    return {"status": "healthy", "version": "0.5.0"}


@router.get("/api/status")
async def get_status() -> dict:
    """获取系统状态"""
    from .deps import get_llm_client, get_rag_engine

    llm = get_llm_client()
    rag = get_rag_engine()

    return {
        "status": "ready",
        "version": "0.5.0",
        "api_type": llm.get_api_type() if hasattr(llm, "get_api_type") else "unknown",
        "model": (
            llm.get_current_model_name() if hasattr(llm, "get_current_model_name") else "unknown"
        ),
        "rag_enabled": state.config.knowledge.rag.enabled,
        "rag_available": getattr(rag, "is_available", False),
        "doc_count": getattr(rag, "doc_count", 0),
        "history_length": len(state.conversation_history),
    }
