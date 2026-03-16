"""
MechForge AI RAG 知识检索模块

基于 ChromaDB + sentence-transformers 实现向量检索
"""

import hashlib
import json
import sqlite3
import sys
import time
from pathlib import Path
from typing import Any

from rich.console import Console

from mechforge_knowledge.model_cache import get_sentence_transformer

console = Console()


def _get_cache_dir() -> Path:
    """获取缓存目录"""
    if getattr(sys, "frozen", False):
        base = Path(sys._MEIPASS)
    else:
        base = Path(__file__).parent.parent.parent.parent
    return base / ".cache" / "rag"


class RAGCacheManager:
    """RAG 查询缓存管理器"""

    def __init__(self, cache_dir: Path | None = None):
        if cache_dir is None:
            cache_dir = _get_cache_dir()

        self.cache_dir = cache_dir
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.db_path = self.cache_dir / "rag_cache.db"
        self._init_database()

    def _init_database(self):
        """初始化数据库"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS rag_cache (
                query_hash TEXT PRIMARY KEY,
                query_text TEXT NOT NULL,
                result_json TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expire_at TIMESTAMP NOT NULL
            )
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_expire_at ON rag_cache(expire_at)
        """)

        conn.commit()
        conn.close()

    def get(self, query: str) -> list[dict] | None:
        """获取缓存结果"""
        query_hash = hashlib.md5(query.encode()).hexdigest()

        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()

        cursor.execute(
            "SELECT result_json FROM rag_cache WHERE query_hash = ? AND expire_at > ?",
            (query_hash, time.time()),
        )

        row = cursor.fetchone()
        conn.close()

        if row:
            return json.loads(row[0])
        return None

    def set(self, query: str, results: list[dict], ttl: int = 3600):
        """设置缓存结果"""
        query_hash = hashlib.md5(query.encode()).hexdigest()
        expire_at = time.time() + ttl

        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()

        cursor.execute(
            "INSERT OR REPLACE INTO rag_cache (query_hash, query_text, result_json, expire_at) VALUES (?, ?, ?, ?)",
            (query_hash, query, json.dumps(results), expire_at),
        )

        conn.commit()
        conn.close()


def load_knowledge_files(knowledge_dir: Path) -> list[dict[str, str]]:
    """加载知识库文件"""
    documents = []

    if not knowledge_dir.exists():
        return documents

    for md_file in knowledge_dir.glob("*.md"):
        try:
            with open(md_file, encoding="utf-8", errors="ignore") as f:
                content = f.read()

            documents.append(
                {
                    "id": md_file.stem,
                    "title": md_file.stem.replace("_", " ").replace("-", " ").title(),
                    "content": content,
                    "source": str(md_file),
                }
            )
        except Exception as e:
            console.print(f"[yellow]警告: 读取 {md_file} 失败: {e}[/yellow]")

    return documents


def search_with_chroma(
    knowledge_dir: Path,
    query: str,
    top_k: int = 5,
) -> list[dict[str, Any]]:
    """使用 ChromaDB 进行向量检索"""
    try:
        import chromadb
    except ImportError:
        console.print("[yellow]ChromaDB 未安装，使用文本搜索[/yellow]")
        return search_text(knowledge_dir, query, top_k)

    # 加载文档
    documents = load_knowledge_files(knowledge_dir)

    if not documents:
        return []

    # 初始化 ChromaDB
    client = chromadb.PersistentClient(path=str(_get_cache_dir() / "chroma"))
    collection = client.get_or_create_collection("knowledge")

    # 如果集合为空，添加文档
    if collection.count() == 0:
        try:
            # 使用缓存的模型，避免重复加载
            embedding_model = get_sentence_transformer("all-MiniLM-L6-v2")

            ids = [d["id"] for d in documents]
            contents = [d["content"] for d in documents]
            embeddings = embedding_model.encode(contents).tolist()

            collection.add(
                ids=ids,
                documents=contents,
                embeddings=embeddings,
                metadatas=[{"title": d["title"], "source": d["source"]} for d in documents],
            )
        except ImportError:
            # 使用文本搜索
            return search_text(knowledge_dir, query, top_k)

    # 搜索
    try:
        # 使用缓存的模型，避免重复加载
        embedding_model = get_sentence_transformer("all-MiniLM-L6-v2")
        query_embedding = embedding_model.encode([query]).tolist()

        results = collection.query(
            query_embeddings=query_embedding,
            n_results=top_k,
        )

        # 格式化结果
        search_results = []
        if results["documents"] and results["documents"][0]:
            for i, doc in enumerate(results["documents"][0]):
                search_results.append(
                    {
                        "title": results["metadatas"][0][i].get("title", "Untitled"),
                        "content": doc,
                        "source": results["metadatas"][0][i].get("source", ""),
                        "score": 1.0
                        - (results["distances"][0][i] if results.get("distances") else 0),
                    }
                )

        return search_results

    except Exception as e:
        console.print(f"[yellow]向量搜索失败: {e}[/yellow]")
        return search_text(knowledge_dir, query, top_k)


def search_text(
    knowledge_dir: Path,
    query: str,
    top_k: int = 5,
) -> list[dict[str, Any]]:
    """简单的文本搜索（关键词匹配）"""
    documents = load_knowledge_files(knowledge_dir)

    if not documents:
        return []

    query_lower = query.lower()
    query_words = set(query_lower.split())

    results = []
    for doc in documents:
        content_lower = doc["content"].lower()

        # 计算匹配分数
        matches = 0
        for word in query_words:
            if word in content_lower:
                matches += 1

        if matches > 0:
            # 提取相关片段
            lines = doc["content"].split("\n")
            relevant_lines = []
            for line in lines:
                if any(word in line.lower() for word in query_words):
                    relevant_lines.append(line.strip())

            results.append(
                {
                    "title": doc["title"],
                    "content": "\n".join(relevant_lines[:5]),
                    "source": doc["source"],
                    "score": matches / len(query_words),
                }
            )

    # 排序并返回前 top_k 个
    results.sort(key=lambda x: x["score"], reverse=True)
    return results[:top_k]


def search_knowledge(
    config,
    query: str,
    limit: int = 5,
) -> list[dict[str, Any]]:
    """搜索知识库

    Args:
        config: KnowledgeConfig 对象
        query: 搜索查询
        limit: 返回结果数量

    Returns:
        搜索结果列表
    """
    # 优先使用 ChromaDB 向量搜索
    try:
        return search_with_chroma(
            config.knowledge_path,
            query,
            top_k=limit,
        )
    except Exception as e:
        console.print(f"[yellow]RAG 搜索失败: {e}[/yellow]")
        # 回退到文本搜索
        return search_text(config.knowledge_path, query, limit)
