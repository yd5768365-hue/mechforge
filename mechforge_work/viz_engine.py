"""
MechForge Work - Visualization Engine

PyVista 可视化引擎，支持交互式 3D 结果查看
"""

import contextlib
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


@dataclass
class VisualizationResult:
    """可视化结果"""

    success: bool
    screenshot_path: Path | None = None
    error: str = ""


class PyVistaEngine:
    """PyVista 可视化引擎"""

    def __init__(self):
        self._pv = None
        self._mesh = None
        self._plotter = None

    def _check_pyvista(self) -> bool:
        """检查 PyVista 是否可用"""
        try:
            import pyvista

            self._pv = pyvista
            return True
        except ImportError:
            return False

    def is_available(self) -> bool:
        """检查可视化引擎是否可用"""
        return self._check_pyvista()

    def load_mesh(self, mesh_file: Path) -> bool:
        """加载网格文件"""
        if not self._check_pyvista():
            return False

        if not mesh_file.exists():
            return False

        try:
            self._mesh = self._pv.read(str(mesh_file))
            return True
        except Exception as e:
            print(f"加载网格失败: {e}")
            return False

    def create_mesh_from_gmsh(self, gmsh_engine) -> bool:
        """从 Gmsh 引擎创建 PyVista 网格"""
        if not self._check_pyvista():
            return False

        try:
            import gmsh

            # 导出到临时文件
            temp_dir = Path(tempfile.gettempdir())
            mesh_file = temp_dir / "temp_mesh.vtk"
            gmsh.write(str(mesh_file))

            # 加载到 PyVista
            self._mesh = self._pv.read(str(mesh_file))
            return True

        except Exception as e:
            print(f"创建网格失败: {e}")
            return False

    def show_mesh(
        self,
        show_edges: bool = True,
        color: str = "lightblue",
        background: str = "white",
        window_size: tuple = (1024, 768),
        off_screen: bool = False,
    ) -> VisualizationResult:
        """
        显示网格

        Args:
            show_edges: 显示边
            color: 网格颜色
            background: 背景颜色
            window_size: 窗口大小
            off_screen: 离屏渲染模式
        """
        if self._mesh is None:
            return VisualizationResult(success=False, error="未加载网格")

        try:
            # 创建 plotter
            self._plotter = self._pv.Plotter(window_size=window_size, off_screen=off_screen)

            self._plotter.set_background(background)
            self._plotter.add_mesh(self._mesh, show_edges=show_edges, color=color)

            # 添加坐标轴
            self._plotter.add_axes()

            # 显示
            if not off_screen:
                self._plotter.show()

            return VisualizationResult(success=True)

        except Exception as e:
            return VisualizationResult(success=False, error=str(e))

    def show_stress_result(
        self,
        stress_values: list = None,
        cmap: str = "jet",
        scalar_name: str = "Von Mises Stress (MPa)",
        window_size: tuple = (1280, 800),
    ) -> VisualizationResult:
        """
        显示应力结果云图

        Args:
            stress_values: 应力值列表
            cmap: 色图
            scalar_name: 标量名称
            window_size: 窗口大小
        """
        if self._mesh is None:
            return VisualizationResult(success=False, error="未加载网格")

        try:
            import numpy as np

            self._plotter = self._pv.Plotter(window_size=window_size)
            self._plotter.set_background("white")

            # 如果没有提供应力值，使用模拟数据
            if stress_values is None:
                n_points = self._mesh.n_points
                import random

                stress_values = [random.uniform(10, 150) for _ in range(n_points)]

            # 添加应力数据到网格
            self._mesh[scalar_name] = np.array(stress_values)

            # 添加带颜色映射的网格
            self._plotter.add_mesh(
                self._mesh,
                scalars=scalar_name,
                cmap=cmap,
                show_edges=False,
                scalar_bar_args={"title": scalar_name, "vertical": True, "position_y": 0.1},
            )

            # 添加坐标轴和标题
            self._plotter.add_axes()
            self._plotter.add_title("Stress Analysis Result")

            # 显示
            self._plotter.show()

            return VisualizationResult(success=True)

        except Exception as e:
            return VisualizationResult(success=False, error=str(e))

    def show_displacement_result(
        self,
        displacement_values: list = None,
        warp_factor: float = 10.0,
        window_size: tuple = (1280, 800),
    ) -> VisualizationResult:
        """
        显示位移结果

        Args:
            displacement_values: 位移值列表
            warp_factor: 变形放大因子
            window_size: 窗口大小
        """
        if self._mesh is None:
            return VisualizationResult(success=False, error="未加载网格")

        try:
            import numpy as np

            self._plotter = self._pv.Plotter(window_size=window_size)
            self._plotter.set_background("white")

            # 模拟位移场
            if displacement_values is None:
                n_points = self._mesh.n_points
                import random

                # 简化的位移向量
                displacement_values = np.array(
                    [[random.uniform(-0.01, 0.01) for _ in range(3)] for _ in range(n_points)]
                )

            # 创建变形网格
            warped = (
                self._mesh.warp_by_vector("displacement", factor=warp_factor)
                if "displacement" in self._mesh.array_names
                else self._mesh
            )

            # 显示原始和变形网格
            self._plotter.add_mesh(
                self._mesh, color="lightgray", style="wireframe", label="Original"
            )
            self._plotter.add_mesh(
                warped, color="red", style="surface", opacity=0.7, label="Deformed"
            )

            self._plotter.add_axes()
            self._plotter.add_legend()
            self._plotter.show()

            return VisualizationResult(success=True)

        except Exception as e:
            return VisualizationResult(success=False, error=str(e))

    def save_screenshot(self, output_path: Path) -> bool:
        """保存截图"""
        if self._plotter is None:
            return False

        try:
            self._plotter.screenshot(str(output_path))
            return True
        except Exception:
            return False

    def close(self):
        """关闭 plotter"""
        if self._plotter:
            with contextlib.suppress(BaseException):
                self._plotter.close()
            self._plotter = None


class ASCIIViewer:
    """ASCII 终端可视化 (当 PyVista 不可用时)"""

    @staticmethod
    def render_stress_cloud(max_stress: float, min_stress: float) -> str:
        """渲染 ASCII 应力云图"""
        return f"""
    ┌─────────────────────────────────────┐
    │  [dim]·····[/][cyan]▓▓▓▓[green]████████[yellow]█████████[red]███[dim]····[/]  │
    │ [dim]····[/][cyan]▓▓▓▓▓[green]██████████[yellow]███████████[red]████[cyan]▓[dim]···[/] │
    │[dim]···[/][cyan]▓▓▓[green]█████████████[yellow]█████████████[red]█████[dim]··[/]│
    │ [dim]··[/][cyan]▓▓[green]███████████████[yellow]███████████████[red]███[cyan]▓[dim]···[/] │
    │  [green]██████████████████[yellow]██████████████████[red]███[dim]····[/]  │
    │   [green]███████████████████[yellow]████████████████████[red]██[dim]····[/]   │
    │    [cyan]▓▓[green]███████████████████[yellow]█████████████████[red]██[cyan]▓[dim]·····[/]    │
    └─────────────────────────────────────┘

    [red]最大: {max_stress:.1f} MPa[/]    [blue]最小: {min_stress:.1f} MPa[/]
    [dim]─────────────────────────────────[/dim]
    [dim]低 ─────────────────────────── 高[/dim]
"""

    @staticmethod
    def render_mesh_info(nodes: int, elements: int, quality: float) -> str:
        """渲染网格信息"""
        q_bar = int(quality * 20)
        bar = "█" * q_bar + "░" * (20 - q_bar)

        return f"""
    ┌─────────────────────────────────────┐
    │         [bold cyan]网格统计信息[/]          │
    ├─────────────────────────────────────┤
    │  节点数: {nodes:>12,}              │
    │  单元数: {elements:>12,}              │
    │  质量:   [{bar}] {quality:.0%}   │
    └─────────────────────────────────────┘
"""

    @staticmethod
    def render_displacement(max_disp: float, direction: str = "Z") -> str:
        """渲染位移结果"""
        # 简化的变形图
        return f"""
    ┌─────────────────────────────────────┐
    │         [bold green]位移结果[/]               │
    ├─────────────────────────────────────┤
    │                                     │
    │    原始形状    →    变形形状         │
    │    ┌─────┐         ╱─────╲          │
    │    │     │        ╱       ╲         │
    │    │     │       ╱         ╲        │
    │    └─────┘      └───────────┘        │
    │                                     │
    │  最大位移 ({direction}): {max_disp:.4f} mm       │
    └─────────────────────────────────────┘
"""


# 便捷函数
def visualize_result(
    mesh_file: Path = None, result_type: str = "stress", use_pyvista: bool = True
) -> VisualizationResult:
    """
    可视化结果

    Args:
        mesh_file: 网格文件路径
        result_type: 结果类型 (stress/displacement/mesh)
        use_pyvista: 是否尝试使用 PyVista
    """
    if use_pyvista:
        engine = PyVistaEngine()
        if engine.is_available():
            if mesh_file and mesh_file.exists():
                engine.load_mesh(mesh_file)

            if result_type == "stress":
                return engine.show_stress_result()
            elif result_type == "displacement":
                return engine.show_displacement_result()
            else:
                return engine.show_mesh()

    # PyVista 不可用时返回提示
    return VisualizationResult(success=False, error="PyVista 不可用，请使用 ASCII 模式")


# 单例
_viz_instance: PyVistaEngine | None = None


def get_visualizer() -> PyVistaEngine:
    """获取可视化引擎单例"""
    global _viz_instance
    if _viz_instance is None:
        _viz_instance = PyVistaEngine()
    return _viz_instance
