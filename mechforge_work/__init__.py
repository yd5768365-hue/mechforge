"""
MechForge Work - Local CAE Workbench

Gmsh + CalculiX 本地计算工作台

说明：
- 为了在未安装 CLI 依赖（如 typer）时仍然可以使用 `mechforge_work.cae_core`
  等核心模块，这里对 CLI 导入做了安全包装。
"""

from __future__ import annotations

from typing import Any

try:
    from mechforge_work.work_cli import app
except Exception:  # noqa: BLE001
    # 在仅调用 CAE 核心时，不强制要求 CLI 相关依赖存在
    app: Any | None = None

__all__ = ["app"]
