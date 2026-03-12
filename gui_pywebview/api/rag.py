"""
RAG API 路由
"""

import logging
from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from .deps import get_rag_engine
from .state import state

logger = logging.getLogger("mechforge.api.rag")

router = APIRouter(prefix="/api/rag", tags=["RAG"])


# ── 数据模型 ──────────────────────────────────────────────────────────────────


class RAGSearchRequest(BaseModel):
    """RAG 搜索请求"""

    query: str = Field(..., min_length=1)
    limit: int = Field(5, ge=1, le=20)


class RAGSearchResponse(BaseModel):
    """RAG 搜索响应"""

    results: list[dict[str, Any]]


# ── API 端点 ──────────────────────────────────────────────────────────────────


@router.post("/search", response_model=RAGSearchResponse)
async def rag_search(request: RAGSearchRequest) -> RAGSearchResponse:
    """搜索知识库"""
    rag = get_rag_engine()
    if not getattr(rag, "is_available", False):
        return RAGSearchResponse(results=[])

    try:
        context = rag.search(request.query)
    except Exception as e:
        logger.error(f"RAG 检索失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e)) from e

    results: list[dict[str, Any]] = []
    if context:
        current: dict[str, Any] = {}
        for line in context.split("\n"):
            if line.startswith("【参考知识库】"):
                continue
            elif line.startswith("[") and "《" in line:
                if current:
                    results.append(current)
                t_start = line.find("《") + 1
                t_end = line.find("》")
                if 0 < t_start < t_end:
                    current = {
                        "title": line[t_start:t_end],
                        "content": "",
                        "score": 0.9,
                        "source": "knowledge_base",
                    }
            elif line.startswith("来源:"):
                if current:
                    current["source"] = line[3:].strip()
            elif line and not line.startswith("["):
                if current:
                    current["content"] += line + " "
        if current and current not in results:
            results.append(current)

    return RAGSearchResponse(results=results[: request.limit])


@router.get("/status")
async def rag_status() -> dict:
    """获取 RAG 状态"""
    rag = get_rag_engine()
    return {
        "enabled": state.config.knowledge.rag.enabled,
        "available": getattr(rag, "is_available", False),
        "doc_count": getattr(rag, "doc_count", 0),
        "knowledge_path": str(getattr(rag, "knowledge_path", "")) or None,
    }


@router.post("/toggle")
async def toggle_rag(body: dict[str, Any]) -> dict:
    """切换 RAG 开关"""
    enabled = bool(body.get("enabled", False))
    state.config.knowledge.rag.enabled = enabled
    logger.info(f"RAG {'enabled' if enabled else 'disabled'}")
    return {
        "success": True,
        "enabled": enabled,
    }
