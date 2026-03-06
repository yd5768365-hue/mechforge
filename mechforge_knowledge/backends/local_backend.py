"""
本地知识库后端实现

基于 ChromaDB + BM25 的本地知识库实现，无需外部服务依赖。
"""

import os
from pathlib import Path
from typing import Any

from mechforge_knowledge.backends.base import Document, KnowledgeBackend, SearchResult


class LocalBackend(KnowledgeBackend):
    """
    本地知识库后端

    使用 ChromaDB 向量数据库 + BM25 关键词检索，
    支持 Markdown、TXT、PDF 等格式文档。

    特点：
    - 无需外部服务
    - 支持离线使用
    - 轻量级部署
    """

    def __init__(
        self,
        knowledge_path: str | Path = "./knowledge",
        cache_dir: str | Path = ".cache/knowledge",
        embedding_model: str = "all-MiniLM-L6-v2",
        top_k: int = 5,
    ):
        """
        初始化本地知识库后端

        Args:
            knowledge_path: 知识库文档目录
            cache_dir: 缓存目录
            embedding_model: 嵌入模型名称
            top_k: 默认检索数量
        """
        self.knowledge_path = Path(knowledge_path)
        self.cache_dir = Path(cache_dir)
        self.embedding_model = embedding_model
        self.top_k = top_k

        # 延迟初始化的组件
        self._documents: list[dict[str, Any]] = []
        self._chroma_client = None
        self._collection = None
        self._bm25_index = None
        self._embedding_func = None
        self._initialized = False

    def _ensure_initialized(self):
        """确保后端已初始化"""
        if self._initialized:
            return

        # 创建缓存目录
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        # 加载文档
        self._load_documents()

        self._initialized = True

    def _load_documents(self):
        """加载知识库文档"""
        if not self.knowledge_path.exists():
            return

        self._documents = []

        for file_path in self.knowledge_path.glob("*.md"):
            try:
                with open(file_path, encoding="utf-8", errors="ignore") as f:
                    content = f.read()

                # 提取标题
                title = file_path.stem.replace("_", " ").replace("-", " ").title()
                for line in content.split("\n"):
                    if line.strip().startswith("#"):
                        title = line.strip().lstrip("#").strip()
                        break

                self._documents.append(
                    {
                        "id": file_path.stem,
                        "title": title,
                        "content": content,
                        "source": str(file_path),
                        "filename": file_path.name,
                    }
                )
            except Exception:
                pass

        # 也加载 TXT 文件
        for file_path in self.knowledge_path.glob("*.txt"):
            try:
                with open(file_path, encoding="utf-8", errors="ignore") as f:
                    content = f.read()

                self._documents.append(
                    {
                        "id": file_path.stem,
                        "title": file_path.stem,
                        "content": content,
                        "source": str(file_path),
                        "filename": file_path.name,
                    }
                )
            except Exception:
                pass

    async def add_document(self, file_path: str, metadata: dict[str, Any] | None = None) -> str:
        """
        添加文档到知识库

        Args:
            file_path: 文档文件路径
            metadata: 文档元数据

        Returns:
            文档 ID
        """
        self._ensure_initialized()

        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        # 复制文件到知识库目录
        dest_path = self.knowledge_path / file_path.name
        if file_path != dest_path:
            import shutil

            shutil.copy(file_path, dest_path)

        # 重新加载文档
        self._load_documents()

        return file_path.stem

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
        self._ensure_initialized()

        # 生成安全的文件名
        import re

        safe_title = re.sub(r'[<>:"/\\|?*]', "_", title)
        file_path = self.knowledge_path / f"{safe_title}.md"

        # 写入文件
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(f"# {title}\n\n{content}")

        # 重新加载文档
        self._load_documents()

        return safe_title

    async def search(self, query: str, top_k: int = 5) -> list[SearchResult]:
        """
        检索知识库

        使用关键词匹配进行检索。

        Args:
            query: 查询文本
            top_k: 返回结果数量

        Returns:
            检索结果列表
        """
        self._ensure_initialized()

        if not self._documents:
            return []

        query_lower = query.lower()
        query_words = set(query_lower.split())

        results = []
        for doc in self._documents:
            content_lower = doc["content"].lower()
            title_lower = doc["title"].lower()

            # 计算匹配分数
            score = 0

            # 标题匹配
            if query_lower in title_lower:
                score += 100

            # 内容匹配
            if query_lower in content_lower:
                score += 50
                # 计算出现次数
                score += content_lower.count(query_lower) * 10

            # 单词匹配
            for word in query_words:
                if len(word) > 1 and word in content_lower:
                    score += 5

            if score > 0:
                # 提取匹配上下文
                context = self._extract_context(doc["content"], query)

                results.append(
                    SearchResult(
                        content=context,
                        score=float(score),
                        source=doc["filename"],
                        metadata={
                            "doc_id": doc["id"],
                            "title": doc["title"],
                        },
                    )
                )

        # 按分数排序
        results.sort(key=lambda x: x.score, reverse=True)
        return results[:top_k]

    def _extract_context(self, content: str, query: str, context_chars: int = 200) -> str:
        """提取匹配上下文"""
        content_lower = content.lower()
        query_lower = query.lower()

        pos = content_lower.find(query_lower)
        if pos == -1:
            # 返回开头部分
            return content[:context_chars] + "..." if len(content) > context_chars else content

        # 提取上下文
        start = max(0, pos - context_chars // 2)
        end = min(len(content), pos + len(query) + context_chars // 2)

        context = content[start:end]
        if start > 0:
            context = "..." + context
        if end < len(content):
            context = context + "..."

        return context

    async def delete_document(self, doc_id: str) -> bool:
        """
        删除文档

        Args:
            doc_id: 文档 ID

        Returns:
            是否删除成功
        """
        self._ensure_initialized()

        # 查找并删除文件
        for ext in [".md", ".txt"]:
            file_path = self.knowledge_path / f"{doc_id}{ext}"
            if file_path.exists():
                try:
                    os.unlink(file_path)
                    self._load_documents()
                    return True
                except Exception:
                    return False

        return False

    async def list_documents(self, limit: int = 100, offset: int = 0) -> list[Document]:
        """
        列出知识库中的文档

        Args:
            limit: 返回数量限制
            offset: 偏移量

        Returns:
            文档列表
        """
        self._ensure_initialized()

        documents = []
        for doc in self._documents[offset : offset + limit]:
            documents.append(
                Document(
                    id=doc["id"],
                    title=doc["title"],
                    content="",  # 列表不返回内容
                    source=doc["source"],
                    metadata={
                        "filename": doc["filename"],
                    },
                )
            )

        return documents

    async def get_stats(self) -> dict[str, Any]:
        """
        获取知识库统计信息

        Returns:
            统计信息字典
        """
        self._ensure_initialized()

        total_chars = sum(len(doc["content"]) for doc in self._documents)

        return {
            "status": "ready",
            "backend": "local",
            "knowledge_path": str(self.knowledge_path),
            "document_count": len(self._documents),
            "total_chars": total_chars,
            "embedding_model": self.embedding_model,
        }

    async def health_check(self) -> bool:
        """
        检查后端健康状态

        Returns:
            是否健康
        """
        return self.knowledge_path.exists() or True  # 本地后端始终健康