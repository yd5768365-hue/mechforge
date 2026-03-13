"""
本地知识库向量检索引擎

使用 ChromaDB 实现文档的嵌入、存储和语义搜索。
支持 .txt / .md / .pdf 文件，自动分块和索引。
"""

import hashlib
import logging
import os
import re
import threading
from pathlib import Path
from typing import Any

logger = logging.getLogger("mechforge.knowledge")

_engine_lock = threading.Lock()


def _get_persist_dir() -> Path:
    if os.name == "nt":
        base = Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData" / "Local"))
    else:
        base = Path.home() / ".config"
    d = base / "mechforge" / "chroma_db"
    d.mkdir(parents=True, exist_ok=True)
    return d


def _get_knowledge_dir() -> Path:
    candidates = [
        Path(__file__).parent.parent / "knowledge",
        Path.cwd() / "knowledge",
        Path.cwd() / "gui_pywebview" / "knowledge",
    ]
    for c in candidates:
        if c.exists():
            return c
    default = Path(__file__).parent.parent / "knowledge"
    default.mkdir(parents=True, exist_ok=True)
    return default


def _chunk_text(text: str, chunk_size: int = 400, overlap: int = 80) -> list[str]:
    """将文本按段落和长度分块"""
    paragraphs = re.split(r"\n{2,}", text.strip())
    chunks: list[str] = []
    current = ""

    for para in paragraphs:
        para = para.strip()
        if not para:
            continue

        if len(current) + len(para) <= chunk_size:
            current = f"{current}\n\n{para}" if current else para
        else:
            if current:
                chunks.append(current.strip())
            if len(para) > chunk_size:
                words = para
                while len(words) > chunk_size:
                    split_pos = words.rfind("。", 0, chunk_size)
                    if split_pos < chunk_size // 2:
                        split_pos = words.rfind(".", 0, chunk_size)
                    if split_pos < chunk_size // 2:
                        split_pos = chunk_size
                    chunks.append(words[:split_pos + 1].strip())
                    words = words[max(0, split_pos + 1 - overlap):]
                current = words
            else:
                current = para

    if current.strip():
        chunks.append(current.strip())

    return [c for c in chunks if len(c) > 20]


def _read_file(path: Path) -> str | None:
    """读取文件内容"""
    suffix = path.suffix.lower()
    try:
        if suffix in (".txt", ".md"):
            return path.read_text(encoding="utf-8", errors="ignore")
        if suffix == ".pdf":
            try:
                import fitz  # PyMuPDF
                doc = fitz.open(str(path))
                text = "\n\n".join(page.get_text() for page in doc)
                doc.close()
                return text
            except ImportError:
                logger.warning("PyMuPDF 未安装，跳过 PDF 文件: %s", path.name)
                return None
    except Exception as e:
        logger.error("读取文件失败 %s: %s", path, e)
    return None


def _file_hash(path: Path) -> str:
    h = hashlib.md5()
    h.update(str(path.resolve()).encode())
    h.update(str(path.stat().st_mtime).encode())
    h.update(str(path.stat().st_size).encode())
    return h.hexdigest()


class KnowledgeEngine:
    """基于 ChromaDB 的本地知识库引擎"""

    def __init__(self):
        self._client = None
        self._collection = None
        self._ready = False
        self._indexed_files: dict[str, str] = {}
        self._doc_count = 0
        self._knowledge_dir = _get_knowledge_dir()

    def _ensure_ready(self):
        if self._ready:
            return
        with _engine_lock:
            if self._ready:
                return
            try:
                import chromadb
                persist_dir = str(_get_persist_dir())
                self._client = chromadb.PersistentClient(path=persist_dir)
                self._collection = self._client.get_or_create_collection(
                    name="mechforge_knowledge",
                    metadata={"hnsw:space": "cosine"},
                )
                self._doc_count = self._collection.count()
                self._ready = True
                logger.info(
                    "知识库引擎就绪 (ChromaDB %s, %d 条文档块, 存储: %s)",
                    chromadb.__version__, self._doc_count, persist_dir,
                )
            except Exception as e:
                logger.error("知识库引擎初始化失败: %s", e)
                raise

    @property
    def is_ready(self) -> bool:
        return self._ready

    @property
    def doc_count(self) -> int:
        if self._collection:
            self._doc_count = self._collection.count()
        return self._doc_count

    @property
    def knowledge_dir(self) -> Path:
        return self._knowledge_dir

    def index_directory(self, directory: Path | str | None = None) -> dict[str, Any]:
        """索引目录下的所有文档"""
        self._ensure_ready()
        directory = Path(directory) if directory else self._knowledge_dir

        if not directory.exists():
            return {"success": False, "error": f"目录不存在: {directory}", "files": 0, "chunks": 0}

        extensions = {".txt", ".md", ".pdf"}
        files = [f for f in directory.rglob("*") if f.suffix.lower() in extensions and f.is_file()]

        if not files:
            return {"success": True, "files": 0, "chunks": 0, "message": "目录中无可索引文件"}

        total_chunks = 0
        indexed_files = 0
        skipped = 0

        for file_path in files:
            fhash = _file_hash(file_path)
            if self._indexed_files.get(str(file_path)) == fhash:
                skipped += 1
                continue

            text = _read_file(file_path)
            if not text or len(text.strip()) < 50:
                continue

            chunks = _chunk_text(text)
            if not chunks:
                continue

            self._remove_file_docs(str(file_path))

            ids = [f"{file_path.stem}_{i}_{fhash[:8]}" for i in range(len(chunks))]
            metadatas = [
                {
                    "source": file_path.name,
                    "file_path": str(file_path.resolve()),
                    "chunk_index": i,
                    "total_chunks": len(chunks),
                }
                for i in range(len(chunks))
            ]

            batch_size = 50
            for start in range(0, len(chunks), batch_size):
                end = min(start + batch_size, len(chunks))
                self._collection.add(
                    ids=ids[start:end],
                    documents=chunks[start:end],
                    metadatas=metadatas[start:end],
                )

            self._indexed_files[str(file_path)] = fhash
            total_chunks += len(chunks)
            indexed_files += 1
            logger.info("已索引: %s (%d 块)", file_path.name, len(chunks))

        self._doc_count = self._collection.count()

        return {
            "success": True,
            "files": indexed_files,
            "chunks": total_chunks,
            "skipped": skipped,
            "total_in_db": self._doc_count,
            "directory": str(directory),
        }

    def _remove_file_docs(self, file_path: str):
        """移除某个文件的所有文档块"""
        if not self._collection:
            return
        try:
            results = self._collection.get(
                where={"file_path": file_path},
            )
            if results and results["ids"]:
                self._collection.delete(ids=results["ids"])
        except Exception:
            pass

    def search(self, query: str, top_k: int = 5) -> list[dict[str, Any]]:
        """语义搜索"""
        self._ensure_ready()

        if not query.strip():
            return []

        if self._collection.count() == 0:
            return []

        try:
            results = self._collection.query(
                query_texts=[query],
                n_results=min(top_k, self._collection.count()),
                include=["documents", "metadatas", "distances"],
            )
        except Exception as e:
            logger.error("向量搜索失败: %s", e)
            return []

        items: list[dict[str, Any]] = []
        if not results or not results.get("ids") or not results["ids"][0]:
            return items

        for i, doc_id in enumerate(results["ids"][0]):
            doc = results["documents"][0][i] if results.get("documents") else ""
            meta = results["metadatas"][0][i] if results.get("metadatas") else {}
            distance = results["distances"][0][i] if results.get("distances") else 1.0

            score = max(0, 1.0 - distance)

            items.append({
                "id": doc_id,
                "content": doc,
                "score": round(score, 4),
                "source": meta.get("source", "unknown"),
                "file_path": meta.get("file_path", ""),
                "chunk_index": meta.get("chunk_index", 0),
                "total_chunks": meta.get("total_chunks", 1),
            })

        return items

    def get_stats(self) -> dict[str, Any]:
        """获取知识库统计信息"""
        self._ensure_ready()
        return {
            "ready": self._ready,
            "doc_count": self.doc_count,
            "indexed_files": len(self._indexed_files),
            "knowledge_dir": str(self._knowledge_dir),
            "persist_dir": str(_get_persist_dir()),
        }

    def list_sources(self) -> list[dict[str, Any]]:
        """列出所有已索引的文件源"""
        self._ensure_ready()
        sources: dict[str, dict[str, Any]] = {}

        if self._collection.count() == 0:
            return []

        try:
            all_data = self._collection.get(include=["metadatas"])
            for meta in all_data.get("metadatas", []):
                src = meta.get("source", "unknown")
                if src not in sources:
                    sources[src] = {
                        "source": src,
                        "file_path": meta.get("file_path", ""),
                        "chunks": 0,
                    }
                sources[src]["chunks"] += 1
        except Exception as e:
            logger.error("列出文档源失败: %s", e)

        return list(sources.values())

    def clear(self) -> dict[str, Any]:
        """清空知识库"""
        self._ensure_ready()
        try:
            self._client.delete_collection("mechforge_knowledge")
            self._collection = self._client.get_or_create_collection(
                name="mechforge_knowledge",
                metadata={"hnsw:space": "cosine"},
            )
            self._indexed_files.clear()
            self._doc_count = 0
            logger.info("知识库已清空")
            return {"success": True, "message": "知识库已清空"}
        except Exception as e:
            logger.error("清空知识库失败: %s", e)
            return {"success": False, "error": str(e)}


_engine_instance: KnowledgeEngine | None = None


def get_knowledge_engine() -> KnowledgeEngine:
    global _engine_instance
    if _engine_instance is None:
        _engine_instance = KnowledgeEngine()
    return _engine_instance
