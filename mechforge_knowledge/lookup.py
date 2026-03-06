"""
MechForge Knowledge - 知识库查阅模式

纯检索搬运模式：只返回知识库原文 + 上下文，不允许 AI 自由生成
"""

import sys
from pathlib import Path
from typing import Any

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table

console = Console()


def _get_cache_dir() -> Path:
    """获取缓存目录"""
    if getattr(sys, "frozen", False):
        base = Path(sys._MEIPASS)
    else:
        base = Path(__file__).parent.parent.parent.parent
    return base / ".cache" / "rag"


def load_knowledge_files(knowledge_dir: Path) -> list[dict[str, str]]:
    """加载知识库文件"""
    documents = []

    if not knowledge_dir.exists():
        return documents

    for md_file in knowledge_dir.glob("*.md"):
        try:
            with open(md_file, encoding="utf-8", errors="ignore") as f:
                content = f.read()

            # 提取标题（从第一个 # 开头的内容）
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


def search_by_keyword(knowledge_dir: Path, query: str, limit: int = 10) -> list[dict[str, Any]]:
    """关键词精确搜索"""
    documents = load_knowledge_files(knowledge_dir)

    if not documents:
        return []

    query_lower = query.lower()
    query_words = query_lower.replace(" ", "").replace(",", "")

    results = []
    for doc in documents:
        _content_lower = doc["content"].lower()
        filename_lower = doc["filename"].lower()

        # 多重匹配计分
        score = 0

        # 1. 文件名精确匹配（最高优先级）
        if query_lower in filename_lower:
            score += 100

        # 2. 标题匹配
        title_lower = doc["title"].lower()
        if query_lower in title_lower:
            score += 50

        # 3. 在内容中搜索关键词
        lines = doc["content"].split("\n")
        matched_lines = []

        for i, line in enumerate(lines):
            line_lower = line.lower()
            # 精确短语匹配
            if query_lower in line_lower:
                # 获取上下文（前后各一行）
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
            # 关键词匹配（每个词）
            elif any(word in line_lower for word in query_words if len(word) > 1):
                score += 1

        if score > 0:
            results.append(
                {
                    "title": doc["title"],
                    "filename": doc["filename"],
                    "source": doc["source"],
                    "score": score,
                    "matches": matched_lines[:5],  # 最多5个匹配点
                    "content_preview": doc["content"][:500],
                }
            )

    # 排序
    results.sort(key=lambda x: x["score"], reverse=True)
    return results[:limit]


def format_result(result: dict[str, Any], index: int) -> None:
    """格式化输出单条结果"""
    title = result.get("title", "Untitled")
    filename = result.get("filename", "")
    source = result.get("source", "")
    matches = result.get("matches", [])

    # 标题面板
    header = f"[bold cyan]{index}.[/bold cyan] {title}"
    if filename:
        header += f" [dim]({filename})[/dim]"

    console.print(f"\n{header}")

    # 匹配内容
    if matches:
        for match in matches:
            console.print(f"  [yellow]行 {match['line_num']}:[/yellow] {match['content'][:100]}")
    else:
        # 显示内容预览
        preview = result.get("content_preview", "")[:200]
        console.print(f"  [dim]{preview}...[/dim]")

    # 来源
    console.print(f"  [dim]来源: {source}[/dim]")


def show_category_menu(knowledge_dir: Path) -> str | None:
    """显示知识库分类菜单"""
    documents = load_knowledge_files(knowledge_dir)

    if not documents:
        console.print("[yellow]知识库为空[/yellow]")
        return None

    # 按文件名分类
    categories: dict[str, list[dict]] = {}
    for doc in documents:
        # 简单分类：按文件名主要特征
        name = doc["filename"].lower()
        if "material" in name:
            cat = "材料"
        elif "standard" in name or "part" in name:
            cat = "标准件"
        elif "toleranc" in name:
            cat = "公差"
        elif "mechanic" in name:
            cat = "力学"
        elif "solidwork" in name or "freecad" in name:
            cat = "CAD"
        elif "fem" in name or "fea" in name:
            cat = "CAE"
        else:
            cat = "其他"

        if cat not in categories:
            categories[cat] = []
        categories[cat].append(doc)

    # 显示分类菜单
    console.print(
        Panel(
            "[bold]知识库分类[/bold]\n"
            + "\n".join(
                f"  {i + 1}. {cat} ({len(docs)} 篇)"
                for i, (cat, docs) in enumerate(categories.items())
            ),
            title="📚 查阅模式",
            border_style="cyan",
        )
    )

    return None


def interactive_lookup(knowledge_dir: Path) -> None:
    """交互式查阅"""
    console.print(
        Panel(
            "[bold cyan]📚 MechForge Knowledge 知识库查阅模式[/bold cyan]\n\n"
            "纯检索搬运：只返回知识库原文，不允许 AI 生成\n"
            "输入关键词查找手册、零件、标准等\n\n"
            "[dim]命令:[/dim]\n"
            "  /list   - 查看知识库目录\n"
            "  /cat    - 分类浏览\n"
            "  /open   - 打开指定文档\n"
            "  /exit   - 退出",
            title="知识库查阅",
            border_style="cyan",
            expand=False,
        )
    )

    # 显示统计
    docs = load_knowledge_files(knowledge_dir)
    console.print(f"[dim]知识库: {len(docs)} 个文档[/dim]\n")

    while True:
        try:
            query = Prompt.ask("\n[bold cyan]查[/bold cyan] ").strip()

            if not query:
                continue

            # 处理命令
            if query.startswith("/"):
                cmd = query.lower()
                if cmd in ["/exit", "/q"]:
                    console.print("[yellow]退出查阅模式[/yellow]")
                    break
                elif cmd == "/list":
                    _show_doc_list(knowledge_dir)
                elif cmd == "/cat":
                    show_category_menu(knowledge_dir)
                elif cmd.startswith("/open "):
                    doc_name = query[6:].strip()
                    _open_document(knowledge_dir, doc_name)
                else:
                    console.print("[yellow]未知命令[/yellow]")
                continue

            # 执行搜索
            results = search_by_keyword(knowledge_dir, query, limit=5)

            if not results:
                console.print(f"[yellow]未找到与「{query}」相关的内容[/yellow]")
                continue

            console.print(f"\n[bold]找到 {len(results)} 条相关结果:[/bold]")

            for i, result in enumerate(results, 1):
                format_result(result, i)

            console.print("\n[dim]输入编号查看详情，或继续搜索[/dim]")

        except (EOFError, KeyboardInterrupt):
            console.print("\n[yellow]退出查阅模式[/yellow]")
            break


def _show_doc_list(knowledge_dir: Path) -> None:
    """显示文档列表"""
    docs = load_knowledge_files(knowledge_dir)

    if not docs:
        console.print("[yellow]知识库为空[/yellow]")
        return

    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("序号", justify="right")
    table.add_column("文档名")
    table.add_column("大小", justify="right")

    for i, doc in enumerate(docs, 1):
        size = len(doc["content"])
        size_str = f"{size / 1024:.1f}KB" if size > 1024 else f"{size}B"
        table.add_row(str(i), doc["title"], size_str)

    console.print(table)


def _open_document(knowledge_dir: Path, doc_name: str) -> None:
    """打开指定文档"""
    docs = load_knowledge_files(knowledge_dir)

    # 精确匹配或模糊匹配
    matched = None
    for doc in docs:
        if doc["filename"].lower() == doc_name.lower():
            matched = doc
            break
        if doc_name.lower() in doc["filename"].lower():
            matched = doc
            break

    if not matched:
        console.print(f"[yellow]未找到文档: {doc_name}[/yellow]")
        return

    # 显示文档内容
    console.print(
        Panel(
            matched["content"][:3000],
            title=matched["title"],
            border_style="green",
        )
    )


def quick_lookup(knowledge_dir: Path, query: str) -> None:
    """快速查阅（单次查询）"""
    results = search_by_keyword(knowledge_dir, query, limit=3)

    if not results:
        console.print(f"[yellow]未找到与「{query}」相关的内容[/yellow]")
        return

    for i, result in enumerate(results, 1):
        format_result(result, i)


# 导出
__all__ = ["interactive_lookup", "quick_lookup", "search_by_keyword", "load_knowledge_files"]
