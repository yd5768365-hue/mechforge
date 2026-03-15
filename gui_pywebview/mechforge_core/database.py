"""
MechForge Database System

基于 SQLite 的数据库支持:
- 对话历史存储
- 配置持久化
- 知识库元数据索引
- 用户偏好设置

特性:
- 连接池
- 自动迁移
- ORM 风格接口
- 事务支持
"""

import json
import sqlite3
import threading
import uuid
from contextlib import contextmanager
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, TypeVar

T = TypeVar("T")


class DatabaseError(Exception):
    """数据库错误"""

    pass


class MigrationError(DatabaseError):
    """迁移错误"""

    pass


@dataclass
class Conversation:
    """对话记录"""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    session_id: str = ""
    role: str = ""  # user, assistant, system
    content: str = ""
    model: str = ""
    provider: str = ""
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: dict[str, Any] = field(default_factory=dict)
    tokens_input: int = 0
    tokens_output: int = 0
    latency_ms: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "session_id": self.session_id,
            "role": self.role,
            "content": self.content,
            "model": self.model,
            "provider": self.provider,
            "timestamp": self.timestamp.isoformat(),
            "metadata": json.dumps(self.metadata),
            "tokens_input": self.tokens_input,
            "tokens_output": self.tokens_output,
            "latency_ms": self.latency_ms,
        }

    @classmethod
    def from_row(cls, row: sqlite3.Row) -> "Conversation":
        return cls(
            id=row["id"],
            session_id=row["session_id"],
            role=row["role"],
            content=row["content"],
            model=row["model"],
            provider=row["provider"],
            timestamp=datetime.fromisoformat(row["timestamp"]),
            metadata=json.loads(row["metadata"]) if row["metadata"] else {},
            tokens_input=row["tokens_input"],
            tokens_output=row["tokens_output"],
            latency_ms=row["latency_ms"],
        )


@dataclass
class KnowledgeDocument:
    """知识库文档元数据"""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    path: str = ""
    title: str = ""
    content_hash: str = ""
    doc_type: str = ""  # markdown, pdf, txt, etc.
    chunk_count: int = 0
    vector_ids: list[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "path": self.path,
            "title": self.title,
            "content_hash": self.content_hash,
            "doc_type": self.doc_type,
            "chunk_count": self.chunk_count,
            "vector_ids": json.dumps(self.vector_ids),
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "metadata": json.dumps(self.metadata),
        }

    @classmethod
    def from_row(cls, row: sqlite3.Row) -> "KnowledgeDocument":
        return cls(
            id=row["id"],
            path=row["path"],
            title=row["title"],
            content_hash=row["content_hash"],
            doc_type=row["doc_type"],
            chunk_count=row["chunk_count"],
            vector_ids=json.loads(row["vector_ids"]) if row["vector_ids"] else [],
            created_at=datetime.fromisoformat(row["created_at"]),
            updated_at=datetime.fromisoformat(row["updated_at"]),
            metadata=json.loads(row["metadata"]) if row["metadata"] else {},
        )


@dataclass
class UserPreference:
    """用户偏好设置"""

    key: str = ""
    value: Any = None
    category: str = "general"  # general, ui, model, etc.
    updated_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> dict[str, Any]:
        return {
            "key": self.key,
            "value": json.dumps(self.value),
            "category": self.category,
            "updated_at": self.updated_at.isoformat(),
        }

    @classmethod
    def from_row(cls, row: sqlite3.Row) -> "UserPreference":
        return cls(
            key=row["key"],
            value=json.loads(row["value"]),
            category=row["category"],
            updated_at=datetime.fromisoformat(row["updated_at"]),
        )


class Database:
    """
    MechForge 数据库管理器

    使用示例:
        db = Database()

        # 保存对话
        db.save_conversation(Conversation(...))

        # 查询历史
        history = db.get_conversation_history(session_id="xxx")

        # 知识库管理
        db.add_knowledge_document(KnowledgeDocument(...))
    """

    SCHEMA_VERSION = 1

    def __init__(
        self,
        db_path: str | Path | None = None,
    ):
        if db_path is None:
            db_path = Path.home() / ".mechforge" / "mechforge.db"

        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._local = threading.local()
        self._lock = threading.RLock()

        # 初始化数据库
        self._init_database()

    def _get_connection(self) -> sqlite3.Connection:
        """获取线程本地连接"""
        if not hasattr(self._local, "connection") or self._local.connection is None:
            self._local.connection = sqlite3.connect(
                self.db_path,
                check_same_thread=False,
            )
            self._local.connection.row_factory = sqlite3.Row
        return self._local.connection

    @contextmanager
    def transaction(self):
        """事务上下文管理器"""
        conn = self._get_connection()
        with self._lock:
            try:
                conn.execute("BEGIN")
                yield conn
                conn.commit()
            except Exception as e:
                conn.rollback()
                raise DatabaseError(f"Transaction failed: {e}") from e

    def _init_database(self) -> None:
        """初始化数据库表结构"""
        with self._lock:
            conn = self._get_connection()

            # 元数据表
            conn.execute("""
                CREATE TABLE IF NOT EXISTS metadata (
                    key TEXT PRIMARY KEY,
                    value TEXT
                )
            """)

            # 对话历史表
            conn.execute("""
                CREATE TABLE IF NOT EXISTS conversations (
                    id TEXT PRIMARY KEY,
                    session_id TEXT NOT NULL,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    model TEXT,
                    provider TEXT,
                    timestamp TEXT NOT NULL,
                    metadata TEXT,
                    tokens_input INTEGER DEFAULT 0,
                    tokens_output INTEGER DEFAULT 0,
                    latency_ms REAL DEFAULT 0
                )
            """)

            # 会话表
            conn.execute("""
                CREATE TABLE IF NOT EXISTS sessions (
                    id TEXT PRIMARY KEY,
                    title TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    message_count INTEGER DEFAULT 0,
                    metadata TEXT
                )
            """)

            # 知识库文档表
            conn.execute("""
                CREATE TABLE IF NOT EXISTS knowledge_documents (
                    id TEXT PRIMARY KEY,
                    path TEXT UNIQUE NOT NULL,
                    title TEXT,
                    content_hash TEXT,
                    doc_type TEXT,
                    chunk_count INTEGER DEFAULT 0,
                    vector_ids TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    metadata TEXT
                )
            """)

            # 用户偏好设置表
            conn.execute("""
                CREATE TABLE IF NOT EXISTS user_preferences (
                    key TEXT PRIMARY KEY,
                    value TEXT,
                    category TEXT DEFAULT 'general',
                    updated_at TEXT NOT NULL
                )
            """)

            # 创建索引
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_conversations_session
                ON conversations(session_id, timestamp)
            """)

            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_knowledge_path
                ON knowledge_documents(path)
            """)

            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_preferences_category
                ON user_preferences(category)
            """)

            # 设置 schema 版本
            conn.execute(
                "INSERT OR REPLACE INTO metadata (key, value) VALUES (?, ?)",
                ("schema_version", str(self.SCHEMA_VERSION)),
            )

            conn.commit()

    # ==================== 对话历史 ====================

    def save_conversation(self, conv: Conversation) -> None:
        """保存对话记录"""
        with self.transaction() as conn:
            conn.execute(
                """
                INSERT INTO conversations
                (id, session_id, role, content, model, provider, timestamp,
                 metadata, tokens_input, tokens_output, latency_ms)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    conv.id,
                    conv.session_id,
                    conv.role,
                    conv.content,
                    conv.model,
                    conv.provider,
                    conv.timestamp.isoformat(),
                    json.dumps(conv.metadata),
                    conv.tokens_input,
                    conv.tokens_output,
                    conv.latency_ms,
                ),
            )

            # 更新会话统计
            conn.execute(
                """
                INSERT INTO sessions (id, title, created_at, updated_at, message_count)
                VALUES (?, ?, ?, ?, 1)
                ON CONFLICT(id) DO UPDATE SET
                    updated_at = excluded.updated_at,
                    message_count = message_count + 1
                """,
                (
                    conv.session_id,
                    conv.content[:50],
                    conv.timestamp.isoformat(),
                    conv.timestamp.isoformat(),
                ),
            )

    def get_conversation_history(
        self,
        session_id: str,
        limit: int = 100,
        offset: int = 0,
    ) -> list[Conversation]:
        """获取对话历史"""
        conn = self._get_connection()
        cursor = conn.execute(
            """
            SELECT * FROM conversations
            WHERE session_id = ?
            ORDER BY timestamp DESC
            LIMIT ? OFFSET ?
            """,
            (session_id, limit, offset),
        )
        return [Conversation.from_row(row) for row in cursor.fetchall()]

    def get_all_sessions(
        self,
        limit: int = 50,
        offset: int = 0,
    ) -> list[dict[str, Any]]:
        """获取所有会话列表"""
        conn = self._get_connection()
        cursor = conn.execute(
            """
            SELECT * FROM sessions
            ORDER BY updated_at DESC
            LIMIT ? OFFSET ?
            """,
            (limit, offset),
        )
        return [dict(row) for row in cursor.fetchall()]

    def delete_session(self, session_id: str) -> bool:
        """删除会话及其所有对话"""
        with self.transaction() as conn:
            conn.execute("DELETE FROM conversations WHERE session_id = ?", (session_id,))
            cursor = conn.execute("DELETE FROM sessions WHERE id = ?", (session_id,))
            return cursor.rowcount > 0

    def search_conversations(
        self,
        query: str,
        session_id: str | None = None,
        limit: int = 20,
    ) -> list[Conversation]:
        """搜索对话内容"""
        conn = self._get_connection()

        if session_id:
            cursor = conn.execute(
                """
                SELECT * FROM conversations
                WHERE session_id = ? AND content LIKE ?
                ORDER BY timestamp DESC
                LIMIT ?
                """,
                (session_id, f"%{query}%", limit),
            )
        else:
            cursor = conn.execute(
                """
                SELECT * FROM conversations
                WHERE content LIKE ?
                ORDER BY timestamp DESC
                LIMIT ?
                """,
                (f"%{query}%", limit),
            )

        return [Conversation.from_row(row) for row in cursor.fetchall()]

    # ==================== 知识库管理 ====================

    def add_knowledge_document(self, doc: KnowledgeDocument) -> None:
        """添加知识库文档"""
        with self.transaction() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO knowledge_documents
                (id, path, title, content_hash, doc_type, chunk_count, vector_ids,
                 created_at, updated_at, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    doc.id,
                    doc.path,
                    doc.title,
                    doc.content_hash,
                    doc.doc_type,
                    doc.chunk_count,
                    json.dumps(doc.vector_ids),
                    doc.created_at.isoformat(),
                    doc.updated_at.isoformat(),
                    json.dumps(doc.metadata),
                ),
            )

    def get_knowledge_document(self, path: str) -> KnowledgeDocument | None:
        """获取知识库文档"""
        conn = self._get_connection()
        cursor = conn.execute(
            "SELECT * FROM knowledge_documents WHERE path = ?",
            (path,),
        )
        row = cursor.fetchone()
        return KnowledgeDocument.from_row(row) if row else None

    def list_knowledge_documents(
        self,
        doc_type: str | None = None,
        limit: int = 100,
    ) -> list[KnowledgeDocument]:
        """列出所有知识库文档"""
        conn = self._get_connection()

        if doc_type:
            cursor = conn.execute(
                "SELECT * FROM knowledge_documents WHERE doc_type = ? LIMIT ?",
                (doc_type, limit),
            )
        else:
            cursor = conn.execute(
                "SELECT * FROM knowledge_documents LIMIT ?",
                (limit,),
            )

        return [KnowledgeDocument.from_row(row) for row in cursor.fetchall()]

    def delete_knowledge_document(self, path: str) -> bool:
        """删除知识库文档"""
        with self.transaction() as conn:
            cursor = conn.execute(
                "DELETE FROM knowledge_documents WHERE path = ?",
                (path,),
            )
            return cursor.rowcount > 0

    def update_document_hash(self, path: str, content_hash: str) -> bool:
        """更新文档哈希值"""
        with self.transaction() as conn:
            cursor = conn.execute(
                """
                UPDATE knowledge_documents
                SET content_hash = ?, updated_at = ?
                WHERE path = ?
                """,
                (content_hash, datetime.now().isoformat(), path),
            )
            return cursor.rowcount > 0

    # ==================== 用户偏好设置 ====================

    def set_preference(self, key: str, value: Any, category: str = "general") -> None:
        """设置用户偏好"""
        with self.transaction() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO user_preferences (key, value, category, updated_at)
                VALUES (?, ?, ?, ?)
                """,
                (key, json.dumps(value), category, datetime.now().isoformat()),
            )

    def get_preference(self, key: str, default: Any = None) -> Any:
        """获取用户偏好"""
        conn = self._get_connection()
        cursor = conn.execute(
            "SELECT value FROM user_preferences WHERE key = ?",
            (key,),
        )
        row = cursor.fetchone()
        if row:
            return json.loads(row["value"])
        return default

    def get_preferences_by_category(self, category: str) -> dict[str, Any]:
        """获取某类别的所有偏好"""
        conn = self._get_connection()
        cursor = conn.execute(
            "SELECT key, value FROM user_preferences WHERE category = ?",
            (category,),
        )
        return {row["key"]: json.loads(row["value"]) for row in cursor.fetchall()}

    def delete_preference(self, key: str) -> bool:
        """删除用户偏好"""
        with self.transaction() as conn:
            cursor = conn.execute(
                "DELETE FROM user_preferences WHERE key = ?",
                (key,),
            )
            return cursor.rowcount > 0

    # ==================== 统计和工具 ====================

    def get_stats(self) -> dict[str, Any]:
        """获取数据库统计信息"""
        conn = self._get_connection()
        stats = {}

        # 表统计
        for table in ["conversations", "sessions", "knowledge_documents", "user_preferences"]:
            cursor = conn.execute(f"SELECT COUNT(*) FROM {table}")
            stats[f"{table}_count"] = cursor.fetchone()[0]

        # 数据库大小
        stats["db_size_bytes"] = self.db_path.stat().st_size

        return stats

    def vacuum(self) -> None:
        """优化数据库"""
        with self._lock:
            conn = self._get_connection()
            conn.execute("VACUUM")

    def close(self) -> None:
        """关闭数据库连接"""
        if hasattr(self._local, "connection") and self._local.connection:
            self._local.connection.close()
            self._local.connection = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


# 全局数据库实例
_db_instance: Database | None = None
_db_lock = threading.Lock()


def get_database(db_path: str | Path | None = None) -> Database:
    """获取全局数据库实例 (单例)"""
    global _db_instance
    if _db_instance is None:
        with _db_lock:
            if _db_instance is None:
                _db_instance = Database(db_path)
    return _db_instance


def reset_database() -> None:
    """重置数据库实例 (主要用于测试)"""
    global _db_instance
    with _db_lock:
        if _db_instance:
            _db_instance.close()
        _db_instance = None
