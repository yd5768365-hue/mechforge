"""
错误处理模块
提供统一的错误响应格式
"""

import logging
from typing import Any, Dict

from fastapi import Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import ValidationError

logger = logging.getLogger("mechforge.errors")


class APIError(Exception):
    """API 错误基类"""

    def __init__(
        self,
        message: str,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        details: Dict[str, Any] | None = None,
    ) -> None:
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)


class NotFoundError(APIError):
    """资源未找到错误"""

    def __init__(self, message: str = "Resource not found") -> None:
        super().__init__(message, status.HTTP_404_NOT_FOUND)


class ValidationError(APIError):
    """验证错误"""

    def __init__(self, message: str = "Validation failed", details: Dict[str, Any] | None = None) -> None:
        super().__init__(message, status.HTTP_422_UNPROCESSABLE_ENTITY, details)


class ServiceUnavailableError(APIError):
    """服务不可用错误"""

    def __init__(self, message: str = "Service unavailable") -> None:
        super().__init__(message, status.HTTP_503_SERVICE_UNAVAILABLE)


def create_error_response(
    message: str,
    status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
    details: Dict[str, Any] | None = None,
) -> JSONResponse:
    """创建统一的错误响应"""
    content: Dict[str, Any] = {
        "success": False,
        "error": {
            "message": message,
            "code": status_code,
        },
    }
    if details:
        content["error"]["details"] = details

    return JSONResponse(
        status_code=status_code,
        content=jsonable_encoder(content),
    )


async def api_error_handler(request: Request, exc: APIError) -> JSONResponse:
    """处理 APIError"""
    logger.error(f"API Error: {exc.message}", extra={"details": exc.details})
    return create_error_response(exc.message, exc.status_code, exc.details)


async def validation_error_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """处理请求验证错误"""
    errors = exc.errors()
    logger.warning(f"Validation error: {errors}")
    return create_error_response(
        "Validation failed",
        status.HTTP_422_UNPROCESSABLE_ENTITY,
        {"validation_errors": errors},
    )


async def generic_error_handler(request: Request, exc: Exception) -> JSONResponse:
    """处理未捕获的异常"""
    logger.exception(f"Unhandled exception: {exc}")
    return create_error_response(
        "Internal server error",
        status.HTTP_500_INTERNAL_SERVER_ERROR,
    )


def setup_error_handlers(app) -> None:
    """配置错误处理器"""
    from fastapi.exceptions import RequestValidationError

    app.add_exception_handler(APIError, api_error_handler)
    app.add_exception_handler(RequestValidationError, validation_error_handler)
    app.add_exception_handler(Exception, generic_error_handler)