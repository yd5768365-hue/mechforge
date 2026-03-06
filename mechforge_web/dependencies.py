"""
MechForge Web - FastAPI Security Dependencies

安全相关的依赖项，用于路由级别的安全控制:
- Token 认证
- 权限检查
- 请求验证
- 速率限制
"""

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from mechforge_core import get_logger
from mechforge_core.security import APITokenManager, SecurityMiddleware

logger = get_logger("web.dependencies")

# Token 认证方案
security_bearer = HTTPBearer(auto_error=False)


class TokenValidator:
    """Token 验证器"""

    def __init__(self):
        self.token_manager = APITokenManager()

    async def __call__(
        self,
        request: Request,
        credentials: HTTPAuthorizationCredentials | None = Depends(security_bearer),
    ) -> dict | None:
        """
        验证 Token

        Returns:
            Token 数据或 None (如果不需要认证)
        """
        # 从请求头获取 Token
        token = credentials.credentials if credentials else request.headers.get("X-API-Key")

        if not token:
            return None

        # 验证 Token
        token_data = self.token_manager.validate_token(token)

        if not token_data:
            logger.warning(
                "Invalid token",
                extra={
                    "extra_data": {
                        "client_ip": request.client.host if request.client else "unknown",
                        "path": request.url.path,
                    }
                },
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # 将用户信息添加到请求状态
        request.state.user_id = token_data.get("user_id")
        request.state.token_scopes = token_data.get("scopes", [])

        return token_data


class PermissionChecker:
    """权限检查器"""

    def __init__(self, required_scopes: list):
        self.required_scopes = required_scopes

    async def __call__(
        self,
        request: Request,
        token_data: dict | None = Depends(TokenValidator()),
    ) -> bool:
        """检查权限"""
        if not token_data:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required",
            )

        user_scopes = token_data.get("scopes", [])

        # 检查是否有必需的权限
        for scope in self.required_scopes:
            if scope not in user_scopes:
                logger.warning(
                    f"Permission denied: {scope} required",
                    extra={
                        "extra_data": {
                            "user_id": token_data.get("user_id"),
                            "required": self.required_scopes,
                            "has": user_scopes,
                        }
                    },
                )
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Permission denied: {scope} scope required",
                )

        return True


class RateLimitByUser:
    """基于用户的速率限制"""

    def __init__(self, requests_per_minute: int = 60):
        self.requests_per_minute = requests_per_minute
        self.security_middleware = SecurityMiddleware()

    async def __call__(
        self,
        request: Request,
        token_data: dict | None = Depends(TokenValidator()),
    ) -> None:
        """检查速率限制"""
        # 使用用户 ID 或 IP 作为限制键
        if token_data:
            limit_key = f"user:{token_data['user_id']}"
        else:
            client_ip = request.client.host if request.client else "unknown"
            limit_key = f"ip:{client_ip}"

        # 检查限流
        allowed, info = self.security_middleware.rate_limiter.is_allowed(limit_key)

        if not allowed:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail={
                    "error": "Rate limit exceeded",
                    "retry_after": info.get("retry_after", 60),
                },
                headers={
                    "Retry-After": str(info.get("retry_after", 60)),
                    "X-RateLimit-Limit": str(self.requests_per_minute),
                    "X-RateLimit-Remaining": "0",
                },
            )

        # 添加限流信息到请求状态
        request.state.rate_limit_remaining = info.get("remaining")


class InputSanitizer:
    """输入清理器"""

    def __init__(self, allow_html: bool = False):
        self.allow_html = allow_html
        self.security_middleware = SecurityMiddleware()

    def sanitize(self, value: str) -> str:
        """清理输入值"""
        return self.security_middleware.sanitize_input(value, self.allow_html)


# 便捷依赖函数


async def get_current_user(
    request: Request,
    credentials: HTTPAuthorizationCredentials | None = Depends(security_bearer),
) -> dict | None:
    """
    获取当前用户

    使用示例:
        @app.get("/profile")
        async def profile(user: dict = Depends(get_current_user)):
            return {"user_id": user["user_id"]}
    """
    validator = TokenValidator()
    return await validator(request, credentials)


async def require_auth(
    request: Request,
    credentials: HTTPAuthorizationCredentials | None = Depends(security_bearer),
) -> dict:
    """
    要求认证

    使用示例:
        @app.post("/api/data")
        async def create_data(user: dict = Depends(require_auth)):
            pass
    """
    validator = TokenValidator()
    user = await validator(request, credentials)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


def require_scopes(scopes: list):
    """
    要求特定权限

    使用示例:
        @app.delete("/api/data/{id}")
        async def delete_data(
            _: bool = Depends(require_scopes(["write", "admin"]))
        ):
            pass
    """
    return PermissionChecker(scopes)


def rate_limit(requests_per_minute: int = 60):
    """
    速率限制

    使用示例:
        @app.post("/api/submit")
        async def submit(_: None = Depends(rate_limit(10))):
            pass
    """
    return RateLimitByUser(requests_per_minute)


# 常用组合依赖


async def authenticated_user(
    user: dict = Depends(require_auth),
) -> dict:
    """已认证用户 (简化版)"""
    return user


class SecurityContext:
    """安全上下文"""

    def __init__(
        self,
        request: Request,
        user: dict | None = None,
    ):
        self.request = request
        self.user = user
        self.client_ip = request.client.host if request.client else "unknown"
        self.request_id = getattr(request.state, "request_id", "unknown")

    @property
    def is_authenticated(self) -> bool:
        """是否已认证"""
        return self.user is not None

    @property
    def user_id(self) -> str | None:
        """用户 ID"""
        return self.user.get("user_id") if self.user else None

    @property
    def scopes(self) -> list:
        """用户权限"""
        return self.user.get("scopes", []) if self.user else []

    def has_scope(self, scope: str) -> bool:
        """检查是否有特定权限"""
        return scope in self.scopes

    def log_context(self) -> dict:
        """获取日志上下文"""
        return {
            "request_id": self.request_id,
            "client_ip": self.client_ip,
            "user_id": self.user_id,
        }


async def get_security_context(
    request: Request,
    user: dict | None = Depends(get_current_user),
) -> SecurityContext:
    """
    获取安全上下文

    使用示例:
        @app.get("/api/data")
        async def get_data(ctx: SecurityContext = Depends(get_security_context)):
            if not ctx.is_authenticated:
                raise HTTPException(401)
            logger.info("Access", extra=ctx.log_context())
    """
    return SecurityContext(request, user)
