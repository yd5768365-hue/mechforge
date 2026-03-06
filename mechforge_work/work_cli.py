"""
MechForge Work - CAE Workbench CLI

基于 Gmsh + CalculiX + PyVista 的轻量级 CAE 工作台

技术栈（2026 最优）：
- Gmsh: 几何 + 网格 (pip install gmsh)
- CalculiX: FEA 求解 (系统包管理器安装 ccx)
- PyVista: 可视化 (pip install pyvista)
"""

import contextlib
from pathlib import Path

import typer
from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.rule import Rule
from rich.table import Table
from rich.text import Text

from mechforge_work.cae_core import (
    BoundaryCondition,
    CAEEngine,
    Material,
    SolutionConfig,
)

# 全局状态
console = Console()
app = typer.Typer(help="MechForge CAE Workbench - Gmsh + CalculiX")

# 当前引擎实例
current_engine: CAEEngine | None = None


# ==================== UI 组件 ====================


def print_banner():
    """打印启动横幅"""
    logo = """[cyan]███╗   ███╗███████╗ ██████╗██╗  ██╗███████╗ ██████╗ ██████╗  ██████╗ ███████╗
████╗ ████║██╔════╝██╔════╝██║  ██║██╔════╝██╔═══██╗██╔══██╗██╔════╝ ██╔════╝
██╔████╔██║█████╗  ██║     ███████║█████╗  ██║   ██║██████╔╝██║  ███╗█████╗
██║╚██╔╝██║██╔══╝  ██║     ██╔══██║██╔══╝  ██║   ██║██╔══██╗██║   ██║██╔══╝
██║ ╚═╝ ██║███████╗╚██████╗██║  ██║██║     ╚██████╔╝██║  ██║╚██████╔╝███████╗
╚═╝     ╚═╝╚══════╝ ╚═════╝╚═╝  ╚═╝╚═╝      ╚═════╝ ╚═╝  ╚═╝ ╚═════╝ ╚══════╝[/cyan]"""

    console.print()
    console.print(logo)
    console.print(
        Rule("[bold cyan]Work Mode - Gmsh + CalculiX Workbench", style="cyan"),
        style="cyan",
    )


def print_status_panel():
    """打印状态面板"""
    # 检查依赖
    deps_status = []
    try:
        import gmsh  # noqa: F401

        deps_status.append(("Gmsh", "[green]✓[/green]"))
    except ImportError:
        deps_status.append(("Gmsh", "[red]✗ pip install gmsh[/red]"))

    try:
        import subprocess

        _result = subprocess.run(["ccx", "-v"], capture_output=True, timeout=5)
        deps_status.append(("CalculiX", "[green]✓[/green]"))
    except Exception:
        deps_status.append(("CalculiX", "[red]✗ 未安装[/red]"))

    try:
        import pyvista  # noqa: F401

        deps_status.append(("PyVista", "[green]✓[/green]"))
    except ImportError:
        deps_status.append(("PyVista", "[red]✗ pip install pyvista[/red]"))

    # 当前状态
    global current_engine
    if current_engine:
        mesh_status = (
            f"[green]{current_engine.mesh.num_nodes} 节点[/green]"
            if current_engine.mesh
            else "[dim]未生成[/dim]"
        )
        solve_status = (
            "[green]已求解[/green]"
            if (current_engine.result and current_engine.result.success)
            else "[dim]未求解[/dim]"
        )
    else:
        mesh_status = "[dim]未初始化[/dim]"
        solve_status = "[dim]未初始化[/dim]"

    # 创建状态表格
    grid = Table(box=box.SIMPLE_HEAVY, padding=(0, 1), show_edge=False, border_style="dim cyan")
    grid.add_column(width=12, style="orange1")
    grid.add_column(width=25, style="spring_green3")
    grid.add_column(width=12, style="orange1")
    grid.add_column(width=25, style="spring_green3")

    grid.add_row("[bold]Gmsh", deps_status[0][1], "[bold]网格", mesh_status)
    grid.add_row("[bold]CalculiX", deps_status[1][1], "[bold]求解", solve_status)
    grid.add_row(
        "[bold]PyVista",
        deps_status[2][1],
        "[bold]工作目录",
        f"[dim]{current_engine.work_dir.name if current_engine else 'None'}[/dim]",
    )

    console.print(grid)


def print_help_panel():
    """打印帮助面板"""
    help_text = Text(
        "/status /load /demo /mesh /material /bc /solve /show /export /clear /exit",
        style="spring_green3",
    )
    console.print(Panel(help_text, border_style="dim", padding=(0, 1)))


def print_mesh_info():
    """打印网格信息"""
    global current_engine
    if not current_engine or not current_engine.mesh:
        console.print("[yellow]尚未生成网格[/yellow]")
        return

    _mesh = current_engine.mesh
    info = Table(show_header=False, box=box.ROUNDED, border_style="cyan")
    info.add_column(style="orange1", width=12)
    info.add_column(style="white")

    info.add_row("节点数", f"[cyan]{mesh.num_nodes:,}[/cyan]")
    info.add_row("单元数", f"[cyan]{mesh.num_elements:,}[/cyan]")
    info.add_row("单元类型", f"[cyan]{mesh.element_type}[/cyan]")
    info.add_row("物理组", f"[cyan]{len(mesh.node_sets)} 个[/cyan]")

    console.print(Panel(info, title="[bold cyan]网格信息[/bold cyan]", border_style="cyan"))


def print_result_info():
    """打印求解结果"""
    global current_engine
    if not current_engine or not current_engine.result:
        console.print("[yellow]尚未求解[/yellow]")
        return

    result = current_engine.result
    if not result.success:
        console.print(f"[red]求解失败: {result.message}[/red]")
        return

    info = Table(show_header=False, box=box.ROUNDED, border_style="green")
    info.add_column(style="orange1", width=15)
    info.add_column(style="white")

    info.add_row("状态", "[green]✓ 成功[/green]")
    info.add_row("最大位移", f"[cyan]{result.max_displacement:.6f} mm[/cyan]")
    info.add_row("最大应力", f"[cyan]{result.max_von_mises:.2f} MPa[/cyan]")

    console.print(Panel(info, title="[bold green]求解结果[/bold green]", border_style="green"))


# ==================== 命令处理器 ====================


def handle_status():
    """显示状态"""
    print_status_panel()
    console.print()
    print_mesh_info()
    console.print()
    print_result_info()


def handle_load(filepath: str) -> bool:
    """加载几何文件"""
    global current_engine

    path = Path(filepath)
    if not path.exists():
        console.print(f"[red]文件不存在: {filepath}[/red]")
        return False

    suffix = path.suffix.lower()
    if suffix not in [".stp", ".step", ".iges", ".igs", ".stl", ".brep"]:
        console.print(f"[red]不支持的格式: {suffix}[/red]")
        console.print("[yellow]支持: .stp .step .iges .igs .stl .brep[/yellow]")
        return False

    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            progress.add_task("加载几何...", total=None)

            if current_engine is None:
                current_engine = CAEEngine()

            current_engine.load_geometry(path)

        console.print("[green]✓ 几何加载成功[/green]")
        return True

    except Exception as e:
        console.print(f"[red]加载失败: {e}[/red]")
        return False


def handle_demo() -> bool:
    """运行悬臂梁示例"""
    global current_engine

    console.print(
        Panel(
            "[bold]悬臂梁分析示例[/bold]\n\n"
            "尺寸: 100 x 10 x 10 mm\n"
            "材料: 钢 (E=210GPa, ν=0.3)\n"
            "载荷: 1000 N (端部集中力)\n"
            "约束: 一端固定",
            title="[bold cyan]Demo[/bold cyan]",
            border_style="cyan",
        )
    )

    try:
        with Progress(console=console) as progress:
            task = progress.add_task("创建模型...", total=4)

            if current_engine is None:
                current_engine = CAEEngine()
            progress.update(task, advance=1)

            # 创建悬臂梁模型
            current_engine.setup_cantilever_beam(
                length=100.0,
                width=10.0,
                height=10.0,
                mesh_size=2.0,
                force=1000.0,
            )
            progress.update(task, advance=1)

            # 生成网格
            progress.update(task, description="生成网格...")
            current_engine.generate_mesh(mesh_size=2.0)
            progress.update(task, advance=1)

            # 求解
            progress.update(task, description="求解...")
            result = current_engine.solve()
            progress.update(task, advance=1)

        if result.success:
            console.print("[green]✓ 分析完成[/green]")
            print_result_info()

            # 理论解对比
            console.print(
                Panel(
                    "[bold]理论验证 (悬臂梁端部挠度)[/bold]\n\n"
                    "公式: δ = FL³ / (3EI)\n"
                    "理论值: ~0.0254 mm\n"
                    f"计算值: {result.max_displacement:.6f} mm",
                    border_style="dim",
                )
            )
        else:
            console.print(f"[red]求解失败: {result.message}[/red]")

        return result.success

    except Exception as e:
        console.print(f"[red]分析失败: {e}[/red]")
        return False


def handle_mesh(size: float = 5.0, mesh_type: str = "tet") -> bool:
    """生成网格"""
    global current_engine

    if current_engine is None:
        console.print("[red]请先加载几何 /load 或运行示例 /demo[/red]")
        return False

    if not current_engine.geometry_file:
        console.print("[red]未加载几何文件[/red]")
        return False

    try:
        with Progress(console=console) as progress:
            task = progress.add_task("生成网格...", total=100)

            _mesh = current_engine.generate_mesh(
                mesh_size=size,
                mesh_type=mesh_type,  # type: ignore
            )

            progress.update(task, completed=100)

        console.print("[green]✓ 网格生成完成[/green]")
        print_mesh_info()
        return True

    except ImportError:
        console.print("[red]Gmsh 未安装。请运行: pip install gmsh[/red]")
        return False
    except Exception as e:
        console.print(f"[red]网格生成失败: {e}[/red]")
        return False


def handle_material() -> bool:
    """添加材料（交互式）"""
    global current_engine

    if current_engine is None:
        console.print("[red]请先初始化模型[/red]")
        return False

    console.print(
        Panel(
            "[bold]选择材料[/bold]\n\n"
            "1. 结构钢 (E=210GPa, ν=0.3)\n"
            "2. 铝合金 (E=70GPa, ν=0.33)\n"
            "3. 钛合金 (E=116GPa, ν=0.31)\n"
            "4. 自定义",
            title="[bold cyan]材料库[/bold cyan]",
            border_style="cyan",
        )
    )

    choice = console.input("[cyan]选择 [1-4]: [/cyan]").strip()

    materials = {
        "1": Material("Steel", 210000, 0.3, 7850e-9, 250),
        "2": Material("Aluminum", 70000, 0.33, 2700e-9, 150),
        "3": Material("Titanium", 116000, 0.31, 4500e-9, 800),
    }

    if choice in materials:
        current_engine.add_material(materials[choice])
    elif choice == "4":
        name = console.input("[cyan]材料名称: [/cyan]").strip() or "Custom"
        try:
            e = float(console.input("[cyan]弹性模量 E (MPa): [/cyan]").strip() or "210000")
            nu = float(console.input("[cyan]泊松比 ν: [/cyan]").strip() or "0.3")
            current_engine.add_material(Material(name, e, nu))
        except ValueError:
            console.print("[red]输入错误[/red]")
            return False
    else:
        console.print("[red]无效选择[/red]")
        return False

    return True


def handle_bc() -> bool:
    """添加边界条件（交互式）"""
    global current_engine

    if current_engine is None:
        console.print("[red]请先初始化模型[/red]")
        return False

    console.print(
        Panel(
            "[bold]边界条件类型[/bold]\n\n"
            "1. 固定约束 (Fixed)\n"
            "2. 力载荷 (Force)\n"
            "3. 压力载荷 (Pressure)\n"
            "4. 位移约束 (Displacement)\n"
            "0. 返回",
            title="[bold cyan]边界条件[/bold cyan]",
            border_style="cyan",
        )
    )

    choice = console.input("[cyan]选择 [0-4]: [/cyan]").strip()

    if choice == "0":
        return True

    bc_types = {
        "1": ("fixed", "固定约束"),
        "2": ("force", "力载荷"),
        "3": ("pressure", "压力载荷"),
        "4": ("displacement", "位移约束"),
    }

    if choice not in bc_types:
        console.print("[red]无效选择[/red]")
        return False

    bc_type, bc_name = bc_types[choice]

    # 获取实体
    entities = (
        ["all"] + list(current_engine.mesh.node_sets.keys()) if current_engine.mesh else ["all"]
    )
    console.print(f"[dim]可用实体: {', '.join(entities)}[/dim]")
    entity = console.input("[cyan]选择实体: [/cyan]").strip() or "all"

    # 获取数值
    value = 0.0
    if bc_type in ["force", "pressure", "displacement"]:
        try:
            value = float(console.input(f"[cyan]{bc_name} 值: [/cyan]").strip() or "0")
        except ValueError:
            console.print("[red]请输入数字[/red]")
            return False

    # 方向（仅力）
    direction = None
    if bc_type == "force":
        dir_input = console.input("[cyan]方向 (x,y,z, 默认 0,0,-1): [/cyan]").strip()
        if dir_input:
            try:
                direction = [float(x) for x in dir_input.split(",")]
            except Exception:
                direction = [0, 0, -1]
        else:
            direction = [0, 0, -1]

    bc = BoundaryCondition(
        name=f"{bc_name}_{len(current_engine.boundary_conditions) + 1}",
        bc_type=bc_type,  # type: ignore
        entity=entity,
        value=value,
        direction=direction,
    )

    current_engine.add_boundary_condition(bc)
    return True


def handle_solve(analysis_type: str = "static") -> bool:
    """执行求解"""
    global current_engine

    if current_engine is None:
        console.print("[red]请先初始化模型[/red]")
        return False

    if not current_engine.mesh:
        console.print("[red]请先生成网格 /mesh[/red]")
        return False

    if not current_engine.materials:
        console.print("[yellow]警告: 未设置材料，使用默认钢[/yellow]")
        current_engine.add_material(Material("Steel", 210000, 0.3))

    if not current_engine.boundary_conditions:
        console.print("[yellow]警告: 未设置边界条件[/yellow]")

    config = SolutionConfig(analysis_type=analysis_type)  # type: ignore

    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            progress.add_task("CalculiX 求解中...", total=None)
            result = current_engine.solve(config)

        if result.success:
            console.print("[green]✓ 求解完成[/green]")
            print_result_info()
        else:
            console.print(f"[red]求解失败: {result.message}[/red]")

        return result.success

    except Exception as e:
        console.print(f"[red]求解错误: {e}[/red]")
        return False


def handle_show(result_type: str = "vonmises") -> bool:
    """可视化结果"""
    global current_engine

    if current_engine is None:
        console.print("[red]请先初始化模型[/red]")
        return False

    try:
        import pyvista  # noqa: F401
    except ImportError:
        console.print("[red]PyVista 未安装。请运行: pip install pyvista[/red]")
        return False

    try:
        console.print(f"[cyan]正在显示 {result_type}...[/cyan]")
        current_engine.visualize(result_type)  # type: ignore
        return True
    except Exception as e:
        console.print(f"[red]可视化失败: {e}[/red]")
        return False


def handle_export(fmt: str = "vtk") -> bool:
    """导出结果"""
    global current_engine

    if current_engine is None or not current_engine.result:
        console.print("[red]无结果可导出[/red]")
        return False

    filename = f"result.{fmt}"
    filepath = current_engine.work_dir / filename

    try:
        current_engine.export_results(filepath, fmt)  # type: ignore
        console.print(f"[green]✓ 已导出: {filepath}[/green]")
        return True
    except Exception as e:
        console.print(f"[red]导出失败: {e}[/red]")
        return False


def handle_clear():
    """清除状态"""
    global current_engine
    current_engine = None
    console.print("[green]✓ 状态已重置[/green]")


# ==================== 交互式 CLI ====================


def interactive_mode():
    """交互式命令模式"""
    print_banner()
    print_status_panel()
    print_help_panel()

    while True:
        try:
            user_input = console.input("[spring_green3][MechForge] >[/spring_green3] ").strip()

            if not user_input:
                continue

            if user_input.lower() in ["/exit", "/quit", "/q"]:
                console.print("\n[cyan]再见![/cyan]\n")
                break

            if user_input.lower() == "/clear":
                console.clear()
                print_banner()
                print_status_panel()
                print_help_panel()
                continue

            if user_input.lower() == "/status":
                handle_status()
                continue

            if user_input.lower() == "/help":
                print_help_panel()
                continue

            # 解析命令
            parts = user_input.split()
            cmd = parts[0].lower()
            args = parts[1:]

            if cmd == "/load":
                if not args:
                    console.print("[red]用法: /load <文件路径>[/red]")
                    continue
                handle_load(args[0])

            elif cmd == "/demo":
                handle_demo()

            elif cmd == "/mesh":
                size = 5.0
                for arg in args:
                    if arg.startswith("--size=") or arg.startswith("-s="):
                        with contextlib.suppress(Exception):
                            size = float(arg.split("=")[1])
                handle_mesh(size)

            elif cmd == "/material":
                handle_material()

            elif cmd == "/bc":
                handle_bc()

            elif cmd == "/solve":
                analysis_type = args[0] if args else "static"
                handle_solve(analysis_type)

            elif cmd == "/show":
                result_type = args[0] if args else "vonmises"
                handle_show(result_type)

            elif cmd == "/export":
                fmt = args[0] if args else "vtk"
                handle_export(fmt)

            elif cmd == "/reset":
                handle_clear()
                print_banner()
                print_status_panel()

            else:
                console.print(f"[red]未知命令: {cmd}[/red]")
                console.print("[dim]输入 /help 查看可用命令[/dim]")

        except KeyboardInterrupt:
            console.print("\n[dim]使用 /exit 退出[/dim]")
            continue
        except EOFError:
            break


# ==================== Typer CLI 命令 ====================


@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    version: bool = typer.Option(False, "--version", "-v", help="显示版本"),
):
    """MechForge CAE Workbench"""
    if version:
        console.print("[cyan]MechForge Work v0.4.0[/cyan]")
        raise typer.Exit()

    # 如果没有指定子命令，运行 demo
    if ctx.invoked_subcommand is None:
        print_banner()
        handle_demo()
        interactive_mode()


@app.command()
def load(filepath: str = typer.Argument(..., help="几何文件路径 (.stp/.iges/.stl)")):
    """加载几何文件"""
    print_banner()
    handle_load(filepath)
    interactive_mode()


@app.command()
def demo():
    """运行悬臂梁示例"""
    print_banner()
    handle_demo()
    interactive_mode()


@app.command()
def mesh(
    size: float = typer.Option(5.0, "--size", "-s", help="网格尺寸 (mm)"),
    geometry: str | None = typer.Option(None, "--geo", "-g", help="几何文件路径"),
):
    """生成网格"""
    print_banner()
    if geometry:
        handle_load(geometry)
    handle_mesh(size)


@app.command()
def solve(
    analysis_type: str = typer.Argument("static", help="分析类型 (static/modal/thermal)"),
):
    """执行求解"""
    handle_solve(analysis_type)


@app.command()
def show(
    result_type: str = typer.Argument("vonmises", help="结果类型 (vonmises/displacement/mesh)"),
):
    """可视化结果"""
    handle_show(result_type)


@app.command()
def export(
    fmt: str = typer.Argument("vtk", help="导出格式 (vtk/csv/json)"),
):
    """导出结果"""
    handle_export(fmt)


@app.command()
def cli():
    """启动交互式 CLI"""
    interactive_mode()


if __name__ == "__main__":
    app()
