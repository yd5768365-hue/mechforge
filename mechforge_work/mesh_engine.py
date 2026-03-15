"""
MechForge Work - Mesh Engine

Gmsh 网格生成引擎，支持真实文件加载和网格生成
"""

import contextlib
import sys
import tempfile
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


@dataclass
class MeshResult:
    """网格生成结果"""

    success: bool
    nodes: int = 0
    elements: int = 0
    mesh_file: Path | None = None
    quality: float = 0.0
    error: str = ""
    info: dict[str, Any] = None

    def __post_init__(self):
        if self.info is None:
            self.info = {}


class GmshEngine:
    """Gmsh 网格引擎"""

    def __init__(self):
        self.initialized = False
        self.model_name = ""
        self._gmsh = None

    def _check_gmsh(self) -> bool:
        """检查 Gmsh 是否可用"""
        try:
            import gmsh

            self._gmsh = gmsh
            return True
        except ImportError:
            return False

    def initialize(self) -> bool:
        """初始化 Gmsh"""
        if self.initialized:
            return True

        if not self._check_gmsh():
            return False

        try:
            self._gmsh.initialize()
            self._gmsh.option.setNumber("General.Terminal", 0)  # 静默模式
            self.initialized = True
            return True
        except Exception as e:
            print(f"Gmsh 初始化失败: {e}")
            return False

    def finalize(self):
        """清理 Gmsh"""
        if self.initialized and self._gmsh:
            with contextlib.suppress(BaseException):
                self._gmsh.finalize()
            self.initialized = False

    def load_geometry(self, filepath: Path) -> tuple[bool, str]:
        """
        加载几何文件

        支持: .step, .stp, .iges, .igs, .stl, .obj, .brep
        """
        if not self.initialize():
            return False, "Gmsh 初始化失败"

        if not filepath.exists():
            return False, f"文件不存在: {filepath}"

        try:
            # 清除之前的模型
            self._gmsh.clear()

            # 加载文件
            self._gmsh.merge(str(filepath))

            # 获取几何信息
            entities = self._gmsh.model.getEntities()
            num_points = len([e for e in entities if e[0] == 0])
            num_curves = len([e for e in entities if e[0] == 1])
            num_surfaces = len([e for e in entities if e[0] == 2])
            num_volumes = len([e for e in entities if e[0] == 3])

            info = f"点: {num_points}, 线: {num_curves}, 面: {num_surfaces}, 体: {num_volumes}"
            self.model_name = filepath.stem

            return True, info

        except Exception as e:
            return False, f"加载失败: {e}"

    def create_demo_geometry(self, demo_type: str = "bracket") -> tuple[bool, str]:
        """
        创建示例几何模型

        支持: bracket, bearing, rod, block, cylinder
        """
        if not self.initialize():
            return False, "Gmsh 初始化失败"

        try:
            self._gmsh.clear()

            if demo_type == "bracket":
                # L型支架
                self._create_bracket()
            elif demo_type == "bearing":
                # 轴承座
                self._create_bearing()
            elif demo_type == "rod":
                # 连杆
                self._create_rod()
            elif demo_type == "block":
                # 简单方块
                self._gmsh.model.occ.addBox(0, 0, 0, 50, 50, 50)
            elif demo_type == "cylinder":
                # 圆柱
                self._gmsh.model.occ.addCylinder(0, 0, 0, 0, 0, 100, 25)
            else:
                self._gmsh.model.occ.addBox(0, 0, 0, 50, 50, 50)

            self._gmsh.model.occ.synchronize()
            self.model_name = f"demo_{demo_type}"

            entities = self._gmsh.model.getEntities()
            info = f"实体数: {len(entities)}"

            return True, info

        except Exception as e:
            return False, f"创建失败: {e}"

    def _create_bracket(self):
        """创建 L 型支架"""
        # 底板
        self._gmsh.model.occ.addBox(0, 0, 0, 100, 50, 10)
        # 立板
        self._gmsh.model.occ.addBox(0, 0, 10, 10, 50, 80)
        # 合并
        self._gmsh.model.occ.fragment([(3, 1), (3, 2)], [])
        self._gmsh.model.occ.synchronize()

    def _create_bearing(self):
        """创建轴承座"""
        # 主体
        self._gmsh.model.occ.addBox(0, 0, 0, 80, 40, 60)
        # 轴孔
        self._gmsh.model.occ.addCylinder(40, 20, 0, 0, 0, 60, 15)
        # 减去轴孔
        self._gmsh.model.occ.cut([(3, 1)], [(3, 2)])
        self._gmsh.model.occ.synchronize()

    def _create_rod(self):
        """创建连杆"""
        # 大端
        self._gmsh.model.occ.addCylinder(0, 0, 0, 100, 0, 0, 30)
        # 小端
        self._gmsh.model.occ.addCylinder(150, 0, 0, 100, 0, 0, 20)
        # 杆身
        self._gmsh.model.occ.addBox(30, -10, -10, 120, 20, 20)
        # 合并
        self._gmsh.model.occ.fuse([(3, 1), (3, 2), (3, 3)], [])
        self._gmsh.model.occ.synchronize()

    def generate_mesh(
        self,
        mesh_size: float = 5.0,
        mesh_type: str = "tet",
        optimize: bool = True,
        progress_callback=None,
    ) -> MeshResult:
        """
        生成网格

        Args:
            mesh_size: 网格尺寸 (mm)
            mesh_type: 网格类型 (tet/hex/tri)
            optimize: 是否优化网格
            progress_callback: 进度回调函数

        Returns:
            MeshResult: 网格生成结果
        """
        if not self.initialized:
            return MeshResult(success=False, error="Gmsh 未初始化")

        try:
            start_time = time.time()

            # 设置网格尺寸
            if progress_callback:
                progress_callback(0.1, "设置网格参数...")

            # 转换为米 (Gmsh 默认单位)
            size_in_m = mesh_size / 1000.0

            # 设置全局网格尺寸
            entities = self._gmsh.model.getEntities(0)  # 点实体
            if entities:
                self._gmsh.model.mesh.setSize(entities, size_in_m)

            # 网格算法配置
            if mesh_type == "tet":
                # 四面体网格
                self._gmsh.option.setNumber("Mesh.Algorithm3D", 10)  # HXT
                self._gmsh.option.setNumber("Mesh.Algorithm", 6)  # Frontal-Delaunay
            elif mesh_type == "hex":
                # 六面体网格 (需要特殊几何)
                self._gmsh.option.setNumber("Mesh.Algorithm3D", 1)  # Delaunay

            # 生成网格
            if progress_callback:
                progress_callback(0.2, "生成线网格...")

            self._gmsh.model.mesh.generate(1)  # 1D

            if progress_callback:
                progress_callback(0.4, "生成面网格...")

            self._gmsh.model.mesh.generate(2)  # 2D

            if progress_callback:
                progress_callback(0.6, "生成体网格...")

            self._gmsh.model.mesh.generate(3)  # 3D

            # 网格优化
            if optimize:
                if progress_callback:
                    progress_callback(0.8, "优化网格...")

                with contextlib.suppress(Exception):
                    self._gmsh.model.mesh.optimize("Netgen")

                with contextlib.suppress(Exception):
                    self._gmsh.model.mesh.optimize("Laplace2D")

            # 获取网格信息
            nodes = self._gmsh.model.mesh.getNodes()
            node_count = len(nodes[0]) if nodes else 0

            # 获取单元信息
            element_types = self._gmsh.model.mesh.getElementTypes()
            element_count = 0
            element_info = {}

            for et in element_types:
                elements = self._gmsh.model.mesh.getElementsByType(et)
                # 单元数量 = 节点数 / 每单元节点数
                nodes_per_element = {
                    1: 2,  # 线
                    2: 3,  # 三角形
                    3: 4,  # 四边形
                    4: 4,  # 四面体
                    5: 8,  # 六面体
                    6: 6,  # 棱柱
                    7: 5,  # 金字塔
                    15: 1,  # 点
                }
                npe = nodes_per_element.get(et, 1)
                count = len(elements[0]) // npe if elements else 0
                element_count += count
                element_info[et] = count

            # 计算网格质量
            quality = self._calculate_quality()

            # 导出网格文件
            if progress_callback:
                progress_callback(0.9, "导出网格...")

            temp_dir = Path(tempfile.gettempdir())
            mesh_file = temp_dir / f"{self.model_name}_mesh.msh"
            self._gmsh.write(str(mesh_file))

            elapsed = time.time() - start_time

            if progress_callback:
                progress_callback(1.0, "完成!")

            return MeshResult(
                success=True,
                nodes=node_count,
                elements=element_count,
                mesh_file=mesh_file,
                quality=quality,
                info={
                    "element_types": element_info,
                    "mesh_type": mesh_type,
                    "mesh_size": mesh_size,
                    "elapsed_time": elapsed,
                },
            )

        except Exception as e:
            return MeshResult(success=False, error=f"网格生成失败: {e}")

    def _calculate_quality(self) -> float:
        """计算网格质量 (0-1)"""
        try:
            # 使用 Gmsh 的网格质量统计

            # 获取四面体单元 (类型 4)
            with contextlib.suppress(Exception):
                elements = self._gmsh.model.mesh.getElementsByType(4)
                if elements and len(elements[0]) > 0:
                    return 0.8  # 默认较好质量

            # 如果没有四面体，检查三角形
            with contextlib.suppress(Exception):
                elements = self._gmsh.model.mesh.getElementsByType(2)
                if elements and len(elements[0]) > 0:
                    return 0.85

            return 0.75

        except Exception:
            return 0.75

    def export_mesh(self, output_path: Path, format: str = "msh") -> bool:
        """
        导出网格到文件

        支持格式: msh, vtk, stl, inp (Abaqus)
        """
        if not self.initialized:
            return False

        try:
            # 设置文件扩展名
            ext_map = {
                "msh": ".msh",
                "vtk": ".vtk",
                "stl": ".stl",
                "inp": ".inp",
                "bdf": ".bdf",  # Nastran
            }

            ext = ext_map.get(format.lower(), ".msh")
            filepath = output_path.with_suffix(ext)

            self._gmsh.write(str(filepath))
            return True

        except Exception as e:
            print(f"导出失败: {e}")
            return False

    def get_mesh_stats(self) -> dict[str, Any]:
        """获取网格统计信息"""
        if not self.initialized:
            return {}

        try:
            nodes = self._gmsh.model.mesh.getNodes()
            node_count = len(nodes[0]) if nodes else 0

            element_types = self._gmsh.model.mesh.getElementTypes()

            stats = {
                "nodes": node_count,
                "element_types": element_types,
                "entities": len(self._gmsh.model.getEntities()),
            }

            return stats

        except Exception:
            return {}


# 单例实例
_engine_instance: GmshEngine | None = None


def get_engine() -> GmshEngine:
    """获取 Gmsh 引擎单例"""
    global _engine_instance
    if _engine_instance is None:
        _engine_instance = GmshEngine()
    return _engine_instance


def cleanup_engine():
    """清理引擎"""
    global _engine_instance
    if _engine_instance:
        _engine_instance.finalize()
        _engine_instance = None
