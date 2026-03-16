"""
MechForge AI 终端聊天界面

机械设计专业 AI 垂直助手
"""

import json
from pathlib import Path

from mechforge_core.config import get_config
from mechforge_theme.components import UIRenderer

from mechforge_ai.command_handler import CommandHandler
from mechforge_ai.llm_client import LLMClient
from mechforge_ai.rag_engine import RAGEngine


class MechForgeTerminal:
    """MechForge AI 终端聊天界面"""

    def __init__(self, model: str | None = None):
        # 加载统一配置
        self.config = get_config()

        self.running = False
        self.conversation_history: list[dict] = []
        self.command_history: list[str] = []
        self._last_history_input: str = ""

        # 初始化各模块
        self.llm = LLMClient(model)
        self.llm.conversation_history = self.conversation_history
        self.ui = UIRenderer(version="v0.4.0")
        self.command_handler = CommandHandler(self.config)

        # RAG 引擎（延迟初始化）
        self.rag_enabled = self.config.knowledge.rag.enabled
        self._rag_engine: RAGEngine | None = None

        # 加载对话历史
        self._load_conversation_history()

    @property
    def rag_engine(self) -> RAGEngine:
        """延迟加载 RAG 引擎"""
        if self._rag_engine is None:
            self._rag_engine = self._create_rag_engine()
        return self._rag_engine

    def _create_rag_engine(self) -> RAGEngine:
        """创建 RAG 引擎（使用统一的路径查找）"""
        from mechforge_core.config import find_knowledge_path
        knowledge_path = find_knowledge_path()

        return RAGEngine(knowledge_path=knowledge_path, top_k=self.config.knowledge.rag.top_k)

    def start(self):
        """启动终端"""
        self.running = True

        # 加载命令历史
        self._load_command_history()

        # 启动动画
        print()
        self.ui.gear_spin("系统启动中", 0.8)
        self.ui.print_banner()

        # 获取知识库路径（不触发 RAG 引擎加载）
        kb_path = None
        if self.rag_enabled:
            kb_path = self.rag_engine.knowledge_path
        else:
            # 直接检查配置路径
            config_path = Path(self.config.knowledge.path)
            if config_path.exists():
                kb_path = config_path

        self.ui.print_dashboard(
            api_type=self.llm.get_api_type(),
            model_name=self.llm.get_current_model_name(),
            rag_enabled=self.rag_enabled,
            kb_path=kb_path,
            top_k=self.config.knowledge.rag.top_k,
            msg_count=len(self.conversation_history),
        )

        # 打印帮助
        self.ui.print_help_panel()
        self.ui.print_welcome(len(self.conversation_history))

        # 主循环
        history_index = -1

        while self.running:
            try:
                # 输入
                user_input = self._input_with_history(history_index)
                print()

                if not user_input:
                    continue

                # 更新历史
                if user_input != self._last_history_input:
                    self.command_history.append(user_input)
                    self._last_history_input = user_input

                history_index = -1
                self._handle_input(user_input)

                # 保存命令历史
                self._save_command_history()

            except (EOFError, ValueError):
                break
            except KeyboardInterrupt:
                print("\n\n使用 /exit 退出")
                continue

        # 退出
        self._save_conversation_history()
        print("\n再见! 期待下次相遇~\n")

    def _input_with_history(self, history_index: int = -1) -> str:
        """带命令历史的输入"""
        from rich.console import Console

        console = Console()
        try:
            import readline  # noqa: F401

            if history_index < 0:
                return console.input(self.ui.get_prompt()).strip()
            else:
                if history_index < len(self.command_history):
                    return self.command_history[-(history_index + 1)]
                return ""
        except ImportError:
            return console.input(self.ui.get_prompt()).strip()

    def _load_command_history(self):
        """加载命令历史"""
        try:
            import readline  # noqa: F401

            history_file = Path.home() / ".mechforge" / "history"
            if history_file.exists():
                with open(history_file, encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if line:
                            readline.add_history(line)
                            self.command_history.append(line)
        except Exception:
            pass

    def _save_command_history(self):
        """保存命令历史"""
        try:
            history_file = Path.home() / ".mechforge" / "history"
            history_file.parent.mkdir(parents=True, exist_ok=True)
            with open(history_file, "w", encoding="utf-8") as f:
                for cmd in self.command_history[-100:]:
                    f.write(f"{cmd}\n")
        except Exception:
            pass

    def _load_conversation_history(self):
        """加载对话历史"""
        try:
            conv_file = Path.home() / ".mechforge" / "conversation.json"
            if conv_file.exists():
                with open(conv_file, encoding="utf-8") as f:
                    self.conversation_history = json.load(f)
        except Exception:
            pass

    def _save_conversation_history(self):
        """保存对话历史"""
        try:
            conv_file = Path.home() / ".mechforge" / "conversation.json"
            conv_file.parent.mkdir(parents=True, exist_ok=True)
            with open(conv_file, "w", encoding="utf-8") as f:
                json.dump(self.conversation_history[-50:], f, ensure_ascii=False, indent=2)
        except Exception:
            pass

    def _handle_input(self, user_input: str):
        """处理用户输入"""
        if user_input.startswith("/"):
            # 命令模式
            should_exit = self.command_handler.handle(user_input, self)
            if should_exit:
                self.running = False
            return

        # 对话模式
        self.conversation_history.append({"role": "user", "content": user_input})
        self._call_api(user_input)

    def _call_api(self, user_input: str):
        """调用 AI API"""
        # 检查是否需要 RAG
        context = ""
        use_rag = self.rag_enabled or (
            self.rag_engine.is_available and self.rag_engine.check_trigger(user_input)
        )

        if use_rag and self.rag_engine.is_available:
            print("📚 正在检索知识库...")
            context = self.rag_engine.search(user_input)

        # 思考提示
        think_msg = self.ui.get_thinking_message(bool(context))

        # 使用动画调用 API
        try:
            # 模拟 Status 上下文
            from rich.console import Console
            from rich.status import Status

            console = Console()

            with Status(think_msg, console=console, spinner="dots12"):
                response = self.llm.call(user_input, context)

            # 打印响应
            print()
            console.print(response, style="cyan")
            self.conversation_history.append({"role": "assistant", "content": response})

        except Exception as e:
            error_msg = str(e)
            if "connection" in error_msg.lower():
                self.ui.print_error("connection", error_msg)
            elif "timeout" in error_msg.lower():
                self.ui.print_error("timeout", error_msg)
            elif "api" in error_msg.lower():
                self.ui.print_error("api", error_msg)
            else:
                self.ui.print_error("unknown", error_msg)


def main():
    """CLI entry point"""
    import argparse

    parser = argparse.ArgumentParser(
        prog="mechforge", description="MechForge AI - Mechanical Engineering AI Assistant"
    )
    parser.add_argument("--version", action="version", version="%(prog)s 0.4.0")
    _args = parser.parse_args()

    terminal = MechForgeTerminal()
    terminal.start()


if __name__ == "__main__":
    main()
