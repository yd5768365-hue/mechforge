"""
RAG 引擎模块 - 多路召回 + 重排序

支持:
- 向量检索 (Dense Retrieval)
- 关键词检索 (BM25)
- 重排序 (Cross-encoder)
- 智能文档切分
- 结果缓存
"""

import hashlib
import logging
import os
import pickle
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import numpy as np

from mechforge_core.config import get_config

# 抑制 HuggingFace 警告
os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")
os.environ.setdefault("HF_HUB_DISABLE_TELEMETRY", "1")
os.environ.setdefault("TRANSFORMERS_VERBOSITY", "error")

# 抑制 sentence-transformers 日志
logging.getLogger("sentence_transformers").setLevel(logging.ERROR)
logging.getLogger("transformers").setLevel(logging.ERROR)


@dataclass
class Document:
    """文档对象"""

    id: str
    content: str
    metadata: dict[str, Any] = field(default_factory=dict)
    embedding: np.ndarray | None = None


@dataclass
class SearchResult:
    """搜索结果"""

    document: Document
    vector_score: float = 0.0
    bm25_score: float = 0.0
    final_score: float = 0.0


class TextSplitter:
    """智能文本切分器"""

    def __init__(
        self,
        chunk_size: int = 512,
        chunk_overlap: int = 50,
        separators: list[str] | None = None,
    ):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.separators = separators or ["\n## ", "\n### ", "\n\n", "\n", "。", ". ", " ", ""]

    def split(self, text: str) -> list[str]:
        """切分文本"""
        chunks = []
        current_chunk = ""

        # 首先按段落分割
        paragraphs = self._split_by_separators(text)

        for para in paragraphs:
            if len(current_chunk) + len(para) < self.chunk_size:
                current_chunk += para + "\n"
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                # 处理长段落
                if len(para) > self.chunk_size:
                    sub_chunks = self._split_long_text(para)
                    chunks.extend(sub_chunks[:-1])
                    current_chunk = sub_chunks[-1] + "\n"
                else:
                    current_chunk = para + "\n"

        if current_chunk:
            chunks.append(current_chunk.strip())

        return chunks

    def _split_by_separators(self, text: str) -> list[str]:
        """按分隔符分割"""
        result = [text]
        for sep in self.separators[:4]:  # 只用前4个作为段落分隔
            new_result = []
            for chunk in result:
                parts = chunk.split(sep)
                for i, part in enumerate(parts):
                    if i > 0:
                        new_result.append(sep + part)
                    else:
                        new_result.append(part)
            result = new_result
        return [r.strip() for r in result if r.strip()]

    def _split_long_text(self, text: str) -> list[str]:
        """切分长文本"""
        chunks = []
        start = 0
        while start < len(text):
            end = min(start + self.chunk_size, len(text))
            # 尝试在句子边界切分
            if end < len(text):
                for sep in ["。", ". ", "?", "!"]:
                    pos = text.rfind(sep, start, end)
                    if pos > start + self.chunk_size // 2:
                        end = pos + 1
                        break
            chunks.append(text[start:end])
            start = end - self.chunk_overlap
        return chunks


class BM25Retriever:
    """BM25 关键词检索器"""

    def __init__(self, documents: list[Document], k1: float = 1.5, b: float = 0.75):
        self.documents = documents
        self.k1 = k1
        self.b = b
        self.avg_doc_len = 0.0
        self.doc_freqs: dict[str, int] = {}
        self.doc_lens: list[int] = []
        self._build_index()

    def _build_index(self):
        """构建索引"""
        total_len = 0
        word_sets = []

        for doc in self.documents:
            words = self._tokenize(doc.content)
            self.doc_lens.append(len(words))
            total_len += len(words)
            word_sets.append(set(words))

        self.avg_doc_len = total_len / len(self.documents) if self.documents else 0

        # 计算文档频率
        all_words = set()
        for ws in word_sets:
            all_words.update(ws)

        for word in all_words:
            freq = sum(1 for ws in word_sets if word in ws)
            self.doc_freqs[word] = freq

    def _tokenize(self, text: str) -> list[str]:
        """分词（简单实现）"""
        # 中文按字，英文按词
        words = []
        current_word = ""

        for char in text.lower():
            if char.isalpha():
                current_word += char
            else:
                if current_word:
                    words.append(current_word)
                    current_word = ""
                if char.strip():
                    words.append(char)

        if current_word:
            words.append(current_word)

        return words

    def search(self, query: str, top_k: int = 5) -> list[tuple[int, float]]:
        """搜索"""
        query_words = self._tokenize(query)
        scores = []

        for idx, doc in enumerate(self.documents):
            doc_words = self._tokenize(doc.content)
            doc_len = len(doc_words)
            doc_word_count = {}
            for w in doc_words:
                doc_word_count[w] = doc_word_count.get(w, 0) + 1

            score = 0.0
            for word in query_words:
                if word not in doc_word_count:
                    continue

                df = self.doc_freqs.get(word, 1)
                idf = np.log((len(self.documents) - df + 0.5) / (df + 0.5) + 1)

                tf = doc_word_count[word]
                denom = tf + self.k1 * (1 - self.b + self.b * doc_len / self.avg_doc_len)
                score += idf * (tf * (self.k1 + 1)) / denom if denom > 0 else 0

            if score > 0:
                scores.append((idx, score))

        scores.sort(key=lambda x: x[1], reverse=True)
        return scores[:top_k]


class VectorRetriever:
    """向量检索器"""

    def __init__(self, documents: list[Document], embedding_model: Any | None = None):
        self.documents = documents
        self.embedding_model = embedding_model
        self.embeddings: np.ndarray | None = None
        self._build_index()

    def _build_index(self):
        """构建向量索引"""
        if not self.documents:
            return

        # 收集已有嵌入或计算新嵌入
        embeddings_list = []
        for doc in self.documents:
            if doc.embedding is not None:
                embeddings_list.append(doc.embedding)
            else:
                emb = self._compute_embedding(doc.content)
                doc.embedding = emb
                embeddings_list.append(emb)

        self.embeddings = np.array(embeddings_list)

    def _compute_embedding(self, text: str) -> np.ndarray:
        """计算文本嵌入（简化实现）"""
        if self.embedding_model:
            try:
                return self.embedding_model.encode(text)
            except Exception:
                pass

        # 回退：使用简单的词袋模型
        words = text.lower().split()
        # 简单的哈希嵌入
        dim = 384  # 与 all-MiniLM-L6-v2 相同维度
        vec = np.zeros(dim)
        for word in words:
            hash_val = int(hashlib.md5(word.encode()).hexdigest(), 16)
            for i in range(dim):
                vec[i] += (hash_val >> (i % 32)) & 1
        # 归一化
        norm = np.linalg.norm(vec)
        return vec / norm if norm > 0 else vec

    def search(self, query: str, top_k: int = 5) -> list[tuple[int, float]]:
        """向量搜索"""
        if self.embeddings is None or len(self.documents) == 0:
            return []

        query_emb = self._compute_embedding(query)

        # 余弦相似度
        similarities = np.dot(self.embeddings, query_emb) / (
            np.linalg.norm(self.embeddings, axis=1) * np.linalg.norm(query_emb) + 1e-8
        )

        # 获取 top_k
        top_indices = np.argsort(similarities)[::-1][:top_k]
        return [(int(idx), float(similarities[idx])) for idx in top_indices]


class Reranker:
    """重排序器（Cross-encoder 简化实现）"""

    def __init__(self, model_name: str | None = None):
        self.model_name = model_name
        self.model = None
        self._load_model()

    def _load_model(self):
        """加载重排序模型"""
        if not self.model_name:
            return

        try:
            from sentence_transformers import CrossEncoder

            self.model = CrossEncoder(self.model_name)
        except Exception:
            self.model = None

    def rerank(
        self, query: str, documents: list[Document], top_k: int = 5
    ) -> list[tuple[int, float]]:
        """重排序"""
        if not documents:
            return []

        if self.model:
            try:
                pairs = [(query, doc.content[:512]) for doc in documents]
                scores = self.model.predict(pairs)
                indexed_scores = list(enumerate(scores))
                indexed_scores.sort(key=lambda x: x[1], reverse=True)
                return [(idx, float(score)) for idx, score in indexed_scores[:top_k]]
            except Exception:
                pass

        # 回退：使用简单的特征匹配
        query_words = set(query.lower().split())
        scores = []
        for idx, doc in enumerate(documents):
            doc_words = set(doc.content.lower().split())
            overlap = len(query_words & doc_words)
            score = overlap / (len(query_words) + 1)
            scores.append((idx, score))

        scores.sort(key=lambda x: x[1], reverse=True)
        return scores[:top_k]


class RAGEngine:
    """增强型 RAG 搜索引擎 - 多路召回 + 重排序"""

    def __init__(
        self,
        knowledge_path: Path | None = None,
        top_k: int = 5,
        use_vector: bool = True,
        use_bm25: bool = True,
        use_rerank: bool = True,
    ):
        self.config = get_config()
        self.knowledge_path = knowledge_path or Path(self.config.knowledge.path)
        self.top_k = top_k
        self.use_vector = use_vector
        self.use_bm25 = use_bm25
        self.use_rerank = use_rerank

        # 检索组件
        self.documents: list[Document] = []
        self.vector_retriever: VectorRetriever | None = None
        self.bm25_retriever: BM25Retriever | None = None
        self.reranker: Reranker | None = None

        # 缓存
        self._cache_dir = Path(self.config.knowledge.rag.cache_dir)
        self._cache_dir.mkdir(parents=True, exist_ok=True)

        # 初始化
        self._load_documents()
        self._init_retrievers()

    def _load_documents(self):
        """加载文档"""
        if not self.knowledge_path.exists():
            return

        cache_file = self._cache_dir / "documents.pkl"

        # 检查缓存
        if cache_file.exists():
            try:
                with open(cache_file, "rb") as f:
                    self.documents = pickle.load(f)
                return
            except Exception:
                pass

        # 从文件加载
        self.documents = []
        splitter = TextSplitter(
            chunk_size=self.config.knowledge.rag.chunk_size,
            chunk_overlap=self.config.knowledge.rag.chunk_overlap,
        )

        for ext in self.config.knowledge.file_extensions:
            for file_path in self.knowledge_path.rglob(f"*{ext}"):
                try:
                    content = file_path.read_text(encoding="utf-8")
                    chunks = splitter.split(content)

                    for i, chunk in enumerate(chunks):
                        doc = Document(
                            id=f"{file_path.stem}_{i}",
                            content=chunk,
                            metadata={
                                "source": str(file_path),
                                "title": file_path.stem,
                                "chunk_index": i,
                                "total_chunks": len(chunks),
                            },
                        )
                        self.documents.append(doc)

                except Exception as e:
                    print(f"加载文件失败 {file_path}: {e}")

        # 保存缓存
        try:
            with open(cache_file, "wb") as f:
                pickle.dump(self.documents, f)
        except Exception:
            pass

    def _init_retrievers(self):
        """初始化检索器"""
        if not self.documents:
            return

        # 向量检索器
        if self.use_vector:
            embedding_model = None
            if self.config.knowledge.rag.embedding_model:
                try:
                    import warnings

                    with warnings.catch_warnings():
                        warnings.simplefilter("ignore")
                        from sentence_transformers import SentenceTransformer

                        embedding_model = SentenceTransformer(
                            self.config.knowledge.rag.embedding_model
                        )
                except Exception:
                    pass
            self.vector_retriever = VectorRetriever(self.documents, embedding_model)

        # BM25 检索器
        if self.use_bm25:
            self.bm25_retriever = BM25Retriever(self.documents)

        # 重排序器
        if self.use_rerank:
            self.reranker = Reranker(self.config.knowledge.rag.rerank_model)

    @property
    def is_available(self) -> bool:
        """检查知识库是否可用"""
        return len(self.documents) > 0

    @property
    def doc_count(self) -> int:
        """获取文档数量"""
        return len(self.documents)

    def check_trigger(self, user_input: str) -> bool:
        """检查是否触发 RAG"""
        triggers = [
            "知识库",
            "数据库",
            "搜索",
            "查一下",
            "帮我查",
            "请问",
            "根据",
            "参照",
            "按照",
            "rag",
            "手册",
            "标准",
            "规范",
            "材料",
            "螺栓",
            "轴承",
            "零件",
            "尺寸",
            "参数",
            "规格",
            "gb",
            "iso",
            "jb",
        ]
        return any(t in user_input.lower() for t in triggers)

    def search(self, query: str) -> str:
        """执行 RAG 搜索 - 多路召回"""
        if not self.is_available:
            return ""

        print(f"   [RAG] 正在检索知识库（共 {self.doc_count} 个文档片段）...")

        # 1. 多路召回
        all_results: dict[str, SearchResult] = {}

        # 向量检索
        if self.vector_retriever:
            vector_results = self.vector_retriever.search(query, top_k=self.top_k * 2)
            for idx, score in vector_results:
                doc_id = self.documents[idx].id
                if doc_id not in all_results:
                    all_results[doc_id] = SearchResult(
                        document=self.documents[idx],
                        vector_score=score,
                    )
                else:
                    all_results[doc_id].vector_score = max(all_results[doc_id].vector_score, score)

        # BM25 检索
        if self.bm25_retriever:
            bm25_results = self.bm25_retriever.search(query, top_k=self.top_k * 2)
            # 归一化 BM25 分数
            max_bm25 = max((s for _, s in bm25_results), default=1.0)
            for idx, score in bm25_results:
                doc_id = self.documents[idx].id
                normalized_score = score / max_bm25 if max_bm25 > 0 else 0
                if doc_id not in all_results:
                    all_results[doc_id] = SearchResult(
                        document=self.documents[idx],
                        bm25_score=normalized_score,
                    )
                else:
                    all_results[doc_id].bm25_score = max(
                        all_results[doc_id].bm25_score, normalized_score
                    )

        if not all_results:
            return ""

        # 2. 融合分数
        fused_results = []
        for result in all_results.values():
            # RRF (Reciprocal Rank Fusion) 或简单加权
            vector_rank = result.vector_score
            bm25_rank = result.bm25_score

            # 加权融合
            result.final_score = 0.6 * vector_rank + 0.4 * bm25_rank
            fused_results.append(result)

        fused_results.sort(key=lambda x: x.final_score, reverse=True)
        fused_results = fused_results[: self.top_k * 2]

        # 3. 重排序
        if self.reranker and self.use_rerank:
            rerank_results = self.reranker.rerank(
                query, [r.document for r in fused_results], top_k=self.top_k
            )
            # 根据重排序结果重新组织
            final_results = []
            for idx, score in rerank_results:
                result = fused_results[idx]
                result.final_score = score
                final_results.append(result)
            final_results.sort(key=lambda x: x.final_score, reverse=True)
        else:
            final_results = fused_results[: self.top_k]

        # 打印结果
        self._print_results(final_results)

        # 构建上下文
        return self._build_context(final_results)

    def _print_results(self, results: list[SearchResult]):
        """打印搜索结果"""
        print(f"   找到 {len(results)} 条最相关知识:")
        for i, r in enumerate(results, 1):
            score = r.final_score
            filled = min(int(score * 5), 5)
            bar = "█" * filled + "░" * (5 - filled)
            title = r.document.metadata.get("title", "未知")[:25]
            source = Path(r.document.metadata.get("source", "")).name[:15]
            print(f"   {i}. [{bar}] {title:<25} ({source})")

    def _build_context(self, results: list[SearchResult]) -> str:
        """构建上下文"""
        context_parts = ["\n【参考知识库】"]

        for i, r in enumerate(results, 1):
            doc = r.document
            title = doc.metadata.get("title", "未知")
            source = doc.metadata.get("source", "")
            content = doc.content[:600]  # 限制长度

            context_parts.append(f"\n[{i}] 《{title}》")
            if source:
                context_parts.append(f"来源: {source}")
            context_parts.append(f"{content}...")

        return "\n".join(context_parts)

    def reload(self):
        """重新加载知识库"""
        self.documents = []
        self.vector_retriever = None
        self.bm25_retriever = None

        # 清除缓存
        cache_file = self._cache_dir / "documents.pkl"
        if cache_file.exists():
            cache_file.unlink()

        self._load_documents()
        self._init_retrievers()
        print(f"   [RAG] 知识库已重载，共 {self.doc_count} 个文档片段")
