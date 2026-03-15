"""
GUI 配置管理
集中管理所有硬编码的默认值
"""

import os
from pathlib import Path


class GUIConfig:
    """GUI 配置管理器"""

    # ═══════════════════════════════════════════════════════════════
    # 服务器配置
    # ═══════════════════════════════════════════════════════════════
    @property
    def server_host(self) -> str:
        """服务器主机地址"""
        return os.getenv("MECHFORGE_HOST", "127.0.0.1")

    @property
    def server_port(self) -> int:
        """服务器端口"""
        return int(os.getenv("MECHFORGE_PORT", "5000"))

    @property
    def server_url(self) -> str:
        """完整服务器 URL"""
        return f"http://{self.server_host}:{self.server_port}"

    # ═══════════════════════════════════════════════════════════════
    # Ollama 配置
    # ═══════════════════════════════════════════════════════════════
    @property
    def ollama_url(self) -> str:
        """Ollama 服务地址"""
        return os.getenv("OLLAMA_URL", "http://localhost:11434")

    @property
    def ollama_model(self) -> str:
        """默认 Ollama 模型"""
        return os.getenv("OLLAMA_MODEL", "qwen2.5:3b")

    # ═══════════════════════════════════════════════════════════════
    # GGUF 配置
    # ═══════════════════════════════════════════════════════════════
    @property
    def gguf_server_url(self) -> str:
        """GGUF 服务器地址"""
        return os.getenv("GGUF_SERVER_URL", "http://127.0.0.1:11435")

    # ═══════════════════════════════════════════════════════════════
    # 窗口配置
    # ═══════════════════════════════════════════════════════════════
    @property
    def window_width(self) -> int:
        """默认窗口宽度"""
        return int(os.getenv("MECHFORGE_WINDOW_WIDTH", "1200"))

    @property
    def window_height(self) -> int:
        """默认窗口高度"""
        return int(os.getenv("MECHFORGE_WINDOW_HEIGHT", "800"))

    @property
    def window_min_width(self) -> int:
        """最小窗口宽度"""
        return int(os.getenv("MECHFORGE_WINDOW_MIN_WIDTH", "1000"))

    @property
    def window_min_height(self) -> int:
        """最小窗口高度"""
        return int(os.getenv("MECHFORGE_WINDOW_MIN_HEIGHT", "700"))

    # ═══════════════════════════════════════════════════════════════
    # 路径配置
    # ═══════════════════════════════════════════════════════════════
    @property
    def config_dir(self) -> Path:
        """配置目录"""
        return Path.home() / ".mechforge"

    @property
    def config_file(self) -> Path:
        """配置文件路径"""
        return self.config_dir / "gui_config.json"

    @property
    def log_file(self) -> Path | None:
        """日志文件路径"""
        log_path = os.getenv("MECHFORGE_LOG_FILE")
        if log_path:
            return Path(log_path)
        return None

    # ═══════════════════════════════════════════════════════════════
    # 其他配置
    # ═══════════════════════════════════════════════════════════════
    @property
    def debug(self) -> bool:
        """调试模式"""
        return os.getenv("MECHFORGE_DEBUG", "false").lower() == "true"

    @property
    def theme(self) -> str:
        """默认主题"""
        return os.getenv("MECHFORGE_THEME", "dark")

    @property
    def language(self) -> str:
        """默认语言"""
        return os.getenv("MECHFORGE_LANGUAGE", "zh-CN")


# 全局配置实例
gui_config = GUIConfig()
