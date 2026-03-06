"""
MechForge AI 配置管理 (Pydantic v2)

支持:
- YAML/JSON 配置文件，带完整类型验证
- Provider 配置（多种 AI 提供商）
- MCP 服务器配置
- 环境变量覆盖
- 配置热重载
"""

import contextlib
import os
import sys
import threading
import time
from pathlib import Path
from typing import Any, ClassVar, Literal, Optional

import yaml
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


def _get_app_dir() -> Path:
    """获取应用目录"""
    if getattr(sys, "frozen", False):
        return Path(sys._MEIPASS)
    return Path(__file__).parent.parent.parent.parent


def _get_config_dir() -> Path:
    """获取配置目录"""
    if sys.platform == "win32":
        base = Path.home() / "AppData" / "Local"
    else:
        base = Path.home() / ".config"
    return base / "mechforge"


def _get_default_config_file() -> Path | None:
    """获取默认配置文件路径（按优先级）"""
    # 优先级: ~/.mechforge/config.yaml > ./mechforge-config.yaml > ./config.yaml
    paths = [
        _get_config_dir() / "config.yaml",
        Path.cwd() / "mechforge-config.yaml",
        Path.cwd() / "config.yaml",
    ]
    for path in paths:
        if path.exists():
            return path


def find_knowledge_path() -> Path | None:
    """查找知识库路径（AI模式和知识库模式统一使用）

    按优先级搜索以下路径：
    1. 配置文件中的 knowledge.path
    2. 项目根目录的 knowledge 文件夹
    3. 项目根目录的 data/knowledge 文件夹
    4. 用户主目录的 .mechforge/knowledge 文件夹
    5. 当前工作目录的 knowledge 文件夹
    """
    # 首先检查配置文件
    try:
        config = get_config()
        if config.knowledge and config.knowledge.path:
            config_path = Path(config.knowledge.path)
            if config_path.exists():
                return config_path
    except Exception:
        pass

    # 搜索其他路径
    search_paths = [
        _get_app_dir() / "knowledge",
        _get_app_dir() / "data" / "knowledge",
        _get_config_dir() / "knowledge",
        Path.home() / ".mechforge" / "knowledge",
        Path.cwd() / "knowledge",
    ]

    for path in search_paths:
        if path.exists() and list(path.glob("*.md")):
            return path

    # 返回默认路径（即使不存在）
    return Path.cwd() / "knowledge"
    return None


# ==================== Provider 配置 ====================


class OpenAIConfig(BaseModel):
    """OpenAI 配置"""

    model_config = ConfigDict(frozen=False)

    api_key: str = Field(default="", description="OpenAI API Key")
    model: str = Field(default="gpt-4o-mini", description="模型名称")
    base_url: str = Field(default="https://api.openai.com/v1", description="API 基础 URL")
    timeout: float = Field(default=60.0, description="请求超时时间（秒）")
    max_retries: int = Field(default=3, description="最大重试次数")

    @field_validator("api_key")
    @classmethod
    def _env_api_key(cls, v: str) -> str:
        """从环境变量读取 API Key"""
        return v or os.getenv("OPENAI_API_KEY", "")


class AnthropicConfig(BaseModel):
    """Anthropic 配置"""

    model_config = ConfigDict(frozen=False)

    api_key: str = Field(default="", description="Anthropic API Key")
    model: str = Field(default="claude-3-haiku-20240307", description="模型名称")
    base_url: str = Field(default="https://api.anthropic.com", description="API 基础 URL")
    timeout: float = Field(default=60.0, description="请求超时时间（秒）")
    max_retries: int = Field(default=3, description="最大重试次数")

    @field_validator("api_key")
    @classmethod
    def _env_api_key(cls, v: str) -> str:
        """从环境变量读取 API Key"""
        return v or os.getenv("ANTHROPIC_API_KEY", "")


class OllamaConfig(BaseModel):
    """Ollama 本地模型配置"""

    model_config = ConfigDict(frozen=False)

    url: str = Field(default="http://localhost:11434", description="Ollama 服务地址")
    model: str = Field(default="qwen2.5:1.5b", description="模型名称")
    auto_start: bool = Field(default=True, description="自动启动 Ollama 服务")
    timeout: float = Field(default=120.0, description="请求超时时间（秒）")


class LocalGGUFConfig(BaseModel):
    """本地 GGUF 模型配置"""

    model_config = ConfigDict(frozen=False)

    llm_model: str = Field(
        default="qwen2.5-1.5b-instruct-q4_k_m.gguf", description="LLM 模型文件名"
    )
    embedding_model: str = Field(default="bge-m3-Q8_0.gguf", description="嵌入模型文件名")
    model_dir: Path = Field(default=Path("./models"), description="模型目录")
    n_ctx: int = Field(default=2048, description="上下文长度")
    n_gpu_layers: int = Field(default=0, description="GPU 层数（0 表示 CPU  only）")
    n_threads: int | None = Field(default=None, description="线程数（None 表示自动）")


class ProviderConfig(BaseModel):
    """AI Provider 配置"""

    model_config = ConfigDict(frozen=False)

    default: Literal["openai", "anthropic", "ollama", "local"] = Field(
        default="ollama", description="默认使用的 AI 提供商"
    )
    openai: OpenAIConfig = Field(default_factory=OpenAIConfig)
    anthropic: AnthropicConfig = Field(default_factory=AnthropicConfig)
    ollama: OllamaConfig = Field(default_factory=OllamaConfig)
    local: LocalGGUFConfig = Field(default_factory=LocalGGUFConfig)

    def get_active_provider(self) -> str:
        """获取当前激活的 AI 提供商"""
        # 环境变量优先
        if os.getenv("OPENAI_API_KEY"):
            return "openai"
        if os.getenv("ANTHROPIC_API_KEY"):
            return "anthropic"
        return self.default

    def get_config(
        self, provider: str | None = None
    ) -> OpenAIConfig | AnthropicConfig | OllamaConfig | LocalGGUFConfig:
        """获取指定 provider 的配置"""
        provider = provider or self.get_active_provider()
        configs = {
            "openai": self.openai,
            "anthropic": self.anthropic,
            "ollama": self.ollama,
            "local": self.local,
        }
        return configs.get(provider, self.ollama)


# ==================== 知识库配置 ====================


class RAGConfig(BaseModel):
    """RAG 配置"""

    model_config = ConfigDict(frozen=False)

    enabled: bool = Field(default=False, description="是否启用 RAG")
    top_k: int = Field(default=5, ge=1, le=50, description="检索结果数量")
    cache_dir: Path = Field(default=Path(".cache/rag"), description="缓存目录")
    embedding_model: str = Field(default="all-MiniLM-L6-v2", description="嵌入模型名称")
    chunk_size: int = Field(default=512, ge=100, le=2048, description="文本分块大小")
    chunk_overlap: int = Field(default=50, ge=0, le=200, description="文本分块重叠大小")
    use_bm25: bool = Field(default=True, description="是否启用 BM25 关键词检索")
    use_rerank: bool = Field(default=True, description="是否启用重排序")
    rerank_model: str | None = Field(default=None, description="重排序模型（None 表示使用默认）")


class RAGFlowConfig(BaseModel):
    """RAGFlow 后端配置"""

    model_config = ConfigDict(frozen=False)

    url: str = Field(default="http://localhost:9380", description="RAGFlow 服务地址")
    api_key: str = Field(default="", description="API 密钥")
    kb_id: str = Field(default="", description="知识库 ID")
    timeout: int = Field(default=300, description="请求超时时间（秒）")


class KnowledgeConfig(BaseModel):
    """知识库配置"""

    model_config = ConfigDict(frozen=False)

    backend: Literal["local", "ragflow"] = Field(default="local", description="知识库后端类型")
    path: Path = Field(default=Path("./knowledge"), description="知识库目录")
    rag: RAGConfig = Field(default_factory=RAGConfig)
    ragflow: RAGFlowConfig = Field(default_factory=RAGFlowConfig)
    auto_reload: bool = Field(default=True, description="知识库变更时自动重载")
    file_extensions: list[str] = Field(
        default=[".md", ".txt", ".pdf"], description="支持的文件扩展名"
    )

    @field_validator("path")
    @classmethod
    def _resolve_path(cls, v: Path) -> Path:
        """解析路径"""
        return v.expanduser().resolve()


# ==================== MCP 配置 ====================


class MCPServerConfig(BaseModel):
    """单个 MCP 服务器配置"""

    model_config = ConfigDict(frozen=False)

    command: str = Field(description="执行的命令")
    args: list[str] = Field(default_factory=list, description="命令参数")
    env: dict[str, str] = Field(default_factory=dict, description="环境变量")
    timeout: float = Field(default=30.0, description="超时时间（秒）")
    enabled: bool = Field(default=True, description="是否启用")


class MCPConfig(BaseModel):
    """MCP 配置"""

    model_config = ConfigDict(frozen=False)

    enabled: bool = Field(default=False, description="是否启用 MCP")
    servers: dict[str, MCPServerConfig] = Field(default_factory=dict, description="MCP 服务器配置")


# ==================== UI 配置 ====================


class UIConfig(BaseModel):
    """UI 配置"""

    model_config = ConfigDict(frozen=False)

    theme: Literal["dark", "light", "auto"] = Field(default="dark", description="主题")
    color: bool = Field(default=True, description="是否启用彩色输出")
    show_status: bool = Field(default=True, description="是否显示状态指示器")
    ascii_art: bool = Field(default=True, description="是否显示 ASCII 艺术")
    animation: bool = Field(default=True, description="是否启用动画效果")
    language: str = Field(default="zh-CN", description="界面语言")


# ==================== 日志配置 ====================


class LoggingConfig(BaseModel):
    """日志配置"""

    model_config = ConfigDict(frozen=False)

    level: Literal["debug", "info", "warn", "error", "critical"] = Field(
        default="info", description="日志级别"
    )
    file: Path | None = Field(default=Path(".logs/mechforge.log"), description="日志文件路径")
    max_bytes: int = Field(default=10 * 1024 * 1024, description="单个日志文件最大大小（字节）")
    backup_count: int = Field(default=5, description="保留的日志文件数量")
    format: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        description="日志格式",
    )
    console: bool = Field(default=True, description="是否输出到控制台")


# ==================== 聊天配置 ====================


class ChatConfig(BaseModel):
    """聊天配置"""

    model_config = ConfigDict(frozen=False)

    history_limit: int = Field(default=50, ge=0, le=200, description="对话历史数量限制")
    system_prompt: str = Field(default="", description="系统提示词")
    temperature: float = Field(default=0.7, ge=0.0, le=2.0, description="温度参数")
    max_tokens: int = Field(default=2048, ge=100, le=8192, description="最大生成 token 数")
    stream: bool = Field(default=True, description="是否启用流式输出")
    tools_enabled: bool = Field(default=True, description="是否启用工具调用")
    context_window: int = Field(default=4096, ge=1024, le=128000, description="上下文窗口大小")


# ==================== 主配置类 ====================


class MechForgeConfig(BaseModel):
    """MechForge AI 主配置"""

    model_config = ConfigDict(frozen=False)

    provider: ProviderConfig = Field(default_factory=ProviderConfig)
    knowledge: KnowledgeConfig = Field(default_factory=KnowledgeConfig)
    mcp: MCPConfig = Field(default_factory=MCPConfig)
    ui: UIConfig = Field(default_factory=UIConfig)
    logging: LoggingConfig = Field(default_factory=LoggingConfig)
    chat: ChatConfig = Field(default_factory=ChatConfig)

    # 版本信息
    version: str = Field(default="0.4.0", description="配置版本")

    @model_validator(mode="after")
    def _env_overrides(self) -> "MechForgeConfig":
        """应用环境变量覆盖"""
        # Ollama 配置
        if url := os.getenv("OLLAMA_URL"):
            self.provider.ollama.url = url
        if model := os.getenv("OLLAMA_MODEL"):
            self.provider.ollama.model = model

        # 知识库配置
        if path := os.getenv("MECHFORGE_KNOWLEDGE_PATH"):
            self.knowledge.path = Path(path)
        if enabled := os.getenv("MECHFORGE_RAG"):
            self.knowledge.rag.enabled = enabled.lower() == "true"

        # 日志配置
        if level := os.getenv("MECHFORGE_LOG_LEVEL"):
            self.logging.level = level  # type: ignore

        # UI 配置
        if theme := os.getenv("MECHFORGE_THEME"):
            self.ui.theme = theme  # type: ignore

        return self

    @classmethod
    def from_file(cls, config_path: str | Path | None = None) -> "MechForgeConfig":
        """从文件加载配置"""
        path = Path(config_path) if config_path else _get_default_config_file()

        if not path or not path.exists():
            return cls()

        try:
            with open(path, encoding="utf-8") as f:
                data = yaml.safe_load(f) or {}
            return cls.model_validate(data)
        except Exception as e:
            print(f"警告: 加载配置文件失败: {e}, 使用默认配置")
            return cls()

    def to_file(self, config_path: str | Path | None = None) -> None:
        """保存配置到文件"""
        if config_path:
            path = Path(config_path)
        else:
            config_dir = _get_config_dir()
            config_dir.mkdir(parents=True, exist_ok=True)
            path = config_dir / "config.yaml"

        # 转换为字典并保存
        data = self.model_dump(mode="json", exclude_none=True)
        # 将 Path 对象转换为字符串
        data = _convert_paths_to_strings(data)

        with open(path, "w", encoding="utf-8") as f:
            yaml.dump(data, f, allow_unicode=True, default_flow_style=False, sort_keys=False)


def _convert_paths_to_strings(obj: Any) -> Any:
    """递归将 Path 对象转换为字符串"""
    if isinstance(obj, Path):
        return str(obj)
    elif isinstance(obj, dict):
        return {k: _convert_paths_to_strings(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [_convert_paths_to_strings(item) for item in obj]
    return obj


# ==================== 配置热重载 ====================


class ConfigWatcher:
    """配置文件热重载监视器"""

    _instance: ClassVar[Optional["ConfigWatcher"]] = None
    _lock: ClassVar[threading.Lock] = threading.Lock()

    def __new__(cls) -> "ConfigWatcher":
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self, check_interval: float = 5.0):
        if self._initialized:
            return

        self._initialized = True
        self._check_interval = check_interval
        self._config_path: Path | None = None
        self._last_mtime: float = 0
        self._running = False
        self._thread: threading.Thread | None = None
        self._callbacks: list[callable] = []

    def start(self, config_path: str | Path | None = None) -> None:
        """启动监视器"""
        if self._running:
            return

        self._config_path = Path(config_path) if config_path else _get_default_config_file()
        if not self._config_path or not self._config_path.exists():
            return

        self._last_mtime = self._config_path.stat().st_mtime
        self._running = True
        self._thread = threading.Thread(target=self._watch_loop, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        """停止监视器"""
        self._running = False
        if self._thread:
            self._thread.join(timeout=1.0)

    def _watch_loop(self) -> None:
        """监视循环"""
        while self._running:
            try:
                if self._config_path and self._config_path.exists():
                    current_mtime = self._config_path.stat().st_mtime
                    if current_mtime > self._last_mtime:
                        self._last_mtime = current_mtime
                        self._notify_reload()
            except Exception:
                pass
            time.sleep(self._check_interval)

    def _notify_reload(self) -> None:
        """通知所有回调函数"""
        for callback in self._callbacks:
            with contextlib.suppress(Exception):
                callback()

    def on_reload(self, callback: callable) -> None:
        """注册重载回调"""
        self._callbacks.append(callback)

    def remove_callback(self, callback: callable) -> None:
        """移除重载回调"""
        if callback in self._callbacks:
            self._callbacks.remove(callback)


# ==================== 全局配置实例 ====================

_default_config: MechForgeConfig | None = None
_config_lock = threading.Lock()


def get_config(
    config_path: str | Path | None = None,
    force_reload: bool = False,
    enable_watcher: bool = False,
) -> MechForgeConfig:
    """获取配置（线程安全单例）

    Args:
        config_path: 配置文件路径
        force_reload: 强制重新加载
        enable_watcher: 启用配置热重载监视

    Returns:
        MechForgeConfig 实例
    """
    global _default_config

    with _config_lock:
        if _default_config is None or force_reload:
            _default_config = MechForgeConfig.from_file(config_path)

            # 启动配置监视器
            if enable_watcher:
                watcher = ConfigWatcher()
                watcher.start(config_path)
                watcher.on_reload(lambda: get_config(force_reload=True))

    return _default_config


def reload_config() -> MechForgeConfig:
    """重新加载配置"""
    return get_config(force_reload=True)


def save_config(config: MechForgeConfig, config_path: str | Path | None = None) -> None:
    """保存配置到文件"""
    config.to_file(config_path)


# ==================== 兼容旧代码 ====================


class KnowledgeConfigCompat:
    """兼容旧的 KnowledgeConfig"""

    def __init__(self):
        config = get_config()
        self.knowledge_path = config.knowledge.path
        self.rag_cache_dir = config.knowledge.rag.cache_dir
        self.use_rag = config.knowledge.rag.enabled


def load_config() -> KnowledgeConfigCompat:
    """旧版加载函数兼容"""
    return KnowledgeConfigCompat()
