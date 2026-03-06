"""
知识库后端抽象接口

定义统一的知识库操作接口，支持多种后端实现。
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Optional


@dataclass
class Document:
    """文档对象"""

    id: str
    title: str
    content: str
    source: str
    metadata: dict[str, Any] | None = None


@dataclass
class SearchResult:
    """检索结果"""

    content: str
    score: float
    source: str
    metadata: dict[str, Any] | None = None


class KnowledgeBackend(ABC):
    """
    知识库后端抽象基类

    所有知识库后端必须实现此接口，确保统一的调用方式。
    """

    @abstractmethod
    async def add_document(self, file_path: str, metadata: dict[str, Any] | None = None) -> str:
        """
        添加文档到知识库

        Args:
            file_path: 文档文件路径
            metadata: 文档元数据

        Returns:
            文档 ID
        """
        pass

    @abstractmethod
    async def add_text(self, content: str, title: str, metadata: dict[str, Any] | None = None) -> str:
        """
        添加文本内容到知识库

        Args:
            content: 文本内容
            title: 文档标题
            metadata: 文档元数据

        Returns:
            文档 ID
        """
        pass

    @abstractmethod
    async def search(self, query: str, top_k: int = 5) -> list[SearchResult]:
        """
        检索知识库

        Args:
            query: 查询文本
            top_k: 返回结果数量

        Returns:
            检索结果列表
        """
        pass

    @abstractmethod
    async def delete_document(self, doc_id: str) -> bool:
        """
        删除文档

        Args:
            doc_id: 文档 ID

        Returns:
            是否删除成功
        """
        pass

    @abstractmethod
    async def list_documents(self, limit: int = 100, offset: int = 0) -> list[Document]:
        """
        列出知识库中的文档

        Args:
            limit: 返回数量限制
            offset: 偏移量

        Returns:
            文档列表
        """
        pass

    @abstractmethod
    async def get_stats(self) -> dict[str, Any]:
        """
        获取知识库统计信息

        Returns:
            统计信息字典
        """
        pass

    @abstractmethod
    async def health_check(self) -> bool:
        """
        检查后端健康状态

        Returns:
            是否健康
        """
        pass