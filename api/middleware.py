"""
中间件模块
提供请求日志、性能监控、CORS、认证等中间件
"""

import logging
import time
from collections.abc import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

logger = logging.getLogger("mechforge.middleware")


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """请求日志中间件"""

    def __init__(self, app: ASGIApp, exclude_paths: list[str] = None) -> None:
        super().__init__(app)
        self.exclude_paths = exclude_paths or ["/health", "/static"]

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # 检查是否需要记录
        if any(request.url.path.startswith(p) for p in self.exclude_paths):
            return await call_next(request)

        start_time = time.time()
        client_ip = request.client.host if request.client else "unknown"

        # 记录请求
        logger.info(f"→ {request.method} {request.url.path} [IP: {client_ip}]")

        try:
            response = await call_next(request)
            process_time = time.time() - start_time

            # 记录响应
            logger.info(
                f"← {request.method} {request.url.path} "
                f"[{response.status_code}] {process_time:.3f}s"
            )

            # 添加性能头
            response.headers["X-Process-Time"] = str(process_time)
            return response

        except Exception as e:
            process_time = time.time() - start_time
            logger.error(f"✗ {request.method} {request.url.path} [ERROR] {process_time:.3f}s: {e}")
            raise


class PerformanceMiddleware(BaseHTTPMiddleware):
    """性能监控中间件"""

    def __init__(
        self, app: ASGIApp, slow_threshold: float = 1.0, warning_threshold: float = 0.5
    ) -> None:
        super().__init__(app)
        self.slow_threshold = slow_threshold
        self.warning_threshold = warning_threshold
        self.request_count = 0
        self.total_time = 0.0
        self.slow_requests = 0

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time

        # 更新统计
        self.request_count += 1
        self.total_time += process_time

        # 慢请求警告
        if process_time > self.slow_threshold:
            self.slow_requests += 1
            logger.warning(
                f"Slow request: {request.method} {request.url.path} took {process_time:.3f}s"
            )
        elif process_time > self.warning_threshold:
            logger.info(
                f"Moderate request: {request.method} {request.url.path} took {process_time:.3f}s"
            )

        # 添加性能头
        response.headers["X-Response-Time"] = f"{process_time:.3f}s"
        return response

    def get_stats(self) -> dict:
        """获取性能统计"""
        avg_time = self.total_time / self.request_count if self.request_count > 0 else 0
        return {
            "request_count": self.request_count,
            "total_time": self.total_time,
            "avg_time": avg_time,
            "slow_requests": self.slow_requests,
            "slow_rate": self.slow_requests / self.request_count if self.request_count > 0 else 0,
        }


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """安全头中间件"""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        response = await call_next(request)

        # 添加安全头
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: blob:; "
            "font-src 'self'; "
            "connect-src 'self' ws: wss:;"
        )
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"

        return response


class RateLimitMiddleware(BaseHTTPMiddleware):
    """速率限制中间件（简单实现）"""

    def __init__(self, app: ASGIApp, requests_per_minute: int = 60, burst_size: int = 10) -> None:
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.burst_size = burst_size
        self.requests: dict[str, list[float]] = {}

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        client_ip = request.client.host if request.client else "unknown"
        now = time.time()

        # 清理旧请求
        if client_ip in self.requests:
            self.requests[client_ip] = [t for t in self.requests[client_ip] if now - t < 60]
        else:
            self.requests[client_ip] = []

        # 检查限制
        if len(self.requests[client_ip]) >= self.requests_per_minute:
            logger.warning(f"Rate limit exceeded for {client_ip}")
            from fastapi.responses import JSONResponse

            return JSONResponse(
                status_code=429, content={"error": "Too many requests", "retry_after": 60}
            )

        # 记录请求
        self.requests[client_ip].append(now)

        response = await call_next(request)
        response.headers["X-RateLimit-Limit"] = str(self.requests_per_minute)
        response.headers["X-RateLimit-Remaining"] = str(
            self.requests_per_minute - len(self.requests[client_ip])
        )

        return response


class CacheControlMiddleware(BaseHTTPMiddleware):
    """缓存控制中间件"""

    def __init__(self, app: ASGIApp, cache_paths: dict[str, int] = None) -> None:
        super().__init__(app)
        self.cache_paths = cache_paths or {
            "/static": 3600,
            "/css": 3600,
            "/js": 3600,
        }

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        response = await call_next(request)

        # 根据路径设置缓存
        for path, max_age in self.cache_paths.items():
            if request.url.path.startswith(path):
                response.headers["Cache-Control"] = f"public, max-age={max_age}"
                break
        else:
            # 默认不缓存 API
            if request.url.path.startswith("/api"):
                response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate"

        return response


def setup_middleware(app) -> None:
    """配置所有中间件"""
    from fastapi.middleware.cors import CORSMiddleware

    # CORS 中间件
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # 自定义中间件
    app.add_middleware(SecurityHeadersMiddleware)
    app.add_middleware(RequestLoggingMiddleware)
    app.add_middleware(PerformanceMiddleware)
    app.add_middleware(CacheControlMiddleware)
    # app.add_middleware(RateLimitMiddleware)  # 可选启用
