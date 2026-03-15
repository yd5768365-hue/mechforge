"""
MechForge Knowledge Backends

支持多种知识库后端：
- local: 本地 ChromaDB + BM25 实现
- ragflow: RAGFlow API 后端（高级文档解析能力）
"""

from mechforge_knowledge.backends.base import KnowledgeBackend
from mechforge_knowledge.backends.local_backend import LocalBackend
from mechforge_knowledge.backends.ragflow_backend import RAGFlowBackend

__all__ = [
    "KnowledgeBackend",
    "LocalBackend",
    "RAGFlowBackend",
]