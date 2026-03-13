"""
全局应用状态管理
"""

from typing import Any

from mechforge_core.config import get_config


class AppState:
    """应用全局状态"""

    def __init__(self) -> None:
        self.llm_client: Any | None = None
        self.rag_engine: Any | None = None
        self.conversation_history: list[dict[str, str]] = []
        self.config = get_config()
        # 当前使用的 provider: 'ollama' 或 'gguf'
        self.current_provider: str = "ollama"
        # GGUF 本地模型状态
        self.gguf_model_path: str | None = None
        self.gguf_llm: Any | None = None
        # 当前模式: 'chat' 正常对话 或 'knowledge' 知识库模式
        self.mode: str = "chat"
        # 系统提示词配置
        self.system_prompts = {
            "chat": """You are a friendly and helpful AI assistant named MechForge AI.
You communicate in a warm, conversational tone like a knowledgeable friend.
Feel free to engage in casual conversation, tell jokes, and be approachable.
You can discuss a wide range of topics and help users with various questions.
Always be supportive, encouraging, and easy to talk to.
Respond in the same language as the user's message.

Current mode: NORMAL CHAT - Friendly conversation mode activated.""",
            "knowledge": """You are MechForge AI in KNOWLEDGE BASE MODE.
You are a strict, professional technical assistant focused ONLY on mechanical engineering and related technical topics.
You MUST follow these rules:
1. ONLY answer questions related to mechanical engineering, CAD, CAE, manufacturing, materials, and technical topics
2. If a question is NOT related to these topics, respond: "This question is outside my knowledge base scope. Please switch to AI Chat Mode for general conversation."
3. Use technical terminology precisely and professionally
4. Base your answers strictly on the provided context from the knowledge base
5. If the context doesn't contain relevant information, say: "I cannot find relevant information in the knowledge base for this query."
6. Do NOT engage in casual conversation, jokes, or off-topic discussion
7. Maintain a formal, academic tone at all times
8. Cite specific sections from the knowledge base when possible

Current mode: KNOWLEDGE BASE - Strict technical mode activated.""",
        }

    def get_mode(self) -> str:
        """获取当前模式"""
        return self.mode

    def get_system_prompt(self) -> str:
        """获取当前模式的系统提示词"""
        return self.system_prompts.get(self.mode, self.system_prompts["chat"])

    def set_mode(self, mode: str) -> bool:
        """设置当前模式"""
        if mode in self.system_prompts:
            self.mode = mode
            return True
        return False

    def is_knowledge_mode(self) -> bool:
        """是否为知识库模式"""
        return self.mode == "knowledge"


# 全局状态实例
state = AppState()
