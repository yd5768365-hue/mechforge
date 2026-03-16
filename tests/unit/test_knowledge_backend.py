"""
知识库后端单元测试
"""

import pytest
from abc import ABC

from mechforge_knowledge.backends.base import Document, KnowledgeBackend, SearchResult


class TestDocument:
    """Document 数据类测试"""

    def test_create_document(self):
        """测试创建文档"""
        doc = Document(
            id="doc1",
            title="测试文档",
            content="这是测试内容",
            source="test.md",
        )

        assert doc.id == "doc1"
        assert doc.title == "测试文档"
        assert doc.content == "这是测试内容"
        assert doc.source == "test.md"
        assert doc.metadata is None

    def test_document_with_metadata(self):
        """测试带元数据的文档"""
        doc = Document(
            id="doc2",
            title="测试文档2",
            content="内容",
            source="test.md",
            metadata={"author": "tester", "version": 1},
        )

        assert doc.metadata["author"] == "tester"
        assert doc.metadata["version"] == 1


class TestSearchResult:
    """SearchResult 数据类测试"""

    def test_create_search_result(self):
        """测试创建搜索结果"""
        result = SearchResult(
            content="搜索结果内容",
            score=0.95,
            source="test.md",
        )

        assert result.content == "搜索结果内容"
        assert result.score == 0.95
        assert result.source == "test.md"
        assert result.metadata is None

    def test_search_result_with_metadata(self):
        """测试带元数据的搜索结果"""
        result = SearchResult(
            content="内容",
            score=0.8,
            source="doc.md",
            metadata={"chunk_id": 1},
        )

        assert result.metadata["chunk_id"] == 1


class MockKnowledgeBackend(KnowledgeBackend):
    """模拟知识库后端，用于测试"""

    def __init__(self):
        self._documents: dict[str, Document] = {}

    async def add_document(self, file_path: str, metadata: dict | None = None) -> str:
        doc = Document(
            id=file_path,
            title=file_path,
            content="mock content",
            source=file_path,
            metadata=metadata,
        )
        self._documents[doc.id] = doc
        return doc.id

    async def add_text(self, content: str, title: str, metadata: dict | None = None) -> str:
        doc = Document(
            id=title,
            title=title,
            content=content,
            source="memory",
            metadata=metadata,
        )
        self._documents[doc.id] = doc
        return doc.id

    async def search(self, query: str, top_k: int = 5) -> list[SearchResult]:
        results = []
        for doc in self._documents.values():
            if query.lower() in doc.content.lower():
                results.append(SearchResult(
                    content=doc.content,
                    score=0.9,
                    source=doc.source,
                ))
        return results[:top_k]

    async def delete(self, doc_id: str) -> bool:
        if doc_id in self._documents:
            del self._documents[doc_id]
            return True
        return False

    async def list_documents(self) -> list[Document]:
        return list(self._documents.values())

    async def get_document(self, doc_id: str) -> Document | None:
        return self._documents.get(doc_id)


class TestKnowledgeBackend:
    """KnowledgeBackend 抽象类测试"""

    @pytest.fixture
    def backend(self):
        """创建模拟后端"""
        return MockKnowledgeBackend()

    @pytest.mark.asyncio
    async def test_add_document(self, backend):
        """测试添加文档"""
        doc_id = await backend.add_document("test.md")
        assert doc_id == "test.md"

    @pytest.mark.asyncio
    async def test_add_text(self, backend):
        """测试添加文本"""
        doc_id = await backend.add_text("Hello World", "greeting")
        assert doc_id == "greeting"

    @pytest.mark.asyncio
    async def test_search(self, backend):
        """测试搜索"""
        await backend.add_text("机械设计基础", "design")
        await backend.add_text("材料力学", "materials")

        results = await backend.search("机械")
        assert len(results) >= 1

    @pytest.mark.asyncio
    async def test_delete(self, backend):
        """测试删除"""
        await backend.add_document("to_delete.md")
        result = await backend.delete("to_delete.md")
        assert result is True

    @pytest.mark.asyncio
    async def test_list_documents(self, backend):
        """测试列出文档"""
        await backend.add_document("doc1.md")
        await backend.add_document("doc2.md")

        docs = await backend.list_documents()
        assert len(docs) == 2

    @pytest.mark.asyncio
    async def test_get_document(self, backend):
        """测试获取文档"""
        await backend.add_document("test.md", {"author": "tester"})
        doc = await backend.get_document("test.md")

        assert doc is not None
        assert doc.id == "test.md"
        assert doc.metadata["author"] == "tester"

    def test_backend_is_abstract(self):
        """测试 KnowledgeBackend 是抽象类"""
        # 不能直接实例化抽象类
        with pytest.raises(TypeError):
            KnowledgeBackend()
