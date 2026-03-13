"""
API 依赖项
提供懒加载的 LLM 客户端和 RAG 引擎
"""

import logging
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from mechforge_ai.llm_client import LLMClient
    from mechforge_ai.rag_engine import RAGEngine

from mechforge_core.config import find_knowledge_path

from .state import state

logger = logging.getLogger("mechforge.api")


def get_llm_client() -> "LLMClient":
    """获取或创建 LLM 客户端（懒加载）"""
    if state.llm_client is None:
        from mechforge_ai.llm_client import LLMClient

        state.llm_client = LLMClient()
        state.llm_client.conversation_history = state.conversation_history
        logger.info("LLM 客户端已初始化")
    return state.llm_client


def get_rag_engine() -> "RAGEngine":
    """获取或创建 RAG 引擎（懒加载）"""
    if state.rag_engine is None:
        from mechforge_ai.rag_engine import RAGEngine

        knowledge_path = find_knowledge_path()
        state.rag_engine = RAGEngine(
            knowledge_path=knowledge_path,
            top_k=state.config.knowledge.rag.top_k,
        )
        logger.info(f"RAG 引擎已初始化: {knowledge_path}")
    return state.rag_engine


def get_active_provider_config() -> tuple[str, Any]:
    """获取当前激活的 provider 配置"""
    provider_name = state.config.provider.get_active_provider()
    provider_config = state.config.provider.get_config(provider_name)
    return provider_name, provider_config


def should_use_rag(request_rag: bool) -> bool:
    """判断是否应该使用 RAG"""
    return request_rag or state.config.knowledge.rag.enabled


def retrieve_context(message: str) -> tuple[str, bool]:
    """尝试 RAG 检索，返回 (context, rag_used)

    优先使用本地 ChromaDB 向量引擎，若不可用则回退到原始 RAG 引擎。
    """
    # 1) 优先使用本地 ChromaDB 向量引擎
    try:
        from .knowledge_engine import get_knowledge_engine

        engine = get_knowledge_engine()
        engine._ensure_ready()
        if engine.doc_count > 0:
            results = engine.search(message, top_k=state.config.knowledge.rag.top_k)
            if results:
                context_parts = []
                for r in results:
                    src = r.get("source", "unknown")
                    score = r.get("score", 0)
                    content = r.get("content", "")
                    context_parts.append(f"[来源: {src} | 相关度: {score:.2f}]\n{content}")
                context = "\n\n".join(context_parts)
                logger.info("ChromaDB 向量检索命中 %d 条结果", len(results))
                return context, True
    except Exception as e:
        logger.debug("ChromaDB 向量检索不可用: %s", e)

    # 2) 回退到原始 RAG 引擎
    try:
        rag = get_rag_engine()
        if rag.is_available and rag.check_trigger(message):
            context = rag.search(message)
            logger.info("RAG 已触发，检索到上下文")
            return context, True
    except Exception as e:
        logger.warning("RAG 检索失败，跳过: %s", e)
    return "", False
