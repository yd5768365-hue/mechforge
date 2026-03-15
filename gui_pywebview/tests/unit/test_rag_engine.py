"""
RAG 引擎单元测试
"""

from mechforge_ai.rag_engine import (
    BM25Retriever,
    Document,
    RAGEngine,
    SearchResult,
    TextSplitter,
    VectorRetriever,
)


class TestTextSplitter:
    """测试文本切分器"""

    def test_split_short_text(self):
        """测试短文本不切分"""
        splitter = TextSplitter(chunk_size=100, chunk_overlap=10)
        text = "这是一个短文本。"
        chunks = splitter.split(text)
        assert len(chunks) == 1
        assert chunks[0] == text

    def test_split_long_text(self):
        """测试长文本切分"""
        splitter = TextSplitter(chunk_size=50, chunk_overlap=10)
        text = "这是一段很长的文本。" * 20
        chunks = splitter.split(text)
        assert len(chunks) > 1

    def test_overlap(self):
        """测试重叠"""
        splitter = TextSplitter(chunk_size=100, chunk_overlap=20)
        text = "A" * 150 + "B" * 150
        chunks = splitter.split(text)
        # 检查重叠
        if len(chunks) > 1:
            overlap = set(chunks[0][-20:]) & set(chunks[1][:20])
            assert len(overlap) > 0


class TestBM25Retriever:
    """测试 BM25 检索器"""

    def test_search(self):
        """测试搜索功能"""
        docs = [
            Document(id="1", content="轴承 6205 的额定动载荷是 14kN"),
            Document(id="2", content="螺栓 M8 的拧紧力矩是 25Nm"),
            Document(id="3", content="轴承 6206 的额定动载荷是 19.5kN"),
        ]

        retriever = BM25Retriever(docs)
        results = retriever.search("轴承 6205", top_k=2)

        assert len(results) > 0
        # 第一个结果应该包含 "轴承"
        first_idx = results[0][0]
        assert "轴承" in docs[first_idx].content

    def test_empty_query(self):
        """测试空查询"""
        docs = [Document(id="1", content="test content")]
        retriever = BM25Retriever(docs)
        results = retriever.search("", top_k=5)
        assert len(results) == 0


class TestVectorRetriever:
    """测试向量检索器"""

    def test_search(self):
        """测试向量搜索"""
        docs = [
            Document(id="1", content="深沟球轴承 6205"),
            Document(id="2", content="六角头螺栓 M8"),
            Document(id="3", content="深沟球轴承 6206"),
        ]

        retriever = VectorRetriever(docs)
        results = retriever.search("轴承", top_k=2)

        assert len(results) > 0

    def test_empty_documents(self):
        """测试空文档列表"""
        retriever = VectorRetriever([])
        results = retriever.search("test", top_k=5)
        assert len(results) == 0


class TestRAGEngine:
    """测试 RAG 引擎"""

    def test_initialization(self, temp_dir, sample_knowledge_base, monkeypatch):
        """测试初始化"""
        monkeypatch.setattr(
            "mechforge_core.config.get_config",
            lambda: type(
                "MockConfig",
                (),
                {
                    "knowledge": type(
                        "K",
                        (),
                        {
                            "path": sample_knowledge_base,
                            "rag": type(
                                "R",
                                (),
                                {
                                    "enabled": True,
                                    "top_k": 3,
                                    "cache_dir": temp_dir / "cache",
                                    "chunk_size": 512,
                                    "chunk_overlap": 50,
                                    "embedding_model": None,
                                    "use_bm25": True,
                                    "use_rerank": True,
                                    "rerank_model": None,
                                },
                            ),
                            "file_extensions": [".md"],
                        },
                    )
                },
            )(),
        )

        engine = RAGEngine(knowledge_path=sample_knowledge_base)
        assert engine.is_available
        assert engine.doc_count > 0

    def test_check_trigger(self):
        """测试触发词检测"""
        engine = RAGEngine.__new__(RAGEngine)

        assert engine.check_trigger("查一下轴承参数") is True
        assert engine.check_trigger("手册中怎么说") is True
        assert engine.check_trigger("GB标准") is True
        assert engine.check_trigger("rag 查询") is True
        assert engine.check_trigger("你好") is False

    def test_build_context(self):
        """测试上下文构建"""
        engine = RAGEngine.__new__(RAGEngine)

        results = [
            SearchResult(
                document=Document(
                    id="1",
                    content="轴承参数内容",
                    metadata={"title": "轴承手册", "source": "/path/to/file.md"},
                ),
                final_score=0.9,
            )
        ]

        context = engine._build_context(results)
        assert "轴承手册" in context
        assert "轴承参数内容" in context
