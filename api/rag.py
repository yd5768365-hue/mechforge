"""
RAG API 路由 — 知识库向量检索与文档管理
"""

import logging
from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from .knowledge_engine import get_knowledge_engine
from .state import state

logger = logging.getLogger("mechforge.api.rag")

router = APIRouter(prefix="/api/rag", tags=["RAG"])


# ── 数据模型 ──────────────────────────────────────────────────────────────────


class RAGSearchRequest(BaseModel):
    query: str = Field(..., min_length=1)
    limit: int = Field(5, ge=1, le=20)


# ── 搜索端点 ──────────────────────────────────────────────────────────────────


@router.post("/search")
async def rag_search(request: RAGSearchRequest) -> dict:
    """语义搜索知识库"""
    engine = get_knowledge_engine()

    try:
        engine._ensure_ready()
    except Exception as e:
        logger.warning("知识库引擎未就绪: %s", e)
        return {"results": [], "message": "知识库引擎未就绪"}

    if engine.doc_count == 0:
        return {"results": [], "message": "知识库为空，请先添加文档"}

    try:
        results = engine.search(request.query, top_k=request.limit)
        return {"results": results, "total": len(results)}
    except Exception as e:
        logger.error("RAG 检索失败: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/status")
async def rag_status() -> dict:
    """获取知识库状态"""
    engine = get_knowledge_engine()

    try:
        engine._ensure_ready()
        stats = engine.get_stats()
        return {
            "enabled": state.config.knowledge.rag.enabled,
            "available": engine.is_ready,
            "doc_count": stats["doc_count"],
            "indexed_files": stats["indexed_files"],
            "knowledge_dir": stats["knowledge_dir"],
        }
    except Exception:
        return {
            "enabled": state.config.knowledge.rag.enabled,
            "available": False,
            "doc_count": 0,
            "indexed_files": 0,
            "knowledge_dir": str(engine.knowledge_dir),
        }


@router.post("/toggle")
async def toggle_rag(body: dict[str, Any]) -> dict:
    """切换 RAG 开关"""
    enabled = bool(body.get("enabled", False))
    state.config.knowledge.rag.enabled = enabled
    logger.info("RAG %s", "enabled" if enabled else "disabled")
    return {"success": True, "enabled": enabled}


# ── 文档管理端点 ──────────────────────────────────────────────────────────────


@router.post("/index")
async def index_documents(body: dict[str, Any] | None = None) -> dict:
    """索引知识库目录下的文档"""
    engine = get_knowledge_engine()
    directory = body.get("directory") if body else None

    try:
        result = engine.index_directory(directory)
        return result
    except Exception as e:
        logger.error("文档索引失败: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/sources")
async def list_sources() -> dict:
    """列出已索引的文档源"""
    engine = get_knowledge_engine()

    try:
        engine._ensure_ready()
        sources = engine.list_sources()
        return {"sources": sources, "total": len(sources)}
    except Exception as e:
        logger.error("获取文档源失败: %s", e)
        return {"sources": [], "total": 0}


@router.delete("/clear")
async def clear_knowledge() -> dict:
    """清空知识库"""
    engine = get_knowledge_engine()
    try:
        engine._ensure_ready()
        return engine.clear()
    except Exception as e:
        logger.error("清空知识库失败: %s", e)
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/stats")
async def knowledge_stats() -> dict:
    """获取知识库统计"""
    engine = get_knowledge_engine()
    try:
        engine._ensure_ready()
        return engine.get_stats()
    except Exception as e:
        return {"ready": False, "error": str(e)}
