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