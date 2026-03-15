"""
MechForge Web - FastAPI Security Middleware

安全中间件集合:
- 速率限制中间件
- IP 过滤中间件
- 安全头部中间件
- 请求日志中间件
- 异常处理中间件
"""

import time
import uuid
from collections.abc import Callable

from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from mechforge_core import get_logger
from mechforge_core.security import (
    InputValidator,
    IPFilter,
    RateLimitConfig,
    RateLimiter,
    create_security_headers,
)

logger = get_logger("web.security")


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    速率限制中间件

    基于客户端 IP 或用户 ID 进行限流
    """

    def __init__(
        self,
        app: ASGIApp,
        config: RateLimitConfig | None = None,
        skip_paths: list | None = None,
    ):
        super().__init__(app)
        self.limiter = RateLimiter(config or RateLimitConfig())
        self.skip_paths = skip_paths or ["/health", "/docs", "/openapi.json", "/static"]

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # 跳过特定路径
        path = request.url.path
        if any(path.startswith(skip) for skip in self.skip_paths):
            return await call_next(request)

        # 获取客户端标识
        client_id = self._get_client_id(request)

        # 检查限流
        allowed, info = self.limiter.is_allowed(client_id)

        if not allowed:
            logger.warning(
                f"Rate limit exceeded for {client_id}",
                extra={
                    "extra_data": {
                        "client_id": client_id,
                        "path": path,
                        "reason": info.get("reason"),
                    }
                },
            )
            return JSONResponse(
                status_code=429,
                content={
                    "error": "Rate limit exceeded",
                    "retry_after": info.get("retry_after", 60),
                    "limit": info.get("limit"),
                },
                headers={
                    "Retry-After": str(info.get("retry_after", 60)),
                    "X-RateLimit-Limit": str(info.get("limit", "unknown")),
                    "X-RateLimit-Remaining": "0",
                },
            )

        # 添加限流信息到响应头
        response = await call_next(request)
        response.headers["X-RateLimit-Limit"] = str(info.get("limit", "unknown"))
        response.headers["X-RateLimit-Remaining"] = str(info.get("remaining", "unknown"))

        return response

    def _get_client_id(self, request: Request) -> str:
        """获取客户端标识"""
        # 优先使用用户 ID
        user_id = request.headers.get("X-User-ID")
        if user_id:
            return f"user:{user_id}"

        # 其次使用 API Key
        api_key = request.headers.get("X-API-Key")
        if api_key:
            return f"api:{api_key[:8]}"

        # 最后使用 IP 地址
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return f"ip:{forwarded.split(',')[0].strip()}"

        client_host = request.client.host if request.client else "unknown"
        return f"ip:{client_host}"


class IPFilterMiddleware(BaseHTTPMiddleware):
    """
    IP 过滤中间件

    基于白名单/黑名单过滤请求
    """

    def __init__(
        self,
        app: ASGIApp,
        whitelist: list | None = None,
        blacklist: list | None = None,
        skip_paths: list | None = None,
    ):
        super().__init__(app)
        self.ip_filter = IPFilter(whitelist=whitelist, blacklist=blacklist)
        self.skip_paths = skip_paths or ["/health"]

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        path = request.url.path
        if any(path.startswith(skip) for skip in self.skip_paths):
            return await call_next(request)

        # 获取客户端 IP
        client_ip = self._get_client_ip(request)

        # 检查 IP
        if not self.ip_filter.is_allowed(client_ip):
            logger.warning(
                f"IP {client_ip} blocked",
                extra={"extra_data": {"ip": client_ip, "path": path}},
            )
            return JSONResponse(
                status_code=403,
                content={"error": "Access denied", "ip": client_ip},
            )

        return await call_next(request)

    def _get_client_ip(self, request: Request) -> str:
        """获取客户端真实 IP"""
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()

        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip

        return request.client.host if request.client else "unknown"


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    安全头部中间件

    添加安全相关的 HTTP 响应头
    """

    def __init__(
        self,
        app: ASGIApp,
        csp_policy: str | None = None,
    ):
        super().__init__(app)
        self.security_headers = create_security_headers()
        if csp_policy:
            self.security_headers["Content-Security-Policy"] = csp_policy

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        response = await call_next(request)

        # 添加安全头部
        for header, value in self.security_headers.items():
            response.headers[header] = value

        return response


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    请求日志中间件

    记录所有请求的详细日志
    """

    def __init__(
        self,
        app: ASGIApp,
        skip_paths: list | None = None,
    ):
        super().__init__(app)
        self.skip_paths = skip_paths or ["/health", "/static"]

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        path = request.url.path

        # 生成请求 ID
        request_id = str(uuid.uuid4())[:8]
        request.state.request_id = request_id

        # 记录请求开始
        start_time = time.time()

        # 跳过特定路径的日志
        if any(path.startswith(skip) for skip in self.skip_paths):
            return await call_next(request)

        # 获取客户端信息
        client_ip = request.client.host if request.client else "unknown"
        method = request.method

        logger.info(
            f"Request started: {method} {path}",
            extra={
                "extra_data": {
                    "request_id": request_id,
                    "method": method,
                    "path": path,
                    "client_ip": client_ip,
                    "user_agent": request.headers.get("User-Agent"),
                }
            },
        )

        try:
            response = await call_next(request)
            duration = time.time() - start_time

            logger.info(
                f"Request completed: {method} {path} - {response.status_code}",
                extra={
                    "extra_data": {
                        "request_id": request_id,
                        "method": method,
                        "path": path,
                        "status_code": response.status_code,
                        "duration_ms": round(duration * 1000, 2),
                    }
                },
            )

            # 添加请求 ID 到响应头
            response.headers["X-Request-ID"] = request_id

            return response

        except Exception as e:
            duration = time.time() - start_time
            logger.error(
                f"Request failed: {method} {path} - {str(e)}",
                extra={
                    "extra_data": {
                        "request_id": request_id,
                        "method": method,
                        "path": path,
                        "error": str(e),
                        "duration_ms": round(duration * 1000, 2),
                    }
                },
            )
            raise


class ExceptionHandlingMiddleware(BaseHTTPMiddleware):
    """
    异常处理中间件

    统一处理未捕获的异常
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        try:
            return await call_next(request)

        except Exception as e:
            # 获取请求 ID
            request_id = getattr(request.state, "request_id", "unknown")

            logger.exception(
                f"Unhandled exception in {request.method} {request.url.path}",
                extra={"extra_data": {"request_id": request_id}},
            )

            # 根据环境返回不同详细程度的错误
            return JSONResponse(
                status_code=500,
                content={
                    "error": "Internal server error",
                    "request_id": request_id,
                    "type": type(e).__name__,
                },
            )


class InputValidationMiddleware(BaseHTTPMiddleware):
    """
    输入验证中间件

    验证和清理请求输入
    """

    def __init__(
        self,
        app: ASGIApp,
        validate_paths: list | None = None,
    ):
        super().__init__(app)
        self.validator = InputValidator()
        self.validate_paths = validate_paths or ["/api/"]

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        path = request.url.path

        # 只验证 API 路径
        if not any(path.startswith(p) for p in self.validate_paths):
            return await call_next(request)

        # 检查查询参数
        for key, values in request.query_params.multi_items():
            for value in values:
                try:
                    self.validator.sanitize_sql(value)
                    self.validator.sanitize_xss(value)
                except Exception as e:
                    logger.warning(
                        f"Invalid input detected: {key}={value[:50]}",
                        extra={
                            "extra_data": {
                                "path": path,
                                "param": key,
                                "error": str(e),
                            }
                        },
                    )
                    return JSONResponse(
                        status_code=400,
                        content={"error": "Invalid input parameter", "param": key},
                    )

        return await call_next(request)


class CORSMiddleware:
    """
    CORS 中间件 (简化版，建议使用 fastapi.middleware.cors)

    用于演示，生产环境请使用官方 CORS 中间件
    """

    def __init__(
        self,
        app: ASGIApp,
        allow_origins: list = None,
        allow_methods: list = None,
        allow_headers: list = None,
        allow_credentials: bool = False,
    ):
        self.app = app
        self.allow_origins = allow_origins or ["*"]
        self.allow_methods = allow_methods or ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
        self.allow_headers = allow_headers or ["*"]
        self.allow_credentials = allow_credentials

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        # 处理预检请求
        method = scope.get("method", "")
        headers = dict(scope.get("headers", []))

        origin = headers.get(b"origin", b"").decode() if b"origin" in headers else ""

        if method == "OPTIONS":
            response_headers = [
                (b"access-control-allow-origin", origin.encode() if origin else b"*"),
                (b"access-control-allow-methods", ", ".join(self.allow_methods).encode()),
                (b"access-control-allow-headers", ", ".join(self.allow_headers).encode()),
                (b"access-control-max-age", b"600"),
            ]

            if self.allow_credentials:
                response_headers.append((b"access-control-allow-credentials", b"true"))

            await send(
                {
                    "type": "http.response.start",
                    "status": 200,
                    "headers": response_headers,
                }
            )
            await send({"type": "http.response.body", "body": b""})
            return

        # 添加 CORS 头到响应
        async def wrapped_send(message):
            if message["type"] == "http.response.start":
                headers = list(message.get("headers", []))
                headers.append(
                    (b"access-control-allow-origin", origin.encode() if origin else b"*")
                )

                if self.allow_credentials:
                    headers.append((b"access-control-allow-credentials", b"true"))

                message["headers"] = headers

            await send(message)

        await self.app(scope, receive, wrapped_send)


def setup_security_middleware(
    app: FastAPI,
    rate_limit_config: RateLimitConfig | None = None,
    ip_whitelist: list | None = None,
    ip_blacklist: list | None = None,
    enable_cors: bool = True,
    cors_origins: list | None = None,
) -> None:
    """
    设置所有安全中间件

    使用示例:
        app = FastAPI()
        setup_security_middleware(
            app,
            rate_limit_config=RateLimitConfig(requests_per_minute=100),
            ip_whitelist=["192.168.1.0/24"],
        )
    """
    # 异常处理 (最先添加，最后执行)
    app.add_middleware(ExceptionHandlingMiddleware)

    # 请求日志
    app.add_middleware(RequestLoggingMiddleware)

    # 安全头部
    app.add_middleware(SecurityHeadersMiddleware)

    # IP 过滤
    if ip_whitelist or ip_blacklist:
        app.add_middleware(
            IPFilterMiddleware,
            whitelist=ip_whitelist,
            blacklist=ip_blacklist,
        )

    # 输入验证
    app.add_middleware(InputValidationMiddleware)

    # 速率限制
    app.add_middleware(
        RateLimitMiddleware,
        config=rate_limit_config or RateLimitConfig(),
    )

    # CORS (最后添加，最先执行)
    if enable_cors:
        from fastapi.middleware.cors import CORSMiddleware as FastAPICORSMiddleware

        app.add_middleware(
            FastAPICORSMiddleware,
            allow_origins=cors_origins or ["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    logger.info("Security middleware setup complete")
