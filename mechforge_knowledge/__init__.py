"""
MechForge Knowledge - Knowledge base search

支持多种知识库后端：
- local: 本地 ChromaDB + BM25 实现
- ragflow: RAGFlow API 后端（高级文档解析能力）
"""

from mechforge_knowledge.backends import KnowledgeBackend, LocalBackend, RAGFlowBackend
from mechforge_knowledge.backends.base import Document, SearchResult
from mechforge_knowledge.lookup import (
    interactive_lookup,
    load_knowledge_files,
    quick_lookup,
    search_by_keyword,
)
from mechforge_knowledge.rag import (
    search_knowledge,
    search_text,
    search_with_chroma,
)


def get_backend(backend_type: str = "local", **kwargs) -> KnowledgeBackend:
    """
    获取知识库后端实例

    Args:
        backend_type: 后端类型 ("local" 或 "ragflow")
        **kwargs: 后端配置参数

    Returns:
        知识库后端实例
    """
    if backend_type == "ragflow":
        return RAGFlowBackend(
            base_url=kwargs.get("url", "http://localhost:9380"),
            api_key=kwargs.get("api_key", ""),
            kb_id=kwargs.get("kb_id", ""),
            timeout=kwargs.get("timeout", 300),
        )
    else:
        return LocalBackend(
            knowledge_path=kwargs.get("path", "./knowledge"),
            cache_dir=kwargs.get("cache_dir", ".cache/knowledge"),
            embedding_model=kwargs.get("embedding_model", "all-MiniLM-L6-v2"),
            top_k=kwargs.get("top_k", 5),
        )


def get_backend_from_config() -> KnowledgeBackend:
    """
    从配置文件获取知识库后端实例

    Returns:
        知识库后端实例
    """
    from mechforge_core.config import get_config

    config = get_config()
    kb_config = config.knowledge

    if kb_config.backend == "ragflow":
        return RAGFlowBackend(
            base_url=kb_config.ragflow.url,
            api_key=kb_config.ragflow.api_key,
            kb_id=kb_config.ragflow.kb_id,
            timeout=kb_config.ragflow.timeout,
        )
    else:
        return LocalBackend(
            knowledge_path=kb_config.path,
            cache_dir=kb_config.rag.cache_dir,
            embedding_model=kb_config.rag.embedding_model,
            top_k=kb_config.rag.top_k,
        )


__all__ = [
    # 后端
    "KnowledgeBackend",
    "LocalBackend",
    "RAGFlowBackend",
    "Document",
    "SearchResult",
    "get_backend",
    "get_backend_from_config",
    # 现有功能
    "search_by_keyword",
    "load_knowledge_files",
    "interactive_lookup",
    "quick_lookup",
    "search_with_chroma",
    "search_text",
    "search_knowledge",
]
