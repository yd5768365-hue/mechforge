"""
CAE 工作台 API 路由

提供与 `mechforge_work` 的 CAEEngine 的桥接：  # cspell:ignore-line
- 依赖与状态检查
- 内置悬臂梁 Demo（含理论值对比）
"""

from __future__ import annotations

import logging
from typing import Any, Literal

from fastapi import APIRouter
from pydantic import BaseModel, Field

from mechforge_work.cae_core import CAEEngine, SolutionResult

logger = logging.getLogger("mechforge.api.cae")

router = APIRouter(prefix="/api/cae", tags=["CAE"])


class DependencyStatus(BaseModel):
    """单个依赖的状态信息"""

    ok: bool = Field(..., description="依赖是否可用")
    message: str = Field(..., description="人类可读的说明/修复建议")


class CAEStatusResponse(BaseModel):
    """CAE 引擎整体状态"""

    dependencies: dict[str, DependencyStatus]
    geometry_loaded: bool
    mesh_generated: bool
    num_materials: int
    num_boundary_conditions: int
    solved: bool
    work_dir: str


class DemoResultResponse(BaseModel):
    """悬臂梁 Demo 结果（带理论值对比）"""

    success: bool
    status: Literal["ok", "warn", "error"] = Field(
        "error", description="整体评估：ok=与理论值一致，warn=偏差略大，error=失败"
    )
    message: str = ""
    max_displacement: float | None = Field(
        default=None, description="计算得到的最大位移 (mm)"
    )
    max_von_mises: float | None = Field(
        default=None, description="计算得到的最大 von Mises 应力 (MPa)"
    )
    theoretical_displacement: float = Field(
        default=0.0254, description="理论端部挠度 (mm)，基于 δ = FL³/(3EI)"
    )
    displacement_error: float | None = Field(
        default=None, description="绝对误差 |数值-理论| (mm)"
    )
    error_ratio: float | None = Field(
        default=None, description="相对误差 |数值-理论|/理论，单位 1"
    )
    num_nodes: int | None = Field(
        default=None, description="网格节点数（仅在依赖完整且求解成功时提供）"
    )
    num_elements: int | None = Field(
        default=None, description="网格单元数（仅在依赖完整且求解成功时提供）"
    )
    dependencies: dict[str, bool] = Field(
        default_factory=dict, description="依赖可用性快照"
    )


def _build_dependency_status(raw: dict[str, bool]) -> dict[str, DependencyStatus]:
    """将 CAEEngine 返回的依赖状态转换为带说明的结构"""

    messages: dict[str, str] = {
        "gmsh": "几何与网格模块。未安装时无法生成网格，请运行: pip install gmsh",
        "calculix": (
            "CalculiX (ccx) 求解器。未安装时无法进行真实 FEA 求解，"
            "可从 https://www.calculixforwin.com/ 或发行版仓库安装。"
        ),
        "pyvista": "结果可视化模块。未安装时无法进行 3D 可视化，请运行: pip install pyvista",
    }

    return {
        name: DependencyStatus(
            ok=ok,
            message=("就绪" if ok else messages.get(name, "未就绪，请检查安装")),
        )
        for name, ok in raw.items()
    }


@router.get("/status", response_model=CAEStatusResponse)
async def get_cae_status() -> CAEStatusResponse:
    """获取 CAE 引擎当前状态与依赖情况"""
    engine = CAEEngine()
    raw_status = engine.get_status()

    deps_raw = raw_status.get("dependencies", {})
    deps = _build_dependency_status(deps_raw)

    return CAEStatusResponse(
        dependencies=deps,
        geometry_loaded=bool(raw_status.get("geometry_loaded")),
        mesh_generated=bool(raw_status.get("mesh_generated")),
        num_materials=int(raw_status.get("num_materials", 0)),
        num_boundary_conditions=int(raw_status.get("num_boundary_conditions", 0)),
        solved=bool(raw_status.get("solved")),
        work_dir=str(raw_status.get("work_dir", "")),
    )


def _evaluate_result(result: SolutionResult, theoretical_disp: float) -> dict[str, Any]:
    """根据求解结果与理论值给出评估"""
    if not result.success:
        return {
            "status": "error",
            "message": result.message or "求解失败",
            "max_displacement": None,
            "max_von_mises": None,
            "displacement_error": None,
            "error_ratio": None,
        }

    max_disp = result.max_displacement
    max_vm = result.max_von_mises

    if max_disp <= 0:
        return {
            "status": "error",
            "message": "未能从 CalculiX 结果中解析出有效位移",
            "max_displacement": max_disp,
            "max_von_mises": max_vm,
            "displacement_error": None,
            "error_ratio": None,
        }

    error_abs = abs(max_disp - theoretical_disp)
    error_ratio = error_abs / theoretical_disp if theoretical_disp > 0 else None

    # 经验阈值：<10% 认为 ok，10%~30% 为 warn，>30% 认为误差较大
    if error_ratio is None:
        status: Literal["ok", "warn", "error"] = "warn"
        msg = "无法计算相对误差，但求解完成"
    elif error_ratio <= 0.1:
        status = "ok"
        msg = "数值结果与经典梁理论高度一致"
    elif error_ratio <= 0.3:
        status = "warn"
        msg = "数值结果与经典梁理论存在一定偏差，可用于趋势判断"
    else:
        status = "warn"
        msg = "数值结果与经典梁理论偏差较大，请检查网格密度与边界条件"

    return {
        "status": status,
        "message": msg,
        "max_displacement": max_disp,
        "max_von_mises": max_vm,
        "displacement_error": error_abs,
        "error_ratio": error_ratio,
    }


@router.post("/demo", response_model=DemoResultResponse)
async def run_cantilever_demo() -> DemoResultResponse:
    """
    运行内置悬臂梁 Demo：
    - 梁长 100mm，截面 10x10mm
    - 端部集中力 1000N
    - 钢材 E=210GPa, ν=0.3

    返回：
    - CalculiX 数值结果
    - 经典梁理论端部挠度 0.0254 mm
    - 误差与评估结论
    """
    engine = CAEEngine()
    deps = engine._check_dependencies()  # 使用内部检查，方便前端显示细节

    # 如果关键依赖缺失，直接返回错误提示，不尝试求解
    if not deps.get("gmsh", False) or not deps.get("calculix", False):
        missing = [name for name, ok in deps.items() if not ok]
        msg = (
            "缺少 CAE 关键依赖: " + ", ".join(missing)
            + "。请先安装后再运行 Demo。"
        )
        logger.warning("CAE demo skipped due to missing deps: %s", missing)
        return DemoResultResponse(
            success=False,
            status="error",
            message=msg,
            theoretical_displacement=0.0254,
            dependencies=deps,
        )

    # 理论值（与 README 示例保持一致）
    theoretical_disp = 0.0254

    try:
        # 搭建悬臂梁模型 + 网格 + 求解（与 CLI demo 保持一致的参数）
        engine.setup_cantilever_beam(
            length=100.0,
            width=10.0,
            height=10.0,
            mesh_size=2.0,
            force=1000.0,
        )
        engine.generate_mesh(mesh_size=2.0)
        result = engine.solve()
    except Exception as e:  # noqa: BLE001
        logger.error("CAE demo failed: %s", e)
        return DemoResultResponse(
            success=False,
            status="error",
            message=f"CAE Demo 运行失败: {e}",
            theoretical_displacement=theoretical_disp,
            dependencies=deps,
        )

    eval_data = _evaluate_result(result, theoretical_disp)

    return DemoResultResponse(
        success=result.success,
        status=eval_data["status"],
        message=eval_data["message"],
        max_displacement=eval_data["max_displacement"],
        max_von_mises=eval_data["max_von_mises"],
        theoretical_displacement=theoretical_disp,
        displacement_error=eval_data["displacement_error"],
        error_ratio=eval_data["error_ratio"],
        num_nodes=engine.mesh.num_nodes if engine.mesh is not None else None,
        num_elements=engine.mesh.num_elements if engine.mesh is not None else None,
        dependencies=deps,
    )

