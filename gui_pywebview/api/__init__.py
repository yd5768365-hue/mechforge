"""
MechForge AI GUI API 模块
提供模块化的 API 路由
"""

from .chat import router as chat_router
from .config import router as config_router
from .gguf import router as gguf_router
from .health import router as health_router
from .rag import router as rag_router

try:
    from .cae import router as cae_router
except Exception:
    cae_router = None  # type: ignore[assignment]

__all__ = [
    "chat_router",
    "rag_router",
    "config_router",
    "gguf_router",
    "health_router",
    "cae_router",
]
