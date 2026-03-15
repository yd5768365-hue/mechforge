"""
UI 渲染器模块 - 负责所有界面显示
"""

import random
import time
from datetime import datetime
from pathlib import Path

from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.rule import Rule
from rich.status import Status
from rich.table import Table
from rich.text import Text

console = Console()

# 有趣的欢迎语
_WELCOME_MESSAGES = [
    "机械之美，AI 来造 ~",
    "螺栓螺母已就位，等你提问~",
    "CAD/CAE 随问随答~",
    "材料力学老博士，在线答疑~",
    "有限元分析小能手，听候差遣~",
    "公差配合小专家，为你服务~",
    "机械设计好帮手，上线啦~",
]

# 思考提示
_THINKING_WITH_RAG = [
    "⚙️  结合知识库思考中...",
    "📐  分析结构中...",
    "🔧  查找机械手册...",
    "📊  计算中...",
    "🧠  思考中...",
    "📚  学习ing...",
]

_THINKING_WITHOUT_RAG = [
    "⚙️  齿轮转动中...",
    "📐  分析结构中...",
    "🔧  查找机械手册...",
    "📊  计算中...",
    "🧠  思考中...",
]

_RANDOM_WELCOME = random.choice(_WELCOME_MESSAGES)


class UIRenderer:
    """UI 渲染器"""

    def __init__(self, version: str = "v0.4.0"):
        self.version = version

    def print_banner(self):
        """打印横幅"""
        # 宽幅 ASCII Art Logo
        logo = """[cyan]███╗   ███╗███████╗ ██████╗██╗  ██╗███████╗ ██████╗ ██████╗  ██████╗ ███████╗
████╗ ████║██╔════╝██╔════╝██║  ██║██╔════╝██╔═══██╗██╔══██╗██╔════╝ ██╔════╝
██╔████╔██║█████╗  ██║     ███████║█████╗  ██║   ██║██████╔╝██║  ███╗█████╗
██║╚██╔╝██║██╔══╝  ██║     ██╔══██║██╔══╝  ██║   ██║██╔══██╗██║   ██║██╔══╝
██║ ╚═╝ ██║███████╗╚██████╗██║  ██║██║     ╚██████╔╝██║  ██║╚██████╔╝███████╗
╚═╝     ╚═╝╚══════╝ ╚═════╝╚═╝  ╚═╝╚═╝      ╚═════╝ ╚═╝  ╚═╝ ╚═════╝ ╚══════╝[/cyan]"""

        console = Console(force_terminal=True, no_color=False)

        # Spinner 加载（先显示）
        with console.status("[bold cyan]⚙ 系统初始化中...[/bold cyan]", spinner="dots12"):
            time.sleep(0.5)

        console.print()
        console.print(logo)

        # Rich Rule 分隔线
        console.print(Rule("[bold cyan]MechForge System Initialized", style="cyan"), style="cyan")

    def print_dashboard(
        self,
        api_type: str,
        model_name: str,
        rag_enabled: bool,
        kb_path: Path | None,
        top_k: int,
        msg_count: int,
    ):
        """打印系统状态面板 - 固定显示在屏幕右下角"""
        from rich.align import Align
        from rich.console import Console

        # 获取知识库状态
        kb_status = "未配置"
        if kb_path:
            kb_count = len(list(kb_path.glob("*.md")))
            kb_status = f"{kb_path.name}({kb_count})"

        # RAG 状态
        rag_status = "ON" if rag_enabled else "OFF"
        rag_color = "green" if rag_enabled else "red"

        # 系统时间
        now = datetime.now().strftime("%H:%M:%S")

        # 创建极简单行状态栏
        status_bar = (
            f"[dim]│[/dim] [cyan]API[/cyan] [white]{api_type}[/white] "
            f"[dim]│[/dim] [cyan]模型[/cyan] [white]{model_name}[/white] "
            f"[dim]│[/dim] [cyan]RAG[/cyan] [{rag_color}]{rag_status}[/{rag_color}] "
            f"[dim]│[/dim] [cyan]KB[/cyan] [white]{kb_status}[/white] "
            f"[dim]│[/dim] [cyan]消息[/cyan] [white]{msg_count}[/white] "
            f"[dim]│[/dim] [dim]{self.version} {now}[/dim] [dim]│[/dim]"
        )

        # 使用 ANSI 转义序列固定到屏幕底部右下角
        # \033[s 保存光标位置
        # \033[999;0H 移动到屏幕底部
        # \033[2K 清除当前行
        # \033[0J 清除到屏幕底部
        # \033[u 恢复光标位置
        console.print()
        # 右对齐显示状态栏
        console.print(Align.right(status_bar))

    def print_help_panel(self):
        """打印帮助面板 - 已禁用"""
        pass

    def print_welcome(self, history_count: int):
        """打印欢迎信息"""
        console.rule(style="dim")
        console.print(f"  [spring_green3]{_RANDOM_WELCOME}[/spring_green3]")
        console.print(f"  [dim]对话历史:[/dim] [spring_green3]{history_count} 条[/spring_green3]\n")

    def get_prompt(self) -> str:
        """获取输入提示符"""
        return "[spring_green3][MechForge] >[/spring_green3] "

    def get_thinking_message(self, has_context: bool = False) -> str:
        """获取思考提示消息"""
        if has_context:
            return random.choice(_THINKING_WITH_RAG)
        return random.choice(_THINKING_WITHOUT_RAG)

    def gear_spin(self, text: str = "系统初始化", duration: float = 1.0):
        """齿轮转动动画"""
        frames = ["[○○○] ", "[◐○○] ", "[◑○○] ", "[◒○○] ", "[◓○○] ", "[●●○] ", "[○●○] ", "[○○●] "]
        end_time = time.time() + duration
        while time.time() < end_time:
            for frame in frames:
                if time.time() >= end_time:
                    break
                print(f"\r{frame}{text}...", end="", flush=True)
                time.sleep(0.1)
        print(f"\r    {text}... ✓")
        # 添加水平分隔线
        console.print(Rule(style="dim cyan"))

    def thinking_spinner(self, message: str):
        """带动画的思考"""
        with Status(message, console=console, spinner="dots12"):
            yield

    def print_command_help(self):
        """打印命令帮助"""
        help_text = Text(
            """
/status    查看系统状态
/info      显示会话信息
/rag       开关 RAG 知识库检索
/history   查看对话历史
/clear     清除对话历史
/reload    重新加载配置
/model     配置 AI 模型
/exit      退出
""",
            style="spring_green3",
        )
        console.print(
            Panel(
                help_text,
                title="[bold orange1]MechForge AI - 可用命令[/bold orange1]",
                border_style="orange1",
                padding=(0, 2),
            )
        )

    def print_session_info(
        self,
        conversation_count: int,
        command_count: int,
        rag_enabled: bool,
        provider: str,
        kb_path: Path | None,
    ):
        """打印会话信息"""
        print("""
+================================================================+
|                    会话信息                                |
+================================================================+
""")
        print(f"  对话轮数: {conversation_count // 2}")
        print(f"  消息数:  {conversation_count}")
        print(f"  命令历史: {command_count}")
        print(f"  RAG:     {'启用' if rag_enabled else '禁用'}")
        print(f"  Provider: {provider}")
        print(f"  知识库:  {kb_path or '未配置'}")
        print()

    def print_conversation_history(self, history: list):
        """打印对话历史"""
        if not history:
            print("对话历史为空")
            return

        print("""
+================================================================+
|                    对话历史                                |
+================================================================+
""")
        for msg in history[-10:]:
            role = msg.get("role", "unknown")
            content = msg.get("content", "")[:80]
            if role == "user":
                print(f"[你]: {content}")
            else:
                print(f"[AI]: {content}...")
            print()
        print(f"(显示最近 10 条，共 {len(history)} 条)\n")

    def print_error(self, error_type: str, message: str):
        """打印错误信息"""
        if error_type == "connection":
            print("\n\n[错误] 无法连接到 AI 服务")
            print("请检查:")
            print("  1. 网络连接是否正常")
            print("  2. Ollama 是否已启动 (ollama serve)")
            print("  3. 或使用 /model 配置其他 AI 提供商")
        elif error_type == "timeout":
            print("\n\n[错误] 请求超时")
            print("请尝试:")
            print("  1. 使用更小的模型")
            print("  2. 检查网络连接")
        elif error_type == "api":
            print(f"\n\n[错误] API 调用失败: {message[:50]}")
            print("请检查 API Key 是否正确，或尝试 /model 重新配置")
        else:
            print(f"\n\n[错误] {message[:100]}")
            print("请尝试 /model 重新配置或检查网络连接")
