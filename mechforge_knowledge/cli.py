"""
MechForge AI 知识库搜索 CLI

纯知识库检索模式：强制使用知识库原文回答，不允许 AI 生成
"""

import sys
from datetime import datetime
from pathlib import Path

from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.rule import Rule
from rich.table import Table
from rich.text import Text

console = Console()

# 设置 UTF-8 输出
if sys.platform == "win32" and hasattr(sys.stdout, "buffer"):
    import io

    try:
        if not isinstance(sys.stdout, io.TextIOWrapper):
            sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
        if not isinstance(sys.stderr, io.TextIOWrapper):
            sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")
    except Exception:
        pass


def _find_knowledge_path() -> Path | None:
    """查找知识库路径（使用核心模块的统一函数）"""
    from mechforge_core.config import find_knowledge_path as core_find_path
    return core_find_path()


def load_knowledge_files(knowledge_dir: Path) -> list[dict]:
    """加载知识库文件"""
    documents = []

    if not knowledge_dir.exists():
        return documents

    for md_file in knowledge_dir.glob("*.md"):
        try:
            with open(md_file, encoding="utf-8", errors="ignore") as f:
                content = f.read()

            # 提取标题
            title = md_file.stem.replace("_", " ").replace("-", " ").title()
            for line in content.split("\n"):
                if line.strip().startswith("#"):
                    title = line.strip().lstrip("#").strip()
                    break

            documents.append(
                {
                    "id": md_file.stem,
                    "title": title,
                    "content": content,
                    "source": str(md_file),
                    "filename": md_file.name,
                }
            )
        except Exception:
            pass

    return documents


def search_by_keyword(knowledge_dir: Path, query: str, limit: int = 10) -> list[dict]:
    """关键词搜索"""
    documents = load_knowledge_files(knowledge_dir)

    if not documents:
        return []

    query_lower = query.lower()
    query_words = query_lower.replace(" ", "").replace(",", "")

    results = []
    for doc in documents:
        _content_lower = doc["content"].lower()
        filename_lower = doc["filename"].lower()

        score = 0
        matched_lines = []

        # 文件名匹配
        if query_lower in filename_lower:
            score += 100

        # 标题匹配
        title_lower = doc["title"].lower()
        if query_lower in title_lower:
            score += 50

        # 内容匹配
        lines = doc["content"].split("\n")
        for i, line in enumerate(lines):
            line_lower = line.lower()
            if query_lower in line_lower:
                start = max(0, i - 1)
                end = min(len(lines), i + 2)
                context = "\n".join(lines[start:end])
                matched_lines.append(
                    {
                        "line_num": i + 1,
                        "content": line.strip(),
                        "context": context,
                    }
                )
                score += 10
            elif any(word in line_lower for word in query_words if len(word) > 1):
                score += 1

        if score > 0:
            results.append(
                {
                    "title": doc["title"],
                    "filename": doc["filename"],
                    "source": doc["source"],
                    "score": score,
                    "matches": matched_lines[:5],
                    "content": doc["content"],
                }
            )

    results.sort(key=lambda x: x["score"], reverse=True)
    return results[:limit]


def print_result(result: dict, index: int):
    """打印单条搜索结果"""
    title = result.get("title", "未知")
    filename = result.get("filename", "")
    source = result.get("source", "")
    matches = result.get("matches", [])
    content = result.get("content", "")

    print(f"\n{'=' * 60}")
    print(f"[{index}] {title}")
    if filename:
        print(f"    文件: {filename}")
    print(f"{'=' * 60}")

    # 显示匹配的内容
    if matches:
        print("\n--- 匹配内容 ---")
        for match in matches:
            print(f"\n行 {match['line_num']}:")
            print(match["context"])
    else:
        # 显示内容摘要
        print("\n--- 内容摘要 ---")
        # 提取前几段有意义的内容
        lines = content.split("\n")
        content_lines = []
        for line in lines:
            line = line.strip()
            if line and not line.startswith("#") and len(line) > 10:
                content_lines.append(line)
                if len(content_lines) >= 5:
                    break
        print("\n".join(content_lines))

    print(f"\n来源: {source}")


def print_banner(doc_count: int = 0):
    """打印横幅"""
    now = datetime.now().strftime("%H:%M:%S")

    # ASCII Art Logo
    logo = """[cyan]███╗   ███╗███████╗ ██████╗██╗  ██╗███████╗ ██████╗ ██████╗  ██████╗ ███████╗
████╗ ████║██╔════╝██╔════╝██║  ██║██╔════╝██╔═══██╗██╔══██╗██╔════╝ ██╔════╝
██╔████╔██║█████╗  ██║     ███████║█████╗  ██║   ██║██████╔╝██║  ███╗█████╗
██║╚██╔╝██║██╔══╝  ██║     ██╔══██║██╔══╝  ██║   ██║██╔══██╗██║   ██║██╔══╝
██║ ╚═╝ ██║███████╗╚██████╗██║  ██║██║     ╚██████╔╝██║  ██║╚██████╔╝███████╗
╚═╝     ╚═╝╚══════╝ ╚═════╝╚═╝  ╚═╝╚═╝      ╚═════╝ ╚═╝  ╚═╝ ╚═════╝ ╚══════╝[/cyan]"""

    console.print(logo)

    # 使用 Rich Rule 添加分隔线
    console.print(Rule("[bold cyan]Knowledge Base Ready", style="cyan"), style="cyan")

    # 创建状态表格
    grid = Table(box=box.SIMPLE_HEAVY, padding=(0, 1), show_edge=False, border_style="dim cyan")
    grid.add_column(width=10, style="orange1")
    grid.add_column(width=18, style="spring_green3")
    grid.add_column(width=10, style="orange1")
    grid.add_column(width=18, style="spring_green3")

    grid.add_row("[bold]模式", "知识库检索", "[bold]文档", f"{doc_count} 篇")
    grid.add_row("[bold]版本", "v0.4.0", "[bold]运行", f"[dim]{now}[/dim]")

    console.print(grid)

    # 打印标题
    title = Text("MechForge AI", style="bold orange1")
    subtitle = Text("知识库检索 - 精准搜索 拒绝幻觉", style="italic dim")
    console.print(Panel.fit(title, subtitle=subtitle, border_style="orange1", padding=(0, 2)))
    console.rule(style="dim")


def main():
    """知识库搜索主函数"""
    import argparse

    parser = argparse.ArgumentParser(
        prog="mechforge-k", description="MechForge Knowledge Base Search"
    )
    parser.add_argument("--version", action="version", version="%(prog)s 0.4.0")
    _args = parser.parse_args()

    # 查找知识库
    knowledge_path = _find_knowledge_path()

    if not knowledge_path:
        print("错误: 未找到知识库目录")
        print("请在以下位置放置 .md 文件:")
        print("  1. ./knowledge/")
        print("  2. ~/knowledge/")
        print("  3. 当前目录 knowledge/")
        sys.exit(1)

    # 加载文档
    docs = load_knowledge_files(knowledge_path)

    if not docs:
        print("错误: 知识库为空")
        sys.exit(1)

    print_banner(len(docs))
    console.print(f"[dim]知识库:[/dim] [spring_green3]{knowledge_path}[/spring_green3]")
    console.print(f"[dim]文档数:[/dim] [spring_green3]{len(docs)} 篇[/spring_green3]")
    console.print(
        "\n[spring_green3]输入关键词搜索[/spring_green3] [dim]|[/dim] [spring_green3]/list[/spring_green3] [dim]查看文档[/dim] [spring_green3]/exit[/spring_green3] [dim]退出[/dim]\n"
    )

    while True:
        try:
            query = console.input("[spring_green3][MechForge] >[/spring_green3] ").strip()

            if not query:
                continue

            if query.lower() in ["/exit", "/q", "/quit"]:
                print("\n再见!\n")
                break

            if query.lower() == "/list":
                # 列出所有文档
                print("\n--- 文档列表 ---")
                for i, doc in enumerate(docs, 1):
                    size = len(doc["content"])
                    size_str = f"{size / 1024:.1f}KB" if size > 1024 else f"{size}B"
                    print(f"  {i:2d}. {doc['title']:<40} {size_str}")
                print()
                continue

            if query.lower() == "/help":
                print("""
命令:
  /list     - 列出所有文档
  /exit     - 退出

直接输入关键词搜索知识库
                """)
                continue

            # 搜索
            results = search_by_keyword(knowledge_path, query, limit=3)

            if not results:
                print(f"\n未找到与「{query}」相关的知识\n")
                continue

            print(f"\n找到 {len(results)} 条相关结果:\n")

            for i, result in enumerate(results, 1):
                print_result(result, i)

            print("\n" + "-" * 60)

        except (EOFError, KeyboardInterrupt):
            print("\n\n再见!\n")
            break


if __name__ == "__main__":
    main()
