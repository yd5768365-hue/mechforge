"""
MechForge Logging System

结构化日志记录:
- 多级日志 (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- 文件轮转
- JSON 格式输出
- 性能指标收集
- 上下文追踪

特性:
- 彩色终端输出
- 结构化日志 (JSON)
- 异步日志写入
- 日志级别热切换
"""

import json
import logging
import logging.handlers
import sys
import threading
import time
import traceback
from contextvars import ContextVar
from datetime import datetime
from functools import wraps
from pathlib import Path
from typing import Optional

# 上下文变量用于追踪请求/会话
request_id_var: ContextVar[str] = ContextVar("request_id", default="")
session_id_var: ContextVar[str] = ContextVar("session_id", default="")
user_id_var: ContextVar[str] = ContextVar("user_id", default="")


class ColoredFormatter(logging.Formatter):
    """彩色日志格式化器"""

    # ANSI 颜色码
    COLORS = {
        "DEBUG": "\033[36m",  # 青色
        "INFO": "\033[32m",  # 绿色
        "WARNING": "\033[33m",  # 黄色
        "ERROR": "\033[31m",  # 红色
        "CRITICAL": "\033[35m",  # 紫色
        "RESET": "\033[0m",  # 重置
    }

    def format(self, record: logging.LogRecord) -> str:
        # 保存原始级别名称
        levelname = record.levelname

        # 添加颜色
        if levelname in self.COLORS:
            record.levelname = f"{self.COLORS[levelname]}{levelname}{self.COLORS['RESET']}"

        # 格式化
        result = super().format(record)

        # 恢复原始级别名称
        record.levelname = levelname

        return result


class JSONFormatter(logging.Formatter):
    """JSON 格式日志"""

    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
            "thread": record.thread,
            "process": record.process,
        }

        # 添加上下文信息
        request_id = request_id_var.get()
        session_id = session_id_var.get()
        user_id = user_id_var.get()

        if request_id:
            log_data["request_id"] = request_id
        if session_id:
            log_data["session_id"] = session_id
        if user_id:
            log_data["user_id"] = user_id

        # 添加异常信息
        if record.exc_info:
            log_data["exception"] = traceback.format_exception(*record.exc_info)

        # 添加额外字段
        if hasattr(record, "extra_data"):
            log_data.update(record.extra_data)

        return json.dumps(log_data, ensure_ascii=False)


class PerformanceHandler(logging.Handler):
    """性能指标收集处理器"""

    def __init__(self, max_entries: int = 1000):
        super().__init__()
        self.metrics: list = []
        self.max_entries = max_entries
        self._lock = threading.Lock()

    def emit(self, record: logging.LogRecord):
        """收集性能指标"""
        if hasattr(record, "metric_name") and hasattr(record, "metric_value"):
            with self._lock:
                self.metrics.append(
                    {
                        "timestamp": datetime.fromtimestamp(record.created).isoformat(),
                        "name": record.metric_name,
                        "value": record.metric_value,
                        "unit": getattr(record, "metric_unit", ""),
                        "tags": getattr(record, "metric_tags", {}),
                    }
                )

                # 限制条目数
                if len(self.metrics) > self.max_entries:
                    self.metrics = self.metrics[-self.max_entries :]

    def get_metrics(self, name: str | None = None) -> list:
        """获取性能指标"""
        with self._lock:
            if name:
                return [m for m in self.metrics if m["name"] == name]
            return self.metrics.copy()

    def clear(self):
        """清空指标"""
        with self._lock:
            self.metrics.clear()


class LoggerManager:
    """
    日志管理器

    管理所有 logger 的配置和创建
    """

    _instance: Optional["LoggerManager"] = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if hasattr(self, "_initialized"):
            return

        self._initialized = True
        self.log_dir = Path.home() / ".mechforge" / "logs"
        self.log_dir.mkdir(parents=True, exist_ok=True)

        self.level = logging.INFO
        self.json_mode = False
        self.performance_handler = PerformanceHandler()

        # 配置根 logger
        self._setup_root_logger()

    def _setup_root_logger(self):
        """配置根 logger"""
        root_logger = logging.getLogger("mechforge")
        root_logger.setLevel(self.level)
        root_logger.handlers = []  # 清除现有处理器

        # 控制台处理器
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(self.level)

        if self.json_mode:
            console_handler.setFormatter(JSONFormatter())
        else:
            console_handler.setFormatter(
                ColoredFormatter(
                    "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s", datefmt="%H:%M:%S"
                )
            )

        root_logger.addHandler(console_handler)

        # 文件处理器 (轮转)
        file_handler = logging.handlers.RotatingFileHandler(
            self.log_dir / "mechforge.log",
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5,
            encoding="utf-8",
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(JSONFormatter())
        root_logger.addHandler(file_handler)

        # 错误日志单独文件
        error_handler = logging.handlers.RotatingFileHandler(
            self.log_dir / "error.log",
            maxBytes=10 * 1024 * 1024,
            backupCount=5,
            encoding="utf-8",
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(JSONFormatter())
        root_logger.addHandler(error_handler)

        # 性能指标处理器
        root_logger.addHandler(self.performance_handler)

    def get_logger(self, name: str) -> logging.Logger:
        """获取 logger"""
        return logging.getLogger(f"mechforge.{name}")

    def set_level(self, level: int | str):
        """设置日志级别"""
        if isinstance(level, str):
            level = getattr(logging, level.upper())

        self.level = level
        logging.getLogger("mechforge").setLevel(level)

    def enable_json_mode(self, enable: bool = True):
        """启用/禁用 JSON 模式"""
        self.json_mode = enable
        self._setup_root_logger()

    def get_performance_metrics(self, name: str | None = None) -> list:
        """获取性能指标"""
        return self.performance_handler.get_metrics(name)


# 全局日志管理器
logger_manager = LoggerManager()


def get_logger(name: str) -> logging.Logger:
    """获取 logger"""
    return logger_manager.get_logger(name)


def set_log_level(level: int | str):
    """设置日志级别"""
    logger_manager.set_level(level)


def set_request_id(request_id: str):
    """设置请求 ID"""
    request_id_var.set(request_id)


def set_session_id(session_id: str):
    """设置会话 ID"""
    session_id_var.set(session_id)


def set_user_id(user_id: str):
    """设置用户 ID"""
    user_id_var.set(user_id)


def clear_context():
    """清除上下文"""
    request_id_var.set("")
    session_id_var.set("")
    user_id_var.set("")


class log_performance:
    """
    性能日志上下文管理器/装饰器

    使用示例:
        # 作为上下文管理器
        with log_performance("database_query"):
            result = db.query()

        # 作为装饰器
        @log_performance("api_call")
        def call_api():
            pass
    """

    def __init__(
        self,
        name: str,
        logger: logging.Logger | None = None,
        level: int = logging.DEBUG,
    ):
        self.name = name
        self.logger = logger or get_logger("performance")
        self.level = level
        self.start_time: float | None = None
        self.end_time: float | None = None

    def __enter__(self):
        self.start_time = time.time()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end_time = time.time()
        duration = (self.end_time - self.start_time) * 1000  # ms

        extra = {
            "metric_name": self.name,
            "metric_value": duration,
            "metric_unit": "ms",
        }

        if exc_type:
            extra["error"] = str(exc_val)
            self.logger.error(
                f"Performance: {self.name} failed after {duration:.2f}ms",
                extra={"extra_data": extra},
            )
        else:
            self.logger.log(
                self.level,
                f"Performance: {self.name} completed in {duration:.2f}ms",
                extra={"extra_data": extra},
            )

    def __call__(self, func):
        """作为装饰器使用"""

        @wraps(func)
        def wrapper(*args, **kwargs):
            with self:
                return func(*args, **kwargs)

        return wrapper


# 便捷函数


def debug(msg: str, **kwargs):
    """记录 DEBUG 日志"""
    logger = get_logger("app")
    if kwargs:
        extra = {"extra_data": kwargs}
        logger.debug(msg, extra=extra)
    else:
        logger.debug(msg)


def info(msg: str, **kwargs):
    """记录 INFO 日志"""
    logger = get_logger("app")
    if kwargs:
        extra = {"extra_data": kwargs}
        logger.info(msg, extra=extra)
    else:
        logger.info(msg)


def warning(msg: str, **kwargs):
    """记录 WARNING 日志"""
    logger = get_logger("app")
    if kwargs:
        extra = {"extra_data": kwargs}
        logger.warning(msg, extra=extra)
    else:
        logger.warning(msg)


def error(msg: str, **kwargs):
    """记录 ERROR 日志"""
    logger = get_logger("app")
    if kwargs:
        extra = {"extra_data": kwargs}
        logger.error(msg, extra=extra)
    else:
        logger.error(msg)


def exception(msg: str, **kwargs):
    """记录异常日志"""
    logger = get_logger("app")
    if kwargs:
        extra = {"extra_data": kwargs}
        logger.exception(msg, extra=extra)
    else:
        logger.exception(msg)
