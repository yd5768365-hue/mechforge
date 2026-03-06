#!/usr/bin/env python3
"""
本地模型管理 CLI

统一管理 Ollama 和 GGUF 模型：
- 列出可用模型
- 启动/停止模型服务
- 下载新模型
- 测试模型连接

用法:
    mechforge-model list          # 列出所有模型
    mechforge-model serve         # 启动 GGUF 服务器
    mechforge-model select        # 交互式选择模型
    mechforge-model test          # 测试模型连接
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "packages"))

from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()


def cmd_list(args):
    """列出可用模型"""
    from mechforge_core.local_model_manager import LocalModelManager

    manager = LocalModelManager()
    models = manager.scan_models()

    if not models:
        console.print(
            Panel(
                "未找到任何本地模型\n\n"
                "[cyan]建议操作:[/cyan]\n"
                "1. 安装 Ollama: [green]curl -fsSL https://ollama.com/install.sh | sh[/green]\n"
                "2. 下载模型: [green]ollama pull qwen2.5:1.5b[/green]\n"
                "3. 下载 GGUF: 放到 [green]./models/[/green] 目录",
                title="[yellow]⚠ 无可用模型[/yellow]",
                border_style="yellow",
            )
        )
        return 1

    table = Table(title="本地模型列表", box=box.ROUNDED, show_header=True, header_style="bold cyan")

    table.add_column("#", width=3, justify="center")
    table.add_column("提供商", width=8)
    table.add_column("模型名称", style="cyan")
    table.add_column("大小", justify="right")
    table.add_column("状态", width=10)
    table.add_column("API 地址", style="dim")

    for i, model in enumerate(models, 1):
        provider_icon = "🦙" if model.provider == "ollama" else "📦"
        size_str = f"{model.size / 1024 / 1024:.1f} MB"
        status = "[green]运行中[/green]" if model.loaded else "[dim]未加载[/dim]"

        table.add_row(str(i), provider_icon, model.name, size_str, status, model.url)

    console.print(table)
    console.print(f"\n总计: {len(models)} 个模型")
    return 0


def cmd_serve(args):
    """启动 GGUF 服务器"""
    from mechforge_core.gguf_server import GGUFModelServer

    model_path = Path(args.model)
    if not model_path.exists():
        # 尝试在 models 目录查找
        model_path = Path("./models") / args.model
        if not model_path.exists() and not str(args.model).endswith(".gguf"):
            model_path = Path("./models") / f"{args.model}.gguf"

    if not model_path.exists():
        console.print(f"[red]错误: 模型文件不存在: {args.model}[/red]")
        return 1

    server = GGUFModelServer(
        model_path=str(model_path),
        host=args.host,
        port=args.port,
        n_ctx=args.ctx,
        n_gpu_layers=args.gpu_layers,
    )

    if server.load_model():
        console.print(
            Panel(
                f"[green]模型:[/green] {model_path.name}\n"
                f"[green]地址:[/green] http://{args.host}:{args.port}\n"
                f"[green]API:[/green] http://{args.host}:{args.port}/api/chat\n\n"
                f"[dim]按 Ctrl+C 停止服务[/dim]",
                title="[cyan]🚀 GGUF 服务器启动[/cyan]",
                border_style="green",
            )
        )

        try:
            server.run_http_server()
        except KeyboardInterrupt:
            console.print("\n[yellow]服务器已停止[/yellow]")
            return 0

    return 1


def cmd_select(args):
    """交互式选择模型"""
    from mechforge_core.local_model_manager import LocalModelManager

    manager = LocalModelManager()
    selected = manager.select_model_interactive()

    if selected:
        provider, url = manager.get_model_for_config(selected)
        console.print(
            Panel(
                f"[green]已选择:[/green] {selected}\n"
                f"[green]提供商:[/green] {provider}\n"
                f"[green]API 地址:[/green] {url}\n\n"
                f"[dim]更新配置使用此模型...[/dim]",
                title="[cyan]✓ 模型选择[/cyan]",
                border_style="green",
            )
        )

        # 保存到配置文件
        if args.save:
            from mechforge_core.config import get_config, save_config

            config = get_config()
            config.provider.default = provider

            if provider == "ollama":
                config.provider.ollama.url = url
                config.provider.ollama.model = selected.split(":")[1]
            elif provider == "local":
                config.provider.local.model_dir = "./models"

            save_config(config)
            console.print("[green]配置已保存[/green]")

        return 0

    console.print("[yellow]未选择模型[/yellow]")
    return 1


def cmd_test(args):
    """测试模型连接"""
    import requests

    from mechforge_core.local_model_manager import LocalModelManager

    manager = LocalModelManager()
    models = manager.scan_models()

    if not models:
        console.print("[red]未找到可用模型[/red]")
        return 1

    console.print("[cyan]测试模型连接...[/cyan]\n")

    for model in models:
        console.print(f"测试 {model.name}...", end=" ")

        if not model.loaded:
            if model.provider == "gguf":
                console.print("[yellow]未运行，尝试启动...[/yellow]")
                if not manager.start_gguf_server(model.name):
                    console.print("[red]启动失败[/red]")
                    continue
            else:
                console.print("[red]未运行[/red]")
                continue

        # 测试 API
        try:
            resp = requests.post(
                f"{model.url}/api/chat",
                json={
                    "model": model.name,
                    "messages": [{"role": "user", "content": "Hi"}],
                    "stream": False,
                },
                timeout=30,
            )

            if resp.status_code == 200:
                console.print("[green]✓ 连接成功[/green]")
            else:
                console.print(f"[red]✗ 错误: {resp.status_code}[/red]")
        except Exception as e:
            console.print(f"[red]✗ 失败: {e}[/red]")

    return 0


def cmd_download(args):
    """下载模型"""
    console.print(
        Panel(
            "[cyan]Ollama 模型下载:[/cyan]\n"
            f"  [green]ollama pull {args.model}[/green]\n\n"
            "[cyan]GGUF 模型下载:[/cyan]\n"
            "  1. 从 HuggingFace 下载 .gguf 文件\n"
            "  2. 放到 [green]./models/[/green] 目录\n\n"
            "[cyan]推荐模型:[/cyan]\n"
            "  • qwen2.5:1.5b (小，快)\n"
            "  • llama3.2:3b (英文好)\n"
            "  • gemma2:2b (轻量)",
            title="[cyan]⬇️ 模型下载[/cyan]",
            border_style="cyan",
        )
    )
    return 0


def main():
    parser = argparse.ArgumentParser(
        prog="mechforge-model",
        description="本地模型管理工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  mechforge-model list                    # 列出所有模型
  mechforge-model serve -m qwen.gguf      # 启动 GGUF 服务器
  mechforge-model select --save           # 选择并保存默认模型
  mechforge-model test                    # 测试所有模型
        """,
    )

    subparsers = parser.add_subparsers(dest="command", help="可用命令")

    # list 命令
    list_parser = subparsers.add_parser("list", help="列出可用模型")
    list_parser.set_defaults(func=cmd_list)

    # serve 命令
    serve_parser = subparsers.add_parser("serve", help="启动 GGUF 服务器")
    serve_parser.add_argument("-m", "--model", required=True, help="GGUF 模型路径")
    serve_parser.add_argument("-H", "--host", default="127.0.0.1", help="服务器地址")
    serve_parser.add_argument("-p", "--port", type=int, default=11435, help="服务器端口")
    serve_parser.add_argument("-c", "--ctx", type=int, default=2048, help="上下文长度")
    serve_parser.add_argument("-g", "--gpu-layers", type=int, default=0, help="GPU 层数")
    serve_parser.set_defaults(func=cmd_serve)

    # select 命令
    select_parser = subparsers.add_parser("select", help="交互式选择模型")
    select_parser.add_argument("--save", action="store_true", help="保存为默认模型")
    select_parser.set_defaults(func=cmd_select)

    # test 命令
    test_parser = subparsers.add_parser("test", help="测试模型连接")
    test_parser.set_defaults(func=cmd_test)

    # download 命令
    download_parser = subparsers.add_parser("download", help="显示下载帮助")
    download_parser.add_argument("model", nargs="?", help="模型名称")
    download_parser.set_defaults(func=cmd_download)

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
