"""
测试 MechForge Core 新功能
"""

import time

import pytest

from mechforge_core import (
    CacheStats,
    Conversation,
    Database,
    DiskCache,
    KnowledgeDocument,
    MemoryCache,
    MultiLevelCache,
    RateLimitConfig,
    RateLimiter,
    cached,
    lazy_import,
    lazy_load,
)
from mechforge_core.security import (
    APITokenManager,
    InputValidator,
    IPFilter,
    SecurityMiddleware,
)


class TestCache:
    """测试缓存系统"""

    def test_memory_cache_basic(self):
        """测试内存缓存基本功能"""
        cache = MemoryCache(max_size=10)

        # 设置和获取
        cache.set("key1", "value1")
        entry = cache.get("key1")
        assert entry is not None
        assert entry.value == "value1"

        # 不存在的键
        assert cache.get("nonexistent") is None

    def test_memory_cache_ttl(self):
        """测试缓存 TTL"""
        cache = MemoryCache()

        # 设置短 TTL
        cache.set("key1", "value1", ttl=0.1)
        assert cache.get("key1") is not None

        # 等待过期
        time.sleep(0.2)
        assert cache.get("key1") is None

    def test_memory_cache_lru(self):
        """测试 LRU 淘汰"""
        cache = MemoryCache(max_size=3)

        cache.set("a", 1)
        cache.set("b", 2)
        cache.set("c", 3)
        cache.set("d", 4)  # 应该淘汰 a

        assert cache.get("a") is None
        assert cache.get("b") is not None
        assert cache.get("c") is not None
        assert cache.get("d") is not None

    def test_memory_cache_stats(self):
        """测试缓存统计"""
        cache = MemoryCache()

        cache.set("key1", "value1")
        cache.get("key1")  # hit
        cache.get("key2")  # miss

        stats = cache.stats()
        assert isinstance(stats, CacheStats)
        assert stats.hits == 1
        assert stats.misses == 1

    def test_disk_cache(self, tmp_path):
        """测试磁盘缓存"""
        cache = DiskCache(cache_dir=tmp_path)

        cache.set("key1", {"data": "value1"})
        entry = cache.get("key1")
        assert entry is not None
        assert entry.value == {"data": "value1"}

        # 持久化测试
        cache2 = DiskCache(cache_dir=tmp_path)
        entry2 = cache2.get("key1")
        assert entry2 is not None

    def test_multilevel_cache(self, tmp_path):
        """测试多级缓存"""
        l1 = MemoryCache()
        l2 = DiskCache(cache_dir=tmp_path)
        cache = MultiLevelCache(l1, l2)

        cache.set("key1", "value1")

        # 从 L1 读取
        entry = cache.get("key1")
        assert entry.value == "value1"

        # 清空 L1,从 L2 读取并回填
        l1.clear()
        entry = cache.get("key1")
        assert entry.value == "value1"
        assert l1.get("key1") is not None  # 已回填

    def test_cached_decorator(self):
        """测试缓存装饰器"""
        call_count = 0

        @cached(ttl=60, key_prefix="test")
        def expensive_function(x):
            nonlocal call_count
            call_count += 1
            return x * 2

        result1 = expensive_function(5)
        result2 = expensive_function(5)

        assert result1 == result2 == 10
        assert call_count == 1  # 只执行一次


class TestDatabase:
    """测试数据库系统"""

    @pytest.fixture
    def db(self, tmp_path):
        """创建临时数据库"""
        db_path = tmp_path / "test.db"
        database = Database(db_path)
        yield database
        database.close()

    def test_conversation_crud(self, db):
        """测试对话 CRUD"""
        conv = Conversation(
            session_id="session_1",
            role="user",
            content="Hello",
            model="gpt-4",
        )

        db.save_conversation(conv)

        history = db.get_conversation_history("session_1")
        assert len(history) == 1
        assert history[0].content == "Hello"

    def test_conversation_search(self, db):
        """测试对话搜索"""
        db.save_conversation(
            Conversation(
                session_id="s1",
                role="user",
                content="Python programming",
            )
        )
        db.save_conversation(
            Conversation(
                session_id="s1",
                role="assistant",
                content="JavaScript programming",
            )
        )

        results = db.search_conversations("Python")
        assert len(results) == 1
        assert "Python" in results[0].content

    def test_knowledge_document(self, db):
        """测试知识库文档"""
        doc = KnowledgeDocument(
            path="/docs/test.md",
            title="Test Doc",
            content_hash="abc123",
            doc_type="markdown",
        )

        db.add_knowledge_document(doc)

        retrieved = db.get_knowledge_document("/docs/test.md")
        assert retrieved is not None
        assert retrieved.title == "Test Doc"

    def test_user_preference(self, db):
        """测试用户偏好"""
        db.set_preference("theme", "dark", category="ui")
        db.set_preference("model", "gpt-4", category="model")

        theme = db.get_preference("theme")
        assert theme == "dark"

        ui_prefs = db.get_preferences_by_category("ui")
        assert "theme" in ui_prefs

    def test_database_stats(self, db):
        """测试数据库统计"""
        db.save_conversation(Conversation(session_id="s1", role="user", content="test"))
        db.add_knowledge_document(KnowledgeDocument(path="/test.md"))

        stats = db.get_stats()
        assert stats["conversations_count"] == 1
        assert stats["knowledge_documents_count"] == 1


class TestLazyLoader:
    """测试延迟加载"""

    def test_lazy_import(self):
        """测试延迟导入"""
        # 注意: 这里使用一个已知的模块测试
        os_module = lazy_import("os")
        assert os_module.path.exists(".")  # 使用时才真正导入

    def test_lazy_loader(self):
        """测试延迟加载器"""
        init_count = 0

        def factory():
            nonlocal init_count
            init_count += 1
            return {"initialized": True}

        loader = lazy_load(factory, "test")
        assert not loader.is_loaded
        assert init_count == 0

        # 第一次访问时初始化
        _ = loader["initialized"]
        assert loader.is_loaded
        assert init_count == 1

        # 再次访问不重复初始化
        _ = loader["initialized"]
        assert init_count == 1


class TestSecurity:
    """测试安全功能"""

    def test_rate_limiter(self):
        """测试速率限制器"""
        config = RateLimitConfig(
            requests_per_minute=3,
            burst_size=2,
        )
        limiter = RateLimiter(config)

        # 前2个请求应该通过 (burst)
        assert limiter.is_allowed("user1")[0] is True
        assert limiter.is_allowed("user1")[0] is True

        # 第3个请求应该被限制
        assert limiter.is_allowed("user1")[0] is False

    def test_ip_filter(self):
        """测试 IP 过滤器"""
        ip_filter = IPFilter(
            whitelist=["192.168.1.0/24"],
        )

        assert ip_filter.is_allowed("192.168.1.100") is True
        assert ip_filter.is_allowed("10.0.0.1") is False

        # 黑名单测试
        ip_filter2 = IPFilter(
            blacklist=["10.0.0.0/8"],
        )
        assert ip_filter2.is_allowed("10.0.0.1") is False
        assert ip_filter2.is_allowed("192.168.1.1") is True

    def test_input_validator_sql(self):
        """测试 SQL 注入检测"""
        validator = InputValidator()

        # 正常输入
        assert validator.sanitize_sql("Hello World") == "Hello World"

        # SQL 注入应该抛出异常
        from mechforge_core.security import SecurityError

        with pytest.raises(SecurityError):
            validator.sanitize_sql("'; DROP TABLE users; --")

    def test_input_validator_xss(self):
        """测试 XSS 检测"""
        validator = InputValidator()

        # 正常输入
        assert validator.sanitize_xss("Hello") == "Hello"

        # XSS 应该抛出异常
        with pytest.raises(SecurityError):
            validator.sanitize_xss("<script>alert('xss')</script>")

    def test_api_token_manager(self):
        """测试 API Token 管理"""
        manager = APITokenManager(secret_key="test_key")

        token = manager.generate_token("user_123", expires_in=3600)
        assert len(token) > 0

        # 验证有效 Token
        data = manager.validate_token(token)
        assert data is not None
        assert data["user_id"] == "user_123"

        # 验证无效 Token
        assert manager.validate_token("invalid_token") is None

        # 撤销 Token
        manager.revoke_token(token)
        assert manager.validate_token(token) is None

    def test_security_middleware(self):
        """测试安全中间件"""
        middleware = SecurityMiddleware()

        result = middleware.check_request("127.0.0.1")
        assert result["allowed"] is True

        # 添加 IP 到黑名单
        middleware.ip_filter.add_to_blacklist("192.168.1.1")
        result = middleware.check_request("192.168.1.1")
        assert result["allowed"] is False


class TestIntegration:
    """集成测试"""

    def test_cache_and_database_integration(self, tmp_path):
        """测试缓存和数据库集成"""
        # 创建数据库和缓存
        db = Database(tmp_path / "integration.db")
        cache = MultiLevelCache(
            l1=MemoryCache(),
            l2=DiskCache(tmp_path / "cache"),
        )

        # 保存对话到数据库
        conv = Conversation(session_id="s1", role="user", content="test")
        db.save_conversation(conv)

        # 缓存查询结果
        def get_history(session_id):
            return db.get_conversation_history(session_id)

        # 第一次查询
        history1 = get_history("s1")
        cache.set("history_s1", history1)

        # 从缓存读取
        cached = cache.get("history_s1")
        assert cached is not None
        assert len(cached.value) == 1

        db.close()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
