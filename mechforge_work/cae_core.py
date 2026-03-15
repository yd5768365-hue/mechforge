"""
MechForge CAE Core - 轻量级 CAE 引擎

基于最优技术栈：
- Gmsh: 几何 + 网格
- CalculiX: FEA 求解
- PyVista: 可视化

设计原则：简单、轻量、工业级
"""

import re
import subprocess
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Literal

import numpy as np

# ==================== 数据类 ====================


@dataclass
class MeshData:
    """网格数据"""

    nodes: np.ndarray = field(default_factory=lambda: np.array([]))
    elements: np.ndarray = field(default_factory=lambda: np.array([]))
    element_type: str = "tet4"  # tet4, tet10, hex8, hex20
    node_sets: dict[str, np.ndarray] = field(default_factory=dict)
    element_sets: dict[str, np.ndarray] = field(default_factory=dict)

    @property
    def num_nodes(self) -> int:
        return len(self.nodes)

    @property
    def num_elements(self) -> int:
        return len(self.elements)


@dataclass
class BoundaryCondition:
    """边界条件"""

    name: str
    bc_type: Literal["fixed", "displacement", "force", "pressure", "symmetry"]
    entity: str  # 几何实体名称或节点集
    value: float | list[float] = 0.0
    direction: list[float] | None = None  # 力的方向向量


@dataclass
class Material:
    """材料属性"""

    name: str
    youngs_modulus: float  # MPa
    poisson_ratio: float
    density: float = 7850e-9  # kg/mm³ (默认钢)
    yield_strength: float | None = None  # MPa


@dataclass
class SolutionConfig:
    """求解配置"""

    analysis_type: Literal["static", "modal", "thermal"] = "static"
    num_modes: int = 6  # 模态分析模态数
    time_steps: int = 1  # 静态分析步数


@dataclass
class SolutionResult:
    """求解结果"""

    success: bool
    message: str = ""
    displacement: np.ndarray | None = None  # (num_nodes, 3)
    stress: np.ndarray | None = None  # (num_nodes, 6) - Sxx, Syy, Szz, Sxy, Syz, Szx
    von_mises: np.ndarray | None = None  # (num_nodes,)
    frequencies: np.ndarray | None = None  # 模态频率 (Hz)
    max_displacement: float = 0.0
    max_von_mises: float = 0.0


# ==================== CAE 引擎 ====================


class CAEEngine:
    """
    轻量级 CAE 引擎

    完整工作流：几何 → 网格 → 边界条件 → 求解 → 后处理
    """

    def __init__(self, work_dir: Path | None = None):
        self.work_dir = Path(work_dir) if work_dir else Path(tempfile.mkdtemp(prefix="mechforge_"))
        self.work_dir.mkdir(parents=True, exist_ok=True)

        # 当前状态
        self.geometry_file: Path | None = None
        self.mesh: MeshData | None = None
        self.materials: dict[str, Material] = {}
        self.boundary_conditions: list[BoundaryCondition] = []
        self.solution_config = SolutionConfig()
        self.result: SolutionResult | None = None

        # 内部状态
        self._gmsh_initialized = False
        self._model_name = "mechforge_model"

        # 检查依赖
        self._check_dependencies()

    def _check_dependencies(self) -> dict[str, bool]:
        """检查依赖是否安装"""
        deps = {"gmsh": False, "calculix": False, "pyvista": False}

        try:
            import gmsh  # noqa: F401

            deps["gmsh"] = True
        except ImportError:
            pass

        try:
            result = subprocess.run(["ccx", "-v"], capture_output=True, text=True, timeout=5)
            deps["calculix"] = result.returncode == 0
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pass

        try:
            import pyvista  # noqa: F401

            deps["pyvista"] = True
        except ImportError:
            pass

        return deps

    def load_geometry(self, filepath: str | Path) -> bool:
        """
        加载几何文件

        支持格式：STEP (.stp, .step), IGES (.igs, .iges), STL (.stl)
        """
        filepath = Path(filepath)
        if not filepath.exists():
            raise FileNotFoundError(f"几何文件不存在: {filepath}")

        suffix = filepath.suffix.lower()
        if suffix not in [".stp", ".step", ".iges", ".igs", ".stl", ".brep"]:
            raise ValueError(f"不支持的几何格式: {suffix}")

        self.geometry_file = filepath
        print(f"✓ 几何已加载: {filepath.name}")
        return True

    def generate_mesh(
        self,
        mesh_size: float = 5.0,
        mesh_type: Literal["tet", "hex", "auto"] = "tet",
        order: int = 1,
    ) -> MeshData:
        """
        生成网格

        Args:
            mesh_size: 网格尺寸 (mm)
            mesh_type: 网格类型 (tet-四面体, hex-六面体, auto-自动)
            order: 单元阶数 (1-线性, 2-二次)
        """
        try:
            import gmsh  # noqa: F401
        except ImportError as e:
            raise ImportError("Gmsh 未安装。请运行: pip install gmsh") from e

        if not self.geometry_file:
            raise RuntimeError("请先加载几何文件")

        # 初始化 Gmsh
        gmsh.initialize()
        gmsh.model.add(self._model_name)
        gmsh.option.setNumber("General.Terminal", 0)  # 静默模式

        # 加载几何
        gmsh.open(str(self.geometry_file))

        # 设置网格参数
        gmsh.option.setNumber("Mesh.CharacteristicLengthMin", mesh_size * 0.5)
        gmsh.option.setNumber("Mesh.CharacteristicLengthMax", mesh_size)
        gmsh.option.setNumber("Mesh.ElementOrder", order)
        gmsh.option.setNumber("Mesh.Optimize", 1)
        gmsh.option.setNumber("Mesh.OptimizeNetgen", 1)

        # 生成网格
        if mesh_type == "hex":
            # 尝试六面体网格（需要可划分几何）
            gmsh.option.setNumber("Mesh.Algorithm3D", 9)  # HXT (六面体)
        else:
            gmsh.option.setNumber("Mesh.Algorithm3D", 1)  # Delaunay (四面体)

        gmsh.model.mesh.generate(3)

        # 提取网格数据
        mesh = self._extract_mesh(gmsh)

        # 保存网格文件
        mesh_file = self.work_dir / f"{self._model_name}.inp"
        gmsh.write(str(mesh_file))

        gmsh.finalize()

        self.mesh = mesh
        print(f"✓ 网格生成完成: {mesh.num_nodes} 节点, {mesh.num_elements} 单元")
        return mesh

    def _extract_mesh(self, gmsh) -> MeshData:
        """从 Gmsh 提取网格数据"""
        mesh = MeshData()

        # 获取节点
        node_tags, node_coords, _ = gmsh.model.mesh.getNodes()
        mesh.nodes = node_coords.reshape(-1, 3) * 1000  # 转换为 mm

        # 获取单元 (3D 实体单元)
        element_types = [4, 5, 11, 17]  # tet4, tet10, hex8, hex20
        element_names = {4: "tet4", 5: "tet10", 11: "hex8", 17: "hex20"}

        all_elements = []
        for elem_type in element_types:
            try:
                tags, node_tags_elem = gmsh.model.mesh.getElementsByType(elem_type)
                if len(tags) > 0:
                    # 获取每个单元的节点数
                    _, _, _, num_nodes, _ = gmsh.model.mesh.getElementProperties(elem_type)
                    elements = node_tags_elem.reshape(-1, num_nodes)
                    all_elements.append(elements)
                    mesh.element_type = element_names.get(elem_type, "unknown")
            except Exception:
                continue

        if all_elements:
            mesh.elements = np.vstack(all_elements)

        # 获取物理组（用于边界条件）
        physical_groups = gmsh.model.getPhysicalGroups()
        for dim, tag in physical_groups:
            name = gmsh.model.getPhysicalName(dim, tag)
            entities = gmsh.model.getEntitiesForPhysicalGroup(dim, tag)

            # 获取这些实体的节点
            nodes = []
            for entity in entities:
                _, node_tags, _ = gmsh.model.mesh.getNodes(dimTags=[(dim, entity)])
                nodes.extend(node_tags)

            mesh.node_sets[name] = np.unique(nodes)

        return mesh

    def add_material(self, material: Material) -> None:
        """添加材料"""
        self.materials[material.name] = material
        print(f"✓ 材料已添加: {material.name}")

    def add_boundary_condition(self, bc: BoundaryCondition) -> None:
        """添加边界条件"""
        self.boundary_conditions.append(bc)
        print(f"✓ 边界条件已添加: {bc.name} ({bc.bc_type})")

    def setup_cantilever_beam(
        self,
        length: float = 100.0,
        width: float = 10.0,
        height: float = 10.0,
        mesh_size: float = 2.0,
        force: float = 1000.0,  # N
        material: Material | None = None,
    ) -> bool:
        """
        快速设置悬臂梁分析（内置几何生成）

        用于演示和测试，无需外部几何文件
        """
        try:
            import gmsh  # noqa: F401
        except ImportError as e:
            raise ImportError("Gmsh 未安装") from e

        # 创建长方体几何
        gmsh.initialize()
        gmsh.model.add("cantilever_beam")
        gmsh.option.setNumber("General.Terminal", 0)

        # 创建长方体 (x: 0~length, y: 0~width, z: 0~height)
        box = gmsh.model.occ.addBox(0, 0, 0, length, width, height)
        gmsh.model.occ.synchronize()

        # 添加物理组（边界条件用）
        # 固定端 (x=0 的面)
        fixed_surface = gmsh.model.occ.getEntitiesInBoundingBox(
            -0.1, -0.1, -0.1, 0.1, width + 0.1, height + 0.1, dim=2
        )
        if fixed_surface:
            gmsh.model.addPhysicalGroup(2, [s[1] for s in fixed_surface], tag=1)
            gmsh.model.setPhysicalName(2, 1, "fixed_end")

        # 加载端 (x=length 的面)
        load_surface = gmsh.model.occ.getEntitiesInBoundingBox(
            length - 0.1, -0.1, -0.1, length + 0.1, width + 0.1, height + 0.1, dim=2
        )
        if load_surface:
            gmsh.model.addPhysicalGroup(2, [s[1] for s in load_surface], tag=2)
            gmsh.model.setPhysicalName(2, 2, "load_end")

        # 体积（整个梁）
        gmsh.model.addPhysicalGroup(3, [box], tag=3)
        gmsh.model.setPhysicalName(3, 3, "beam_volume")

        gmsh.model.occ.synchronize()

        # 生成网格
        gmsh.option.setNumber("Mesh.CharacteristicLengthMin", mesh_size * 0.5)
        gmsh.option.setNumber("Mesh.CharacteristicLengthMax", mesh_size)
        gmsh.model.mesh.generate(3)

        # 保存几何和网格
        geo_file = self.work_dir / "cantilever.step"
        mesh_file = self.work_dir / "cantilever.inp"
        gmsh.write(str(geo_file))
        gmsh.write(str(mesh_file))

        # 提取网格
        self.mesh = self._extract_mesh(gmsh)

        gmsh.finalize()

        self.geometry_file = geo_file

        # 设置材料
        if material is None:
            material = Material(
                name="Steel",
                youngs_modulus=210000,  # MPa
                poisson_ratio=0.3,
                density=7850e-9,
            )
        self.add_material(material)

        # 设置边界条件
        self.add_boundary_condition(
            BoundaryCondition(
                name="Fixed Support",
                bc_type="fixed",
                entity="fixed_end",
            )
        )

        self.add_boundary_condition(
            BoundaryCondition(
                name="Point Load",
                bc_type="force",
                entity="load_end",
                value=force,
                direction=[0, 0, -1],  # 向下
            )
        )

        print(f"✓ 悬臂梁模型已创建: {length}x{width}x{height} mm, 力={force} N")
        return True

    def solve(self, config: SolutionConfig | None = None) -> SolutionResult:
        """
        执行 FEA 求解（CalculiX）
        """
        if config:
            self.solution_config = config

        if not self.mesh:
            raise RuntimeError("请先生成网格")

        # 检查 CalculiX
        try:
            result = subprocess.run(["ccx", "-v"], capture_output=True, text=True, timeout=5)
            if result.returncode != 0:
                raise FileNotFoundError()
        except FileNotFoundError:
            return SolutionResult(
                success=False,
                message="CalculiX (ccx) 未安装。请从 https://www.calculixforwin.com/ 下载安装",
            )

        # 生成 CalculiX 输入文件
        _inp_file = self._generate_ccx_input()

        # 运行求解
        try:
            result = subprocess.run(
                ["ccx", self._model_name],
                cwd=self.work_dir,
                capture_output=True,
                text=True,
                timeout=300,  # 5分钟超时
            )

            if result.returncode != 0:
                return SolutionResult(
                    success=False,
                    message=f"求解失败:\n{result.stderr}",
                )

            # 解析结果
            self.result = self._parse_results()
            return self.result

        except subprocess.TimeoutExpired:
            return SolutionResult(success=False, message="求解超时（超过5分钟）")
        except Exception as e:
            return SolutionResult(success=False, message=f"求解错误: {e}")

    def _generate_ccx_input(self) -> Path:
        """生成 CalculiX 输入文件 (.inp)"""
        _inp_file = self.work_dir / f"{self._model_name}.inp"

        lines = []
        lines.append("** MechForge CAE Analysis")
        lines.append(f"** Model: {self._model_name}")
        lines.append("")

        # 包含网格文件
        mesh_file = self.work_dir / f"{self._model_name}.inp"
        if mesh_file.exists():
            lines.append(f"*INCLUDE, INPUT={mesh_file.name}")
            lines.append("")

        # 材料定义
        for name, mat in self.materials.items():
            lines.append(f"*MATERIAL, NAME={name}")
            lines.append("*ELASTIC")
            lines.append(f"{mat.youngs_modulus}, {mat.poisson_ratio}")
            lines.append("*DENSITY")
            lines.append(f"{mat.density}")
            lines.append("")

        # 截面属性
        lines.append(
            f"*SOLID SECTION, ELSET=beam_volume, MATERIAL={list(self.materials.keys())[0]}"
        )
        lines.append("")

        # 分析步
        if self.solution_config.analysis_type == "static":
            lines.append("*STEP")
            lines.append("*STATIC")
            lines.append("1., 1., 1e-5, 1.")
        elif self.solution_config.analysis_type == "modal":
            lines.append("*STEP")
            lines.append("*FREQUENCY")
            lines.append(f"{self.solution_config.num_modes}")

        # 边界条件
        for bc in self.boundary_conditions:
            if bc.bc_type == "fixed":
                lines.append("*BOUNDARY")
                lines.append(f"{bc.entity}, 1, 3, 0")  # 固定 xyz
            elif bc.bc_type == "force":
                lines.append("*CLOAD")
                direction = bc.direction or [0, 0, 1]
                for i, comp in enumerate(direction, 1):
                    if comp != 0:
                        lines.append(f"{bc.entity}, {i}, {bc.value * comp}")

        # 输出请求
        lines.append("*NODE PRINT, NSET=Nall")
        lines.append("U")
        lines.append("*EL PRINT, ELSET=Eall")
        lines.append("S")
        lines.append("*NODE FILE")
        lines.append("U")
        lines.append("*EL FILE")
        lines.append("S, E")
        lines.append("*END STEP")

        # 写入文件
        _inp_file.write_text("\n".join(lines), encoding="utf-8")
        return _inp_file

    def _parse_results(self) -> SolutionResult:
        """解析 CalculiX 结果文件 (.frd)"""
        frd_file = self.work_dir / f"{self._model_name}.frd"
        dat_file = self.work_dir / f"{self._model_name}.dat"

        result = SolutionResult(success=True, message="求解完成")

        # 解析 .dat 文件获取数值结果
        if dat_file.exists():
            text = dat_file.read_text()

            # 提取最大位移
            disp_match = re.search(r"maximum absolute values\s+\n.*?\n\s*(\S+)", text, re.DOTALL)
            if disp_match:
                result.max_displacement = float(disp_match.group(1))

            # 提取最大应力
            stress_match = re.search(r"maximum von Mises stress.*?\n\s*(\S+)", text, re.DOTALL)
            if stress_match:
                result.max_von_mises = float(stress_match.group(1))

        # 解析 .frd 文件（二进制/文本）
        if frd_file.exists():
            try:
                result.displacement, result.stress, result.von_mises = self._parse_frd(frd_file)
            except Exception as e:
                print(f"警告: 结果解析部分失败: {e}")

        return result

    def _parse_frd(self, frd_file: Path) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        """解析 FRD 结果文件"""
        # 简化的 FRD 解析（文本格式）
        lines = frd_file.read_text().split("\n")

        displacements = []
        reading_disp = False

        for line in lines:
            if "DISP" in line:
                reading_disp = True
                continue
            if reading_disp and line.startswith(" -1"):
                # 数据行: -1 node_id x y z
                parts = line.split()
                if len(parts) >= 5:
                    displacements.append([float(parts[2]), float(parts[3]), float(parts[4])])
            elif reading_disp and line.startswith(" -3"):
                break

        disp_array = np.array(displacements) if displacements else np.array([])

        # 简化的应力解析（实际需要更复杂的解析）
        stress_array = np.array([])
        vm_array = np.array([])

        return disp_array, stress_array, vm_array

    def visualize(
        self, result_type: Literal["mesh", "displacement", "stress", "vonmises"] = "vonmises"
    ):
        """
        可视化结果（PyVista）
        """
        try:
            import pyvista as pv  # noqa: F401
        except ImportError as e:
            raise ImportError("PyVista 未安装。请运行: pip install pyvista") from e

        if not self.mesh:
            raise RuntimeError("请先生成网格")

        # 创建 PyVista 网格
        if self.mesh.element_type.startswith("tet"):
            cell_type = pv.CellType.TETRA
        elif self.mesh.element_type.startswith("hex"):
            cell_type = pv.CellType.HEXAHEDRON
        else:
            cell_type = pv.CellType.TETRA

        # 构建单元连接
        cells = []
        for elem in self.mesh.elements:
            cells.append(len(elem))
            cells.extend(elem - 1)  # 转换为 0-based

        grid = pv.UnstructuredGrid(
            np.array(cells), [cell_type] * len(self.mesh.elements), self.mesh.nodes
        )

        # 添加结果数据
        if result_type == "displacement" and self.result and self.result.displacement is not None:
            if len(self.result.displacement) == len(self.mesh.nodes):
                grid["Displacement"] = np.linalg.norm(self.result.displacement, axis=1)
                grid["Displacement_Vector"] = self.result.displacement

        elif (
            result_type == "vonmises"
            and self.result
            and self.result.von_mises is not None
            and len(self.result.von_mises) == len(self.mesh.nodes)
        ):
            grid["von_Mises"] = self.result.von_mises

        # 创建绘图器
        plotter = pv.Plotter()

        if result_type == "mesh":
            plotter.add_mesh(grid, show_edges=True, color="lightblue")
        elif "Displacement" in grid.array_names:
            plotter.add_mesh(grid, scalars="Displacement", show_edges=True, cmap="jet")
            plotter.add_scalar_bar(title="位移 (mm)")
        elif "von_Mises" in grid.array_names:
            plotter.add_mesh(grid, scalars="von_Mises", show_edges=True, cmap="jet")
            plotter.add_scalar_bar(title="von Mises 应力 (MPa)")
        else:
            plotter.add_mesh(grid, show_edges=True, color="lightblue")

        plotter.add_axes()
        plotter.add_title(f"MechForge - {result_type}")

        print(f"✓ 正在显示 {result_type}...")
        plotter.show()

        return grid

    def export_results(self, filepath: str | Path, format: Literal["vtk", "csv", "json"] = "vtk"):
        """
        导出结果
        """
        filepath = Path(filepath)

        if format == "vtk":
            # 使用 PyVista 导出 VTK
            grid = self.visualize("vonmises")
            grid.save(str(filepath))
            print(f"✓ 结果已导出: {filepath}")

        elif format == "csv":
            # 导出节点数据 CSV
            import pandas as pd

            data = {
                "Node": range(len(self.mesh.nodes)),
                "X": self.mesh.nodes[:, 0],
                "Y": self.mesh.nodes[:, 1],
                "Z": self.mesh.nodes[:, 2],
            }

            if self.result and self.result.displacement is not None:
                data["Disp_X"] = self.result.displacement[:, 0]
                data["Disp_Y"] = self.result.displacement[:, 1]
                data["Disp_Z"] = self.result.displacement[:, 2]
                data["Disp_Mag"] = np.linalg.norm(self.result.displacement, axis=1)

            df = pd.DataFrame(data)
            df.to_csv(filepath, index=False)
            print(f"✓ 结果已导出: {filepath}")

        elif format == "json":
            import json

            data = {
                "model": self._model_name,
                "mesh": {"nodes": self.mesh.num_nodes, "elements": self.mesh.num_elements},
                "result": {},
            }

            if self.result:
                data["result"] = {
                    "max_displacement": self.result.max_displacement,
                    "max_von_mises": self.result.max_von_mises,
                }

            with open(filepath, "w") as f:
                json.dump(data, f, indent=2)
            print(f"✓ 结果已导出: {filepath}")

    def get_status(self) -> dict[str, Any]:
        """获取当前状态"""
        deps = self._check_dependencies()

        return {
            "dependencies": deps,
            "geometry_loaded": self.geometry_file is not None,
            "mesh_generated": self.mesh is not None,
            "num_materials": len(self.materials),
            "num_boundary_conditions": len(self.boundary_conditions),
            "solved": self.result is not None and self.result.success,
            "work_dir": str(self.work_dir),
        }
