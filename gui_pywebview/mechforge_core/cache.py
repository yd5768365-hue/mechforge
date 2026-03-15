"""
MechForge Cache System

提供多级缓存支持:
- L1: 内存缓存 (LRU)
- L2: 磁盘缓存 (SQLite/JSON)
- L3: 分布式缓存 (Redis, 可选)

特性:
- TTL (Time To Live) 支持
n- 缓存预热
- 缓存统计
- 自动序列化/反序列化
- 线程安全
"""

import hashlib
import pickle
import sqlite3
import threading
import time
from abc import ABC, abstractmethod
from collections.abc import Callable
from dataclasses import dataclass, field
from functools import wraps
from pathlib import Path
from typing import Generic, TypeVar

T = TypeVar("T")


@dataclass
class CacheEntry(Generic[T]):
    """缓存条目"""

    value: T
    created_at: float = field(default_factory=time.time)
    expires_at: float | None = None
    access_count: int = 0
    last_accessed: float = field(default_factory=time.time)

    def is_expired(self) -> bool:
        """检查是否过期"""
        if self.expires_at is None:
            return False
        return time.time() > self.expires_at


@dataclass
class CacheStats:
    """缓存统计信息"""

    hits: int = 0
    misses: int = 0
    evictions: int = 0
    total_entries: int = 0
    memory_usage: int = 0  # bytes

    @property
    def hit_rate(self) -> float:
        """命中率"""
        total = self.hits + self.misses
        return self.hits / total if total > 0 else 0.0


class CacheBackend(ABC, Generic[T]):
    """缓存后端抽象基类"""

    @abstractmethod
    def get(self, key: str) -> CacheEntry[T] | None:
        """获取缓存值"""
        pass

    @abstractmethod
    def set(
        self,
        key: str,
        value: T,
        ttl: int | None = None,
    ) -> None:
        """设置缓存值"""
        pass

    @abstractmethod
    def delete(self, key: str) -> bool:
        """删除缓存值"""
        pass

    @abstractmethod
    def clear(self) -> None:
        """清空缓存"""
        pass

    @abstractmethod
    def keys(self) -> list[str]:
        """获取所有键"""
        pass

    @abstractmethod
    def stats(self) -> CacheStats:
        """获取统计信息"""
        pass


class MemoryCache(CacheBackend[T]):
    """
    内存缓存 (L1)

    基于字典 + LRU 淘汰策略
    """

    def __init__(
        self,
        max_size: int = 1000,
        default_ttl: int | None = None,
    ):
        self.max_size = max_size
        self.default_ttl = default_ttl
        self._cache: dict[str, CacheEntry[T]] = {}
        self._lock = threading.RLock()
        self._stats = CacheStats()

    def get(self, key: str) -> CacheEntry[T] | None:
        with self._lock:
            entry = self._cache.get(key)
            if entry is None:
                self._stats.misses += 1
                return None

            if entry.is_expired():
                del self._cache[key]
                self._stats.evictions += 1
                self._stats.misses += 1
                return None

            entry.access_count += 1
            entry.last_accessed = time.time()
            self._stats.hits += 1
            return entry

    def set(
        self,
        key: str,
        value: T,
        ttl: int | None = None,
    ) -> None:
        with self._lock:
            # 淘汰策略: 如果满了,删除最久未使用的
            if len(self._cache) >= self.max_size and key not in self._cache:
                self._evict_lru()

            ttl = ttl or self.default_ttl
            expires_at = time.time() + ttl if ttl else None

            self._cache[key] = CacheEntry(
                value=value,
                expires_at=expires_at,
            )
            self._stats.total_entries = len(self._cache)

    def delete(self, key: str) -> bool:
        with self._lock:
            if key in self._cache:
                del self._cache[key]
                self._stats.total_entries = len(self._cache)
                return True
            return False

    def clear(self) -> None:
        with self._lock:
            self._cache.clear()
            self._stats.total_entries = 0

    def keys(self) -> list[str]:
        with self._lock:
            return list(self._cache.keys())

    def stats(self) -> CacheStats:
        with self._lock:
            stats = CacheStats(
                hits=self._stats.hits,
                misses=self._stats.misses,
                evictions=self._stats.evictions,
                total_entries=len(self._cache),
            )
            # 估算内存使用
            stats.memory_usage = sum(
                len(pickle.dumps(entry.value)) for entry in self._cache.values()
            )
            return stats

    def _evict_lru(self) -> None:
        """LRU 淘汰"""
        if not self._cache:
            return

        # 找到最久未访问的
        lru_key = min(
            self._cache.keys(),
            key=lambda k: self._cache[k].last_accessed,
        )
        del self._cache[lru_key]
        self._stats.evictions += 1


class DiskCache(CacheBackend[T]):
    """
    磁盘缓存 (L2)

    基于 SQLite 实现
    """

    def __init__(
        self,
        cache_dir: str | Path | None = None,
        default_ttl: int | None = None,
    ):
        if cache_dir is None:
            cache_dir = Path.home() / ".mechforge" / "cache"

        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.default_ttl = default_ttl
        self._db_path = self.cache_dir / "cache.db"
        self._lock = threading.RLock()
        self._stats = CacheStats()
        self._init_db()

    def _init_db(self) -> None:
        """初始化数据库"""
        with sqlite3.connect(self._db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS cache (
                    key TEXT PRIMARY KEY,
                    value BLOB NOT NULL,
                    created_at REAL NOT NULL,
                    expires_at REAL,
                    access_count INTEGER DEFAULT 0,
                    last_accessed REAL NOT NULL
                )
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_expires ON cache(expires_at)
            """)
            conn.commit()

    def get(self, key: str) -> CacheEntry[T] | None:
        with self._lock, sqlite3.connect(self._db_path) as conn:
            cursor = conn.execute(
                "SELECT value, created_at, expires_at, access_count, last_accessed FROM cache WHERE key = ?",
                (key,),
            )
            row = cursor.fetchone()

            if row is None:
                self._stats.misses += 1
                return None

            value_blob, created_at, expires_at, access_count, last_accessed = row

            # 检查过期
            if expires_at and time.time() > expires_at:
                conn.execute("DELETE FROM cache WHERE key = ?", (key,))
                conn.commit()
                self._stats.evictions += 1
                self._stats.misses += 1
                return None

            # 更新访问统计
            conn.execute(
                "UPDATE cache SET access_count = access_count + 1, last_accessed = ? WHERE key = ?",
                (time.time(), key),
            )
            conn.commit()

            try:
                value = pickle.loads(value_blob)
            except Exception:
                self._stats.misses += 1
                return None

            self._stats.hits += 1
            return CacheEntry(
                value=value,
                created_at=created_at,
                expires_at=expires_at,
                access_count=access_count + 1,
                last_accessed=time.time(),
            )

    def set(
        self,
        key: str,
        value: T,
        ttl: int | None = None,
    ) -> None:
        with self._lock:
            ttl = ttl or self.default_ttl
            expires_at = time.time() + ttl if ttl else None
            created_at = time.time()

            try:
                value_blob = pickle.dumps(value)
            except Exception as e:
                raise ValueError(f"Cannot serialize value: {e}") from e

            with sqlite3.connect(self._db_path) as conn:
                conn.execute(
                    """
                    INSERT OR REPLACE INTO cache (key, value, created_at, expires_at, last_accessed)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (key, value_blob, created_at, expires_at, created_at),
                )
                conn.commit()

    def delete(self, key: str) -> bool:
        with self._lock, sqlite3.connect(self._db_path) as conn:
            cursor = conn.execute("DELETE FROM cache WHERE key = ?", (key,))
            conn.commit()
            return cursor.rowcount > 0

    def clear(self) -> None:
        with self._lock, sqlite3.connect(self._db_path) as conn:
            conn.execute("DELETE FROM cache")
            conn.commit()

    def keys(self) -> list[str]:
        with self._lock, sqlite3.connect(self._db_path) as conn:
            cursor = conn.execute("SELECT key FROM cache")
            return [row[0] for row in cursor.fetchall()]

    def stats(self) -> CacheStats:
        with self._lock:
            with sqlite3.connect(self._db_path) as conn:
                cursor = conn.execute("SELECT COUNT(*), SUM(LENGTH(value)) FROM cache")
                total_entries, memory_usage = cursor.fetchone()

            return CacheStats(
                hits=self._stats.hits,
                misses=self._stats.misses,
                evictions=self._stats.evictions,
                total_entries=total_entries or 0,
                memory_usage=memory_usage or 0,
            )

    def cleanup_expired(self) -> int:
        """清理过期条目,返回清理数量"""
        with self._lock, sqlite3.connect(self._db_path) as conn:
            cursor = conn.execute(
                "DELETE FROM cache WHERE expires_at IS NOT NULL AND expires_at < ?",
                (time.time(),),
            )
            conn.commit()
            return cursor.rowcount


class MultiLevelCache(CacheBackend[T]):
    """
    多级缓存 (L1 + L2)

    写入: L1 -> L2
    读取: L1 -> L2 (如果L2命中,回填L1)
    """

    def __init__(
        self,
        l1_cache: MemoryCache[T] | None = None,
        l2_cache: DiskCache[T] | None = None,
    ):
        self.l1 = l1_cache or MemoryCache()
        self.l2 = l2_cache or DiskCache()

    def get(self, key: str) -> CacheEntry[T] | None:
        # 先查 L1
        entry = self.l1.get(key)
        if entry is not None:
            return entry

        # 再查 L2
        entry = self.l2.get(key)
        if entry is not None:
            # 回填 L1
            self.l1.set(key, entry.value, ttl=300)  # L1 默认5分钟
            return entry

        return None

    def set(
        self,
        key: str,
        value: T,
        ttl: int | None = None,
    ) -> None:
        # 写入两级缓存
        self.l1.set(key, value, ttl=ttl)
        self.l2.set(key, value, ttl=ttl)

    def delete(self, key: str) -> bool:
        l1_deleted = self.l1.delete(key)
        l2_deleted = self.l2.delete(key)
        return l1_deleted or l2_deleted

    def clear(self) -> None:
        self.l1.clear()
        self.l2.clear()

    def keys(self) -> list[str]:
        # 合并两级缓存的键
        l1_keys = set(self.l1.keys())
        l2_keys = set(self.l2.keys())
        return list(l1_keys | l2_keys)

    def stats(self) -> CacheStats:
        l1_stats = self.l1.stats()
        l2_stats = self.l2.stats()

        return CacheStats(
            hits=l1_stats.hits + l2_stats.hits,
            misses=l1_stats.misses,
            evictions=l1_stats.evictions + l2_stats.evictions,
            total_entries=l1_stats.total_entries + l2_stats.total_entries,
            memory_usage=l1_stats.memory_usage + l2_stats.memory_usage,
        )


def cached(
    ttl: int | None = None,
    key_prefix: str = "",
    cache: CacheBackend | None = None,
):
    """
    缓存装饰器

    示例:
        @cached(ttl=300, key_prefix="llm:")
        def expensive_function(x, y):
            return x + y
    """

    def decorator(func: Callable) -> Callable:
        _cache = cache or _default_cache

        @wraps(func)
        def wrapper(*args, **kwargs):
            # 生成缓存键
            key_parts = [key_prefix, func.__name__]
            key_parts.extend(str(arg) for arg in args)
            key_parts.extend(f"{k}={v}" for k, v in sorted(kwargs.items()))
            key = hashlib.md5("|".join(key_parts).encode()).hexdigest()

            # 尝试从缓存获取
            entry = _cache.get(key)
            if entry is not None:
                return entry.value

            # 执行函数
            result = func(*args, **kwargs)

            # 存入缓存
            _cache.set(key, result, ttl=ttl)

            return result

        # 添加缓存控制方法
        wrapper.cache_clear = lambda: _cache.clear()
        wrapper.cache_info = lambda: _cache.stats()

        return wrapper

    return decorator


# 全局默认缓存实例
_default_cache: MultiLevelCache = MultiLevelCache()


def get_cache() -> MultiLevelCache:
    """获取全局缓存实例"""
    return _default_cache


def set_default_cache(cache: MultiLevelCache) -> None:
    """设置全局默认缓存"""
    global _default_cache
    _default_cache = cache
