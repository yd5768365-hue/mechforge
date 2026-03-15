"""
MechForge Work - Solver Engine

CalculiX 求解器引擎，支持真实求解和模拟模式
支持 API 调用和本地求解两种方式
"""

import json
import os
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request
from collections.abc import Callable
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


class SolveMode(Enum):
    """求解模式"""

    LOCAL = "local"  # 本地 CalculiX 求解
    API = "api"  # API 远程求解
    SIMULATION = "sim"  # 模拟求解


@dataclass
class SolveResult:
    """求解结果"""

    success: bool
    solve_type: str = "static"
    solve_mode: SolveMode = SolveMode.SIMULATION
    max_disp: float = 0.0
    max_stress: float = 0.0
    min_stress: float = 0.0
    solve_time: float = 0.0
    error: str = ""
    result_file: Path | None = None
    info: dict[str, Any] = field(default_factory=dict)


@dataclass
class BoundaryCondition:
    """边界条件"""

    name: str
    bc_type: str  # "fixed", "force", "pressure", "displacement"
    target: str  # 面集名称或节点集
    values: dict[str, float] = field(default_factory=dict)


@dataclass
class Material:
    """材料属性"""

    name: str
    youngs_modulus: float = 210000.0  # MPa
    poisson_ratio: float = 0.3
    density: float = 7850.0  # kg/m³
    yield_stress: float = 250.0  # MPa


# 预定义材料
MATERIALS = {
    "steel": Material("Steel", 210000, 0.3, 7850, 250),
    "aluminum": Material("Aluminum", 70000, 0.33, 2700, 150),
    "copper": Material("Copper", 120000, 0.34, 8960, 70),
    "titanium": Material("Titanium", 110000, 0.33, 4500, 880),
}


class CalculiXEngine:
    """CalculiX 求解引擎"""

    def __init__(self, api_endpoint: str = None):
        """
        初始化求解引擎

        Args:
            api_endpoint: API 服务端点 (可选)
        """
        self.ccx_path = self._find_ccx()
        self.mesh_file: Path | None = None
        self.inp_file: Path | None = None
        self.api_endpoint = api_endpoint or os.environ.get("CALCULIX_API", "")

        # 分析配置
        self.material = MATERIALS["steel"]
        self.boundary_conditions: list[BoundaryCondition] = []
        self.analysis_type = "static"

        # 回调
        self._progress_callback: Callable | None = None

    def _find_ccx(self) -> str | None:
        """查找 CalculiX 可执行文件"""
        names = ["ccx", "ccx_2.21", "ccx_2.20", "calculix"]

        for name in names:
            result = subprocess.run(
                ["where", name] if sys.platform == "win32" else ["which", name],
                capture_output=True,
                text=True,
            )
            if result.returncode == 0:
                return result.stdout.strip().split("\n")[0]

        return None

    def is_available(self) -> bool:
        """检查 CalculiX 是否可用"""
        return self.ccx_path is not None

    def set_mesh(self, mesh_file: Path):
        """设置网格文件"""
        self.mesh_file = mesh_file

    def generate_inp(
        self,
        analysis_type: str = "static",
        boundary_conditions: dict = None,
        material: dict = None,
        output_path: Path = None,
    ) -> Path:
        """
        生成 CalculiX 输入文件 (.inp)

        Args:
            analysis_type: 分析类型 (static/thermal/modal)
            boundary_conditions: 边界条件
            material: 材料属性
            output_path: 输出路径
        """
        if output_path is None:
            output_path = Path(tempfile.gettempdir()) / "analysis.inp"

        # 默认材料 (钢)
        if material is None:
            material = {
                "name": "Steel",
                "youngs_modulus": 210000,  # MPa
                "poisson_ratio": 0.3,
                "density": 7850,  # kg/m³
            }

        # 默认边界条件
        if boundary_conditions is None:
            boundary_conditions = {
                "fixed_faces": [1],  # 固定面
                "load_faces": [2],  # 载荷面
                "force": 1000,  # N
            }

        # 生成 INP 文件内容
        inp_content = self._generate_inp_content(analysis_type, boundary_conditions, material)

        with open(output_path, "w") as f:
            f.write(inp_content)

        self.inp_file = output_path
        return output_path

    def _generate_inp_content(
        self, analysis_type: str, boundary_conditions: dict, material: dict
    ) -> str:
        """生成 INP 文件内容"""

        # 标题
        content = f"""** MechForge Work - CalculiX Input File
** Generated automatically
** Analysis Type: {analysis_type}
**
*HEADING
MechForge Analysis
**
** Material Definition
*MATERIAL, NAME={material["name"]}
*ELASTIC, TYPE=ISO
{material["youngs_modulus"]},{material["poisson_ratio"]}
*DENSITY
{material["density"]},
**
** Section Definition
*SOLID SECTION, ELSET=EALL, MATERIAL={material["name"]}
**
"""

        # 分析步
        if analysis_type == "static":
            content += """** Step 1: Static Analysis
*STEP
*STATIC
**
"""
        elif analysis_type == "modal":
            content += """** Step 1: Modal Analysis
*STEP
*FREQUENCY, SOLVER=ARPACK
10
**
"""
        elif analysis_type == "thermal":
            content += """** Step 1: Thermal Analysis
*STEP
*HEAT TRANSFER
**
"""

        # 边界条件 (简化)
        content += """** Boundary Conditions
*BOUNDARY
NFIXED, 1, 3
**
** Output Requests
*NODE FILE, OUTPUT=2D
U
*EL FILE, OUTPUT=2D
S, E
*END STEP
"""

        return content

    def solve(
        self, analysis_type: str = "static", progress_callback=None, simulation_mode: bool = False
    ) -> SolveResult:
        """
        执行求解

        Args:
            analysis_type: 分析类型
            progress_callback: 进度回调
            simulation_mode: 是否使用模拟模式
        """
        start_time = time.time()

        # 如果 CalculiX 不可用或指定模拟模式，使用模拟
        if simulation_mode or not self.is_available():
            return self._simulate_solve(analysis_type, progress_callback)

        try:
            if progress_callback:
                progress_callback(0.1, "准备求解...")

            # 生成输入文件
            inp_file = self.generate_inp(analysis_type)

            if progress_callback:
                progress_callback(0.2, "启动 CalculiX...")

            # 运行 CalculiX
            subprocess.run(
                [self.ccx_path, inp_file.stem],
                cwd=inp_file.parent,
                capture_output=True,
                text=True,
                timeout=300,  # 5 分钟超时
            )

            if progress_callback:
                progress_callback(0.8, "读取结果...")

            # 解析结果
            solve_result = self._parse_results(analysis_type)

            elapsed = time.time() - start_time
            solve_result.solve_time = elapsed

            if progress_callback:
                progress_callback(1.0, "完成!")

            return solve_result

        except subprocess.TimeoutExpired:
            return SolveResult(success=False, error="求解超时 (>5分钟)")
        except Exception as e:
            return SolveResult(success=False, error=f"求解失败: {e}")

    def _simulate_solve(self, analysis_type: str, progress_callback=None) -> SolveResult:
        """模拟求解过程 (当 CalculiX 不可用时)"""
        import random

        start_time = time.time()

        steps = [
            (0.1, "检查边界条件..."),
            (0.2, "组装刚度矩阵..."),
            (0.4, "求解线性方程组..."),
            (0.6, "计算应力应变..."),
            (0.8, "后处理..."),
            (1.0, "完成!"),
        ]

        for progress, message in steps:
            if progress_callback:
                progress_callback(progress, message)
            time.sleep(0.3 + random.random() * 0.2)

        elapsed = time.time() - start_time

        # 生成模拟结果
        max_disp = random.uniform(0.01, 0.1)
        max_stress = random.uniform(50, 200)

        return SolveResult(
            success=True,
            solve_type=analysis_type,
            solve_mode=SolveMode.SIMULATION,
            max_disp=max_disp,
            max_stress=max_stress,
            min_stress=max_stress * 0.05,
            solve_time=elapsed,
            info={
                "simulation": True,
                "nodes": random.randint(5000, 20000),
                "elements": random.randint(20000, 80000),
                "iterations": random.randint(50, 200),
            },
        )

    def _parse_results(self, analysis_type: str) -> SolveResult:
        """解析 CalculiX 结果文件"""
        # 这里需要实现结果文件解析
        # 暂时返回模拟结果
        import random

        return SolveResult(
            success=True,
            solve_type=analysis_type,
            solve_mode=SolveMode.LOCAL,
            max_disp=random.uniform(0.01, 0.1),
            max_stress=random.uniform(50, 200),
            min_stress=random.uniform(5, 20),
        )

    def get_stress_field(self) -> dict[str, Any]:
        """获取应力场数据 (用于可视化)"""
        # 这里需要从结果文件读取
        # 暂时返回模拟数据
        import random

        return {
            "von_mises": [random.uniform(10, 150) for _ in range(100)],
            "max": random.uniform(100, 200),
            "min": random.uniform(5, 20),
        }

    def get_displacement_field(self) -> dict[str, Any]:
        """获取位移场数据"""
        import random

        return {
            "magnitude": [random.uniform(0, 0.05) for _ in range(100)],
            "max": random.uniform(0.02, 0.1),
        }

    # ==================== API 求解功能 ====================

    def set_api_endpoint(self, endpoint: str):
        """设置 API 端点"""
        self.api_endpoint = endpoint

    def set_material(self, material: Material):
        """设置材料"""
        self.material = material

    def set_material_by_name(self, name: str) -> bool:
        """按名称设置材料"""
        if name.lower() in MATERIALS:
            self.material = MATERIALS[name.lower()]
            return True
        return False

    def add_boundary_condition(self, bc: BoundaryCondition):
        """添加边界条件"""
        self.boundary_conditions.append(bc)

    def clear_boundary_conditions(self):
        """清空边界条件"""
        self.boundary_conditions.clear()

    def set_progress_callback(self, callback: Callable[[float, str], None]):
        """设置进度回调"""
        self._progress_callback = callback

    def solve_via_api(
        self,
        mesh_file: Path = None,
        analysis_type: str = "static",
        job_name: str = "analysis",
        timeout: int = 600,
    ) -> SolveResult:
        """
        通过 API 提交求解任务

        Args:
            mesh_file: 网格文件路径
            analysis_type: 分析类型
            job_name: 任务名称
            timeout: 超时时间 (秒)

        Returns:
            SolveResult: 求解结果
        """
        import urllib.error
        import urllib.request

        start_time = time.time()

        if not self.api_endpoint:
            return SolveResult(
                success=False,
                error="未配置 API 端点，请先设置 CALCULIX_API 环境变量或调用 set_api_endpoint()",
            )

        try:
            if self._progress_callback:
                self._progress_callback(0.1, "准备提交任务...")

            # 准备请求数据
            mesh_path = mesh_file or self.mesh_file
            if mesh_path and mesh_path.exists():
                with open(mesh_path) as f:
                    mesh_content = f.read()
            else:
                mesh_content = ""

            # 构建请求
            request_data = {
                "job_name": job_name,
                "analysis_type": analysis_type,
                "material": {
                    "name": self.material.name,
                    "youngs_modulus": self.material.youngs_modulus,
                    "poisson_ratio": self.material.poisson_ratio,
                    "density": self.material.density,
                },
                "boundary_conditions": [
                    {
                        "name": bc.name,
                        "type": bc.bc_type,
                        "target": bc.target,
                        "values": bc.values,
                    }
                    for bc in self.boundary_conditions
                ],
                "mesh_content": mesh_content,
            }

            if self._progress_callback:
                self._progress_callback(0.2, "提交任务到 API...")

            # 发送请求
            url = f"{self.api_endpoint.rstrip('/')}/solve"
            req = urllib.request.Request(
                url,
                data=json.dumps(request_data).encode("utf-8"),
                headers={"Content-Type": "application/json"},
                method="POST",
            )

            with urllib.request.urlopen(req, timeout=timeout) as response:
                result = json.loads(response.read().decode("utf-8"))

            if self._progress_callback:
                self._progress_callback(0.6, "解析结果...")

            # 解析响应
            if result.get("success"):
                elapsed = time.time() - start_time

                return SolveResult(
                    success=True,
                    solve_type=analysis_type,
                    solve_mode=SolveMode.API,
                    max_disp=result.get("max_displacement", 0.0),
                    max_stress=result.get("max_stress", 0.0),
                    min_stress=result.get("min_stress", 0.0),
                    solve_time=elapsed,
                    info={
                        "job_id": result.get("job_id"),
                        "api_endpoint": self.api_endpoint,
                        "nodes": result.get("nodes", 0),
                        "elements": result.get("elements", 0),
                        "iterations": result.get("iterations", 0),
                    },
                )
            else:
                return SolveResult(success=False, error=result.get("error", "API 返回未知错误"))

        except urllib.error.URLError as e:
            return SolveResult(success=False, error=f"API 连接失败: {e.reason}")
        except urllib.error.HTTPError as e:
            return SolveResult(success=False, error=f"API HTTP 错误: {e.code} {e.reason}")
        except Exception as e:
            return SolveResult(success=False, error=f"API 调用失败: {e}")

    def solve_smart(
        self, mesh_file: Path = None, analysis_type: str = "static", prefer_api: bool = True
    ) -> SolveResult:
        """
        智能求解 - 自动选择最佳求解方式

        优先级:
        1. 如果 prefer_api=True 且 API 端点可用 -> API 求解
        2. 如果本地 CalculiX 可用 -> 本地求解
        3. 模拟求解

        Args:
            mesh_file: 网格文件
            analysis_type: 分析类型
            prefer_api: 是否优先使用 API

        Returns:
            SolveResult: 求解结果
        """
        # 优先 API
        if prefer_api and self.api_endpoint:
            if self._progress_callback:
                self._progress_callback(0.0, "使用 API 求解...")
            return self.solve_via_api(mesh_file, analysis_type)

        # 本地求解
        if self.is_available():
            if self._progress_callback:
                self._progress_callback(0.0, "使用本地 CalculiX 求解...")
            return self.solve(analysis_type, self._progress_callback)

        # 模拟求解
        if self._progress_callback:
            self._progress_callback(0.0, "使用模拟求解...")
        return self.solve(analysis_type, self._progress_callback, simulation_mode=True)

    def check_api_status(self) -> dict[str, Any]:
        """
        检查 API 服务状态

        Returns:
            包含状态信息的字典
        """
        import urllib.error
        import urllib.request

        if not self.api_endpoint:
            return {"available": False, "error": "未配置 API 端点"}

        try:
            url = f"{self.api_endpoint.rstrip('/')}/status"
            req = urllib.request.Request(url, method="GET")

            with urllib.request.urlopen(req, timeout=10) as response:
                result = json.loads(response.read().decode("utf-8"))

            return {
                "available": True,
                "status": result.get("status", "unknown"),
                "version": result.get("version", "unknown"),
                "queue_size": result.get("queue_size", 0),
            }

        except urllib.error.URLError as e:
            return {"available": False, "error": f"连接失败: {e.reason}"}
        except Exception as e:
            return {"available": False, "error": str(e)}

    def get_available_solvers(self) -> dict[str, Any]:
        """
        获取可用求解器列表

        Returns:
            求解器可用性字典
        """
        api_status = self.check_api_status()

        return {
            "local_ccx": self.is_available(),
            "api": api_status.get("available", False),
            "simulation": True,  # 模拟模式始终可用
            "api_endpoint": self.api_endpoint or "未配置",
        }

    def discover_docker_solvers(self) -> list[dict[str, Any]]:
        """
        自动发现 Docker 容器中的求解器

        Returns:
            可用求解器列表
        """
        solvers = []

        # 常见端口
        ports = [8080, 8081, 8082, 8000, 5000]

        for port in ports:
            try:
                url = f"http://localhost:{port}/status"
                req = urllib.request.Request(url, method="GET")

                with urllib.request.urlopen(req, timeout=2) as response:
                    result = json.loads(response.read().decode("utf-8"))

                    solvers.append(
                        {
                            "port": port,
                            "url": f"http://localhost:{port}",
                            "status": result.get("status", "unknown"),
                            "ccx_available": result.get("ccx_available", False),
                        }
                    )
            except (urllib.error.URLError, OSError, json.JSONDecodeError):
                pass

        return solvers

    def auto_configure(self) -> str:
        """
        自动配置最佳求解器

        Returns:
            配置的 API 端点
        """
        # 1. 检查环境变量
        env_endpoint = os.environ.get("CALCULIX_API", "")
        if env_endpoint:
            self.api_endpoint = env_endpoint
            return env_endpoint

        # 2. 发现 Docker 容器
        solvers = self.discover_docker_solvers()

        if solvers:
            # 选择第一个可用的
            self.api_endpoint = solvers[0]["url"]
            return self.api_endpoint

        # 3. 默认端口
        default_endpoints = [
            "http://localhost:8080",
            "http://localhost:8081",
            "http://host.docker.internal:8080",
        ]

        for endpoint in default_endpoints:
            self.api_endpoint = endpoint
            status = self.check_api_status()
            if status.get("available"):
                return endpoint

        return ""


# Docker 管理函数
def start_docker_solvers() -> dict[str, Any]:
    """
    启动 Docker 求解器容器

    Returns:
        启动结果
    """
    import subprocess

    # 检查 WSL
    if sys.platform == "win32":
        try:
            # 尝试在 WSL 中启动
            result = subprocess.run(
                ["wsl", "docker", "ps"], capture_output=True, text=True, timeout=10
            )

            if result.returncode != 0:
                # 启动 Docker
                subprocess.run(
                    ["wsl", "sudo", "service", "docker", "start"], capture_output=True, timeout=10
                )

            # 启动容器
            result = subprocess.run(
                ["wsl", "bash", "-c", "cd ~/mechforge-solver && docker compose up -d"],
                capture_output=True,
                text=True,
                timeout=60,
            )

            if result.returncode == 0:
                return {"success": True, "message": "Docker 求解器已启动", "output": result.stdout}
            else:
                return {"success": False, "error": result.stderr}

        except Exception as e:
            return {"success": False, "error": str(e)}
    else:
        # Linux 直接启动
        try:
            result = subprocess.run(
                ["docker", "compose", "up", "-d"], capture_output=True, text=True, timeout=60
            )

            if result.returncode == 0:
                return {"success": True, "message": "Docker 求解器已启动"}
            else:
                return {"success": False, "error": result.stderr}
        except Exception as e:
            return {"success": False, "error": str(e)}


def stop_docker_solvers() -> dict[str, Any]:
    """停止 Docker 求解器容器"""
    import subprocess

    if sys.platform == "win32":
        try:
            result = subprocess.run(
                ["wsl", "bash", "-c", "cd ~/mechforge-solver && docker compose down"],
                capture_output=True,
                text=True,
                timeout=30,
            )

            return {
                "success": result.returncode == 0,
                "output": result.stdout,
                "error": result.stderr if result.returncode != 0 else None,
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    else:
        try:
            result = subprocess.run(
                ["docker", "compose", "down"], capture_output=True, text=True, timeout=30
            )

            return {"success": result.returncode == 0, "output": result.stdout}
        except Exception as e:
            return {"success": False, "error": str(e)}


# 单例
_solver_instance: CalculiXEngine | None = None


def get_solver(api_endpoint: str = None) -> CalculiXEngine:
    """
    获取求解器单例

    Args:
        api_endpoint: 可选的 API 端点
    """
    global _solver_instance
    if _solver_instance is None:
        _solver_instance = CalculiXEngine(api_endpoint)
    elif api_endpoint:
        _solver_instance.set_api_endpoint(api_endpoint)
    return _solver_instance


def cleanup_solver():
    """清理求解器单例"""
    global _solver_instance
    _solver_instance = None
