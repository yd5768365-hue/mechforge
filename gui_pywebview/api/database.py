"""
数据库模块
提供 SQLite 数据库连接和 ORM 功能
"""

import json
import logging
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Any

logger = logging.getLogger("mechforge.database")

# 数据库路径
DB_DIR = Path.home() / ".mechforge"
DB_PATH = DB_DIR / "mechforge.db"


def init_database() -> None:
    """初始化数据库"""
    DB_DIR.mkdir(parents=True, exist_ok=True)

    with get_connection() as conn:
        cursor = conn.cursor()

        # 创建对话历史表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                message_count INTEGER DEFAULT 0,
                metadata TEXT
            )
        """)

        # 创建消息表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                conversation_id INTEGER NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                model TEXT,
                rag_used BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE CASCADE
            )
        """)

        # 创建设置表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 创建知识库文档表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS knowledge_docs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT NOT NULL,
                filepath TEXT NOT NULL,
                file_size INTEGER,
                doc_hash TEXT UNIQUE,
                processed BOOLEAN DEFAULT FALSE,
                chunk_count INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 创建索引
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_messages_conversation
            ON messages(conversation_id)
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_messages_created
            ON messages(created_at)
        """)

        conn.commit()
        logger.info("Database initialized")


@contextmanager
def get_connection():
    """获取数据库连接"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


class ConversationDB:
    """对话数据库操作"""

    @staticmethod
    def create(title: str, metadata: dict | None = None) -> int:
        """创建新对话"""
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO conversations (title, metadata) VALUES (?, ?)",
                (title, json.dumps(metadata) if metadata else None),
            )
            conn.commit()
            return cursor.lastrowid

    @staticmethod
    def get(conversation_id: int) -> dict | None:
        """获取对话"""
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM conversations WHERE id = ?", (conversation_id,))
            row = cursor.fetchone()
            if row:
                return dict(row)
            return None

    @staticmethod
    def list_all(limit: int = 100, offset: int = 0) -> list[dict]:
        """列出所有对话"""
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT * FROM conversations
                ORDER BY updated_at DESC
                LIMIT ? OFFSET ?
                """,
                (limit, offset),
            )
            return [dict(row) for row in cursor.fetchall()]

    @staticmethod
    def update(conversation_id: int, title: str | None = None) -> bool:
        """更新对话"""
        with get_connection() as conn:
            cursor = conn.cursor()
            if title:
                cursor.execute(
                    """
                    UPDATE conversations
                    SET title = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                    """,
                    (title, conversation_id),
                )
            conn.commit()
            return cursor.rowcount > 0

    @staticmethod
    def delete(conversation_id: int) -> bool:
        """删除对话"""
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM conversations WHERE id = ?", (conversation_id,))
            conn.commit()
            return cursor.rowcount > 0


class MessageDB:
    """消息数据库操作"""

    @staticmethod
    def create(
        conversation_id: int,
        role: str,
        content: str,
        model: str | None = None,
        rag_used: bool = False,
    ) -> int:
        """创建新消息"""
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO messages
                (conversation_id, role, content, model, rag_used)
                VALUES (?, ?, ?, ?, ?)
                """,
                (conversation_id, role, content, model, rag_used),
            )

            # 更新对话消息数
            cursor.execute(
                """
                UPDATE conversations
                SET message_count = message_count + 1,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
                """,
                (conversation_id,),
            )

            conn.commit()
            return cursor.lastrowid

    @staticmethod
    def get_by_conversation(conversation_id: int) -> list[dict]:
        """获取对话的所有消息"""
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT * FROM messages
                WHERE conversation_id = ?
                ORDER BY created_at ASC
                """,
                (conversation_id,),
            )
            return [dict(row) for row in cursor.fetchall()]

    @staticmethod
    def delete_by_conversation(conversation_id: int) -> int:
        """删除对话的所有消息"""
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM messages WHERE conversation_id = ?", (conversation_id,))
            conn.commit()
            return cursor.rowcount


class SettingsDB:
    """设置数据库操作"""

    @staticmethod
    def get(key: str, default: Any = None) -> Any:
        """获取设置"""
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT value FROM settings WHERE key = ?", (key,))
            row = cursor.fetchone()
            if row:
                try:
                    return json.loads(row[0])
                except json.JSONDecodeError:
                    return row[0]
            return default

    @staticmethod
    def set(key: str, value: Any) -> None:
        """设置值"""
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT OR REPLACE INTO settings (key, value, updated_at)
                VALUES (?, ?, CURRENT_TIMESTAMP)
                """,
                (key, json.dumps(value)),
            )
            conn.commit()

    @staticmethod
    def delete(key: str) -> bool:
        """删除设置"""
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM settings WHERE key = ?", (key,))
            conn.commit()
            return cursor.rowcount > 0

    @staticmethod
    def get_all() -> dict[str, Any]:
        """获取所有设置"""
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT key, value FROM settings")
            result = {}
            for row in cursor.fetchall():
                try:
                    result[row[0]] = json.loads(row[1])
                except json.JSONDecodeError:
                    result[row[0]] = row[1]
            return result


class KnowledgeDocDB:
    """知识库文档数据库操作"""

    @staticmethod
    def create(filename: str, filepath: str, file_size: int, doc_hash: str) -> int:
        """创建文档记录"""
        with get_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute(
                    """
                    INSERT INTO knowledge_docs
                    (filename, filepath, file_size, doc_hash)
                    VALUES (?, ?, ?, ?)
                    """,
                    (filename, filepath, file_size, doc_hash),
                )
                conn.commit()
                return cursor.lastrowid
            except sqlite3.IntegrityError:
                # 文档已存在
                return -1

    @staticmethod
    def get_by_hash(doc_hash: str) -> dict | None:
        """通过哈希获取文档"""
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM knowledge_docs WHERE doc_hash = ?", (doc_hash,))
            row = cursor.fetchone()
            return dict(row) if row else None

    @staticmethod
    def list_all(processed_only: bool = False) -> list[dict]:
        """列出所有文档"""
        with get_connection() as conn:
            cursor = conn.cursor()
            if processed_only:
                cursor.execute("SELECT * FROM knowledge_docs WHERE processed = 1")
            else:
                cursor.execute("SELECT * FROM knowledge_docs")
            return [dict(row) for row in cursor.fetchall()]

    @staticmethod
    def mark_processed(doc_id: int, chunk_count: int) -> bool:
        """标记文档为已处理"""
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                UPDATE knowledge_docs
                SET processed = TRUE, chunk_count = ?
                WHERE id = ?
                """,
                (chunk_count, doc_id),
            )
            conn.commit()
            return cursor.rowcount > 0

    @staticmethod
    def delete(doc_id: int) -> bool:
        """删除文档"""
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM knowledge_docs WHERE id = ?", (doc_id,))
            conn.commit()
            return cursor.rowcount > 0


# 初始化数据库
init_database()
