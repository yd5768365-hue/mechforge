"""
MechForge Web - Security Configuration

安全配置示例和工具
"""

from mechforge_core.security import RateLimitConfig

# 默认安全配置
DEFAULT_SECURITY_CONFIG = {
    # 速率限制
    "rate_limit": RateLimitConfig(
        requests_per_minute=120,
        requests_per_hour=3000,
        burst_size=20,
        block_duration=300,  # 5分钟
    ),
    # IP 过滤
    "ip_whitelist": [],  # 空列表表示允许所有
    "ip_blacklist": [],
    # CORS 配置
    "cors": {
        "enabled": True,
        "origins": [
            "http://localhost:8080",
            "http://127.0.0.1:8080",
            "http://localhost:3000",  # React 开发服务器
        ],
        "allow_credentials": True,
        "allow_methods": ["*"],
        "allow_headers": ["*"],
    },
    # 安全头部
    "security_headers": {
        "X-Content-Type-Options": "nosniff",
        "X-Frame-Options": "DENY",
        "X-XSS-Protection": "1; mode=block",
        "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
        "Referrer-Policy": "strict-origin-when-cross-origin",
    },
    # Token 配置
    "token": {
        "expires_in": 3600,  # 1小时
        "refresh_before": 300,  # 到期前5分钟可刷新
    },
}

# 生产环境配置
PRODUCTION_SECURITY_CONFIG = {
    "rate_limit": RateLimitConfig(
        requests_per_minute=60,
        requests_per_hour=1000,
        burst_size=10,
        block_duration=600,  # 10分钟
    ),
    "ip_whitelist": [],  # 按需配置
    "ip_blacklist": [],
    "cors": {
        "enabled": True,
        "origins": [
            # 只允许特定域名
            "https://mechforge.example.com",
        ],
        "allow_credentials": True,
        "allow_methods": ["GET", "POST", "PUT", "DELETE"],
        "allow_headers": [
            "Authorization",
            "Content-Type",
            "X-Request-ID",
        ],
    },
    "security_headers": {
        "X-Content-Type-Options": "nosniff",
        "X-Frame-Options": "DENY",
        "X-XSS-Protection": "1; mode=block",
        "Strict-Transport-Security": "max-age=31536000; includeSubDomains; preload",
        "Content-Security-Policy": "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'",
        "Referrer-Policy": "strict-origin-when-cross-origin",
        "Permissions-Policy": "geolocation=(), microphone=(), camera=()",
    },
    "token": {
        "expires_in": 1800,  # 30分钟
        "refresh_before": 300,
    },
}

# 开发环境配置
DEVELOPMENT_SECURITY_CONFIG = {
    "rate_limit": RateLimitConfig(
        requests_per_minute=1000,  # 开发环境放宽限制
        requests_per_hour=10000,
        burst_size=100,
        block_duration=60,
    ),
    "ip_whitelist": [],
    "ip_blacklist": [],
    "cors": {
        "enabled": True,
        "origins": ["*"],  # 允许所有来源
        "allow_credentials": True,
        "allow_methods": ["*"],
        "allow_headers": ["*"],
    },
    "security_headers": {
        "X-Content-Type-Options": "nosniff",
    },
    "token": {
        "expires_in": 86400,  # 24小时
        "refresh_before": 3600,
    },
}


def get_security_config(environment: str = "default") -> dict:
    """
    获取安全配置

    Args:
        environment: 环境名称 (default, production, development)

    Returns:
        安全配置字典
    """
    configs = {
        "default": DEFAULT_SECURITY_CONFIG,
        "production": PRODUCTION_SECURITY_CONFIG,
        "development": DEVELOPMENT_SECURITY_CONFIG,
    }

    return configs.get(environment, DEFAULT_SECURITY_CONFIG)
