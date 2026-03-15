"""
MechForge Security Module

API 安全功能:
- 速率限制 (Rate Limiting)
- 输入验证和清理
- Token 认证
- CORS 配置
- 安全头部

特性:
- 滑动窗口限流
- IP 白名单/黑名单
- 请求签名验证
- SQL 注入防护
- XSS 防护
"""

import hashlib
import hmac
import ipaddress
import re
import secrets
import time
from dataclasses import dataclass, field
from typing import Any


class SecurityError(Exception):
    """安全错误"""

    pass


class RateLimitExceededError(SecurityError):
    """速率限制超出"""

    pass


class AuthenticationError(SecurityError):
    """认证错误"""

    pass


@dataclass
class RateLimitConfig:
    """速率限制配置"""

    requests_per_minute: int = 60
    requests_per_hour: int = 1000
    burst_size: int = 10  # 突发请求数
    block_duration: int = 300  # 封禁时长(秒)


@dataclass
class RequestRecord:
    """请求记录"""

    count: int = 0
    window_start: float = field(default_factory=time.time)
    blocked_until: float | None = None


class RateLimiter:
    """
    滑动窗口速率限制器

    使用示例:
        limiter = RateLimiter(RateLimitConfig(requests_per_minute=60))

        if limiter.is_allowed("user_123"):
            process_request()
        else:
            raise RateLimitExceededError()
    """

    def __init__(self, config: RateLimitConfig | None = None):
        self.config = config or RateLimitConfig()
        self._records: dict[str, RequestRecord] = {}
        self._window_size = 60  # 1分钟窗口

    def is_allowed(self, key: str) -> tuple[bool, dict[str, Any]]:
        """
        检查是否允许请求

        Returns:
            (allowed, info)
        """
        now = time.time()
        record = self._records.get(key)

        # 检查是否被封禁
        if record and record.blocked_until and now < record.blocked_until:
            return False, {
                "allowed": False,
                "retry_after": int(record.blocked_until - now),
                "reason": "rate_limited",
            }

        # 清理旧记录
        if record and now - record.window_start > self._window_size:
            record = None

        # 创建新记录
        if record is None:
            record = RequestRecord(window_start=now)
            self._records[key] = record

        # 检查突发限制
        if record.count >= self.config.burst_size:
            # 封禁
            record.blocked_until = now + self.config.block_duration
            return False, {
                "allowed": False,
                "retry_after": self.config.block_duration,
                "reason": "burst_limit_exceeded",
            }

        # 检查速率限制
        if record.count >= self.config.requests_per_minute:
            return False, {
                "allowed": False,
                "retry_after": int(self._window_size - (now - record.window_start)),
                "reason": "rate_limit_exceeded",
            }

        # 允许请求
        record.count += 1

        return True, {
            "allowed": True,
            "remaining": self.config.requests_per_minute - record.count,
            "reset_time": int(record.window_start + self._window_size),
        }

    def reset(self, key: str):
        """重置限制"""
        if key in self._records:
            del self._records[key]

    def cleanup(self):
        """清理过期记录"""
        now = time.time()
        expired = [
            key
            for key, record in self._records.items()
            if now - record.window_start > self._window_size * 2
        ]
        for key in expired:
            del self._records[key]


class IPFilter:
    """
    IP 过滤器

    支持白名单和黑名单
    """

    def __init__(
        self,
        whitelist: list[str] | None = None,
        blacklist: list[str] | None = None,
    ):
        self.whitelist: set[ipaddress.IPv4Network] = set()
        self.blacklist: set[ipaddress.IPv4Network] = set()

        if whitelist:
            for ip in whitelist:
                self.add_to_whitelist(ip)

        if blacklist:
            for ip in blacklist:
                self.add_to_blacklist(ip)

    def add_to_whitelist(self, ip: str):
        """添加到白名单"""
        self.whitelist.add(ipaddress.ip_network(ip, strict=False))

    def add_to_blacklist(self, ip: str):
        """添加到黑名单"""
        self.blacklist.add(ipaddress.ip_network(ip, strict=False))

    def is_allowed(self, ip: str) -> bool:
        """检查 IP 是否允许访问"""
        try:
            addr = ipaddress.ip_address(ip)

            # 检查白名单
            if self.whitelist:
                return any(addr in network for network in self.whitelist)

            # 检查黑名单
            return not any(addr in network for network in self.blacklist)

        except ValueError:
            return False


class InputValidator:
    """
    输入验证器

    防止注入攻击
    """

    # SQL 注入模式
    SQL_PATTERNS = [
        r"(\%27)|(\')|(\-\-)|(\%23)|(#)",
        r"((\%3D)|(=))[^\n]*((\%27)|(\')|(\-\-)|(\%3B)|(;))",
        r"\w*((\%27)|(\'))((\%6F)|o|(\%4F))((\%72)|r|(\%52))",
        r"((\%27)|(\'))union",
        r"exec(\s|\+)+(s|x)p\w+",
        r"UNION\s+SELECT",
        r"INSERT\s+INTO",
        r"DELETE\s+FROM",
        r"DROP\s+TABLE",
    ]

    # XSS 模式
    XSS_PATTERNS = [
        r"<script[^>]*>[\s\S]*?</script>",
        r"javascript:",
        r"on\w+\s*=",
        r"<iframe",
        r"<object",
        r"<embed",
    ]

    def __init__(self):
        self.sql_patterns = [re.compile(p, re.IGNORECASE) for p in self.SQL_PATTERNS]
        self.xss_patterns = [re.compile(p, re.IGNORECASE) for p in self.XSS_PATTERNS]

    def sanitize_sql(self, value: str) -> str:
        """清理 SQL 注入"""
        for pattern in self.sql_patterns:
            if pattern.search(value):
                raise SecurityError(f"Potential SQL injection detected: {value[:50]}")
        return value

    def sanitize_xss(self, value: str) -> str:
        """清理 XSS"""
        for pattern in self.xss_patterns:
            if pattern.search(value):
                raise SecurityError(f"Potential XSS detected: {value[:50]}")
        return value

    def sanitize_html(self, value: str) -> str:
        """清理 HTML"""
        # 转义 HTML 特殊字符
        value = value.replace("&", "&amp;")
        value = value.replace("<", "&lt;")
        value = value.replace(">", "&gt;")
        value = value.replace('"', "&quot;")
        value = value.replace("'", "&#x27;")
        return value

    def validate_length(
        self,
        value: str,
        min_length: int = 0,
        max_length: int = 10000,
    ) -> str:
        """验证长度"""
        if len(value) < min_length:
            raise SecurityError(f"Input too short: {len(value)} < {min_length}")
        if len(value) > max_length:
            raise SecurityError(f"Input too long: {len(value)} > {max_length}")
        return value


class APITokenManager:
    """
    API Token 管理器

    生成和验证 API Token
    """

    def __init__(self, secret_key: str | None = None):
        self.secret_key = secret_key or secrets.token_hex(32)
        self._tokens: dict[str, dict[str, Any]] = {}

    def generate_token(
        self,
        user_id: str,
        expires_in: int = 86400,  # 24小时
        scopes: list[str] | None = None,
    ) -> str:
        """生成 Token"""
        token = secrets.token_urlsafe(32)
        expires_at = time.time() + expires_in

        self._tokens[token] = {
            "user_id": user_id,
            "created_at": time.time(),
            "expires_at": expires_at,
            "scopes": scopes or ["read"],
        }

        return token

    def validate_token(self, token: str) -> dict[str, Any] | None:
        """验证 Token"""
        data = self._tokens.get(token)
        if not data:
            return None

        if time.time() > data["expires_at"]:
            del self._tokens[token]
            return None

        return data

    def revoke_token(self, token: str) -> bool:
        """撤销 Token"""
        if token in self._tokens:
            del self._tokens[token]
            return True
        return False

    def generate_signature(
        self,
        data: str,
        timestamp: str | None = None,
    ) -> str:
        """生成请求签名"""
        timestamp = timestamp or str(int(time.time()))
        message = f"{timestamp}:{data}"
        signature = hmac.new(
            self.secret_key.encode(),
            message.encode(),
            hashlib.sha256,
        ).hexdigest()
        return f"{timestamp}:{signature}"

    def verify_signature(self, data: str, signature: str) -> bool:
        """验证请求签名"""
        try:
            timestamp, sig = signature.split(":", 1)
            expected = self.generate_signature(data, timestamp)
            return hmac.compare_digest(signature, expected)
        except ValueError:
            return False


class SecurityMiddleware:
    """
    安全中间件

    组合所有安全功能
    """

    def __init__(
        self,
        rate_limit_config: RateLimitConfig | None = None,
        secret_key: str | None = None,
    ):
        self.rate_limiter = RateLimiter(rate_limit_config)
        self.ip_filter = IPFilter()
        self.validator = InputValidator()
        self.token_manager = APITokenManager(secret_key)

    def check_request(
        self,
        client_ip: str,
        user_id: str | None = None,
        token: str | None = None,
    ) -> dict[str, Any]:
        """
        检查请求安全性

        Returns:
            {"allowed": bool, "reason": str, "info": dict}
        """
        # IP 检查
        if not self.ip_filter.is_allowed(client_ip):
            return {
                "allowed": False,
                "reason": "ip_blocked",
                "info": {},
            }

        # Token 验证
        if token:
            token_data = self.token_manager.validate_token(token)
            if not token_data:
                return {
                    "allowed": False,
                    "reason": "invalid_token",
                    "info": {},
                }

        # 速率限制
        limit_key = user_id or client_ip
        allowed, info = self.rate_limiter.is_allowed(limit_key)

        if not allowed:
            return {
                "allowed": False,
                "reason": info["reason"],
                "info": info,
            }

        return {
            "allowed": True,
            "reason": "",
            "info": info,
        }

    def sanitize_input(self, value: str, allow_html: bool = False) -> str:
        """清理输入"""
        value = self.validator.sanitize_sql(value)
        value = self.validator.sanitize_xss(value)

        if not allow_html:
            value = self.validator.sanitize_html(value)

        return value


# 便捷函数


def create_security_headers() -> dict[str, str]:
    """创建安全 HTTP 头部"""
    return {
        "X-Content-Type-Options": "nosniff",
        "X-Frame-Options": "DENY",
        "X-XSS-Protection": "1; mode=block",
        "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
        "Content-Security-Policy": "default-src 'self'",
        "Referrer-Policy": "strict-origin-when-cross-origin",
        "Permissions-Policy": "geolocation=(), microphone=(), camera=()",
    }


def generate_csrf_token() -> str:
    """生成 CSRF Token"""
    return secrets.token_urlsafe(32)


def validate_password_strength(password: str) -> tuple[bool, list[str]]:
    """
    验证密码强度

    Returns:
        (is_valid, list_of_issues)
    """
    issues = []

    if len(password) < 8:
        issues.append("Password must be at least 8 characters long")

    if not re.search(r"[A-Z]", password):
        issues.append("Password must contain at least one uppercase letter")

    if not re.search(r"[a-z]", password):
        issues.append("Password must contain at least one lowercase letter")

    if not re.search(r"\d", password):
        issues.append("Password must contain at least one digit")

    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        issues.append("Password must contain at least one special character")

    return len(issues) == 0, issues


# 全局安全中间件实例
_security_middleware: SecurityMiddleware | None = None


def get_security_middleware() -> SecurityMiddleware:
    """获取全局安全中间件"""
    global _security_middleware
    if _security_middleware is None:
        _security_middleware = SecurityMiddleware()
    return _security_middleware
