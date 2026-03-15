"""
MechForge Web - Web UI for MechForge AI

FastAPI + WebSocket based modern web interface

Features:
- RESTful API
- WebSocket real-time communication
- Multi-level security (Rate limiting, IP filtering, Input validation)
- Static file serving
- Three modes: AI Chat / Knowledge / CAE Workbench
"""

__version__ = "0.2.0"

from mechforge_web.dependencies import (
    PermissionChecker,
    RateLimitByUser,
    SecurityContext,
    TokenValidator,
    get_current_user,
    get_security_context,
    rate_limit,
    require_auth,
    require_scopes,
)
from mechforge_web.middleware import (
    CORSMiddleware,
    ExceptionHandlingMiddleware,
    InputValidationMiddleware,
    IPFilterMiddleware,
    RateLimitMiddleware,
    RequestLoggingMiddleware,
    SecurityHeadersMiddleware,
    setup_security_middleware,
)
from mechforge_web.security_config import (
    DEFAULT_SECURITY_CONFIG,
    DEVELOPMENT_SECURITY_CONFIG,
    PRODUCTION_SECURITY_CONFIG,
    get_security_config,
)

__all__ = [
    # Dependencies
    "TokenValidator",
    "PermissionChecker",
    "RateLimitByUser",
    "SecurityContext",
    "get_current_user",
    "get_security_context",
    "rate_limit",
    "require_auth",
    "require_scopes",
    # Middleware
    "CORSMiddleware",
    "ExceptionHandlingMiddleware",
    "IPFilterMiddleware",
    "InputValidationMiddleware",
    "RateLimitMiddleware",
    "RequestLoggingMiddleware",
    "SecurityHeadersMiddleware",
    "setup_security_middleware",
    # Config
    "DEFAULT_SECURITY_CONFIG",
    "DEVELOPMENT_SECURITY_CONFIG",
    "PRODUCTION_SECURITY_CONFIG",
    "get_security_config",
]
