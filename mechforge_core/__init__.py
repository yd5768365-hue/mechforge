"""
MechForge Core - Core utilities and configuration
"""

__version__ = "0.2.0"

from mechforge_core.cache import (
    CacheBackend,
    CacheEntry,
    CacheStats,
    DiskCache,
    MemoryCache,
    MultiLevelCache,
    cached,
    get_cache,
)
from mechforge_core.config import MechForgeConfig, get_config
from mechforge_core.database import (
    Conversation,
    Database,
    DatabaseError,
    KnowledgeDocument,
    UserPreference,
    get_database,
)
from mechforge_core.lazy_loader import (
    LazyImport,
    LazyLoader,
    lazy_import,
    lazy_load,
    lazy_property,
)
from mechforge_core.logger import (
    get_logger,
    log_performance,
    set_log_level,
    set_request_id,
    set_session_id,
)
from mechforge_core.security import (
    APITokenManager,
    InputValidator,
    IPFilter,
    RateLimitConfig,
    RateLimiter,
    SecurityMiddleware,
    get_security_middleware,
)
from mechforge_core.reflection import (
    ErrorType,
    ExperienceDB,
    InteractionLog,
    Lesson,
    ReflectionConfig,
    ReflectionEngine,
    ReflectionEntry,
    ReflectionLogger,
    ReflectionReporter,
    TaskResult,
)
from mechforge_core.reflection.integration import (
    ReflectionAwareLLM,
    ReflectionContext,
    ReflectionMixin,
    get_reflection_summary,
    with_reflection,
)

__all__ = [
    # Config
    "MechForgeConfig",
    "get_config",
    # Cache
    "CacheBackend",
    "CacheEntry",
    "CacheStats",
    "MemoryCache",
    "DiskCache",
    "MultiLevelCache",
    "cached",
    "get_cache",
    # Database
    "Database",
    "DatabaseError",
    "Conversation",
    "KnowledgeDocument",
    "UserPreference",
    "get_database",
    # Lazy Loader
    "LazyImport",
    "LazyLoader",
    "lazy_import",
    "lazy_load",
    "lazy_property",
    # Logger
    "get_logger",
    "log_performance",
    "set_log_level",
    "set_request_id",
    "set_session_id",
    # Security
    "RateLimiter",
    "RateLimitConfig",
    "IPFilter",
    "InputValidator",
    "APITokenManager",
    "SecurityMiddleware",
    "get_security_middleware",
    # Reflection
    "ErrorType",
    "ExperienceDB",
    "InteractionLog",
    "Lesson",
    "ReflectionConfig",
    "ReflectionEngine",
    "ReflectionEntry",
    "ReflectionLogger",
    "ReflectionReporter",
    "TaskResult",
    "ReflectionAwareLLM",
    "ReflectionContext",
    "ReflectionMixin",
    "get_reflection_summary",
    "with_reflection",
]
