"""
Obsidian 同步 API 路由
提供 Obsidian Vault 同步功能
"""

import logging
from pathlib import Path
from typing import Any, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from .state import state

logger = logging.getLogger("mechforge.api.obsidian")

router = APIRouter(prefix="/api/obsidian", tags=["Obsidian"])


# ── 配置获取 ──────────────────────────────────────────────────────────────────


def _get_vault_path() -> Optional[str]:
    """获取配置的 Obsidian Vault 路径"""
    try:
        if hasattr(state.config, "knowledge"):
            config = state.config.knowledge
            if hasattr(config, "obsidian_vault_path"):
                return config.obsidian_vault_path
            elif isinstance(config, dict):
                return config.get("obsidian_vault_path")
    except Exception as e:
        logger.warning(f"获取 Obsidian Vault 路径失败: {e}")
    return None


def _set_vault_path(vault_path: str) -> bool:
    """设置 Obsidian Vault 路径到配置"""
    try:
        if hasattr(state.config, "knowledge"):
            config = state.config.knowledge
            if hasattr(config, "obsidian_vault_path"):
                config.obsidian_vault_path = vault_path
                # 保存配置
                state.config.save()
                logger.info(f"Obsidian Vault 路径已设置: {vault_path}")
                return True
        return False
    except Exception as e:
        logger.error(f"设置 Obsidian Vault 路径失败: {e}")
        return False


# ── 请求模型 ──────────────────────────────────────────────────────────────────


class PullRequest(BaseModel):
    subfolder: str = Field("", description="要同步的子文件夹")


class PushRequest(BaseModel):
    content: str = Field(..., description="要写入的内容")
    title: str = Field(..., description="笔记标题")
    tags: list[str] = Field(default_factory=list, description="标签列表")
    target_folder: str = Field("MechForge", description="目标文件夹")


class ConfigRequest(BaseModel):
    vault_path: str = Field(..., description="Obsidian Vault 路径")


# ── API 端点 ─────────────────────────────────────────────────────────────────


@router.get("/status")
async def get_status() -> dict[str, Any]:
    """获取 Obsidian Vault 同步状态"""
    vault_path = _get_vault_path()

    if not vault_path:
        return {
            "configured": False,
            "vault_path": None,
            "accessible": False,
            "total_notes": 0,
            "synced_notes": 0,
            "unsynced_notes": 0,
        }

    vault = Path(vault_path)

    if not vault.exists():
        return {
            "configured": True,
            "vault_path": vault_path,
            "accessible": False,
            "total_notes": 0,
            "synced_notes": 0,
            "unsynced_notes": 0,
            "error": "Vault 路径不存在",
        }

    # 获取同步服务状态
    try:
        from .obsidian_sync import get_obsidian_service
        service = get_obsidian_service(vault_path)
        status = service.get_status()
        return {
            "configured": True,
            "vault_path": vault_path,
            **status,
        }
    except Exception as e:
        return {
            "configured": True,
            "vault_path": vault_path,
            "accessible": True,
            "total_notes": 0,
            "synced_notes": 0,
            "unsynced_notes": 0,
            "error": str(e),
        }


@router.post("/pull")
async def pull_notes(req: PullRequest) -> dict[str, Any]:
    """从 Obsidian Vault 拉取笔记到知识库"""
    vault_path = _get_vault_path()

    if not vault_path:
        raise HTTPException(status_code=400, detail="未配置 Obsidian Vault 路径")

    try:
        from .obsidian_sync import get_obsidian_service
        service = get_obsidian_service(vault_path)
        result = await service.pull(subfolder=req.subfolder)
        return result
    except Exception as e:
        logger.error(f"拉取笔记失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.post("/push")
async def push_note(req: PushRequest) -> dict[str, Any]:
    """将 AI 生成的内容推送到 Obsidian Vault"""
    vault_path = _get_vault_path()

    if not vault_path:
        raise HTTPException(status_code=400, detail="未配置 Obsidian Vault 路径")

    try:
        from .obsidian_sync import get_obsidian_service
        service = get_obsidian_service(vault_path)
        result = await service.push(
            content=req.content,
            title=req.title,
            tags=req.tags,
            target_folder=req.target_folder,
        )
        return result
    except Exception as e:
        logger.error(f"推送笔记失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.post("/config")
async def configure_vault(req: ConfigRequest) -> dict[str, Any]:
    """配置 Obsidian Vault 路径"""
    vault = Path(req.vault_path)

    if not vault.exists():
        raise HTTPException(status_code=400, detail="Vault 路径不存在")

    if not vault.is_dir():
        raise HTTPException(status_code=400, detail="Vault 路径必须是文件夹")

    # 检查是否包含 .obsidian 文件夹
    obsidian_folder = vault / ".obsidian"
    if not obsidian_folder.exists():
        # 可能是普通文件夹，不是 Obsidian Vault
        logger.warning(f"Vault 路径 {vault} 没有 .obsidian 文件夹")

    success = _set_vault_path(req.vault_path)

    if success:
        # 重置服务实例以使用新路径
        try:
            from .obsidian_sync import reset_obsidian_service
            reset_obsidian_service()
        except Exception:
            pass

        return {"success": True, "vault_path": req.vault_path}
    else:
        raise HTTPException(status_code=500, detail="保存配置失败")


@router.get("/vault_tree")
async def get_vault_tree() -> dict[str, Any]:
    """获取 Vault 文件夹结构"""
    vault_path = _get_vault_path()

    if not vault_path:
        raise HTTPException(status_code=400, detail="未配置 Obsidian Vault 路径")

    try:
        from .obsidian_sync import get_obsidian_service
        service = get_obsidian_service(vault_path)
        tree = service.get_vault_tree()
        return {"tree": tree}
    except Exception as e:
        logger.error(f"获取 Vault 树失败: {e}")
        raise HTTPException(status_code=500, detail=str(e)) from e
