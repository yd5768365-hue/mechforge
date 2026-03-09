"""
全局应用状态管理
"""

from typing import Any, Dict, List, Optional

from mechforge_core.config import get_config


class AppState:
    """应用全局状态"""

    def __init__(self) -> None:
        self.llm_client: Optional[Any] = None
        self.rag_engine: Optional[Any] = None
        self.conversation_history: List[Dict[str, str]] = []
        self.config = get_config()
        # 当前使用的 provider: 'ollama' 或 'gguf'
        self.current_provider: str = "ollama"
        # GGUF 本地模型状态
        self.gguf_model_path: Optional[str] = None
        self.gguf_llm: Optional[Any] = None


# 全局状态实例
state = AppState()