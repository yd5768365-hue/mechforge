"""
GGUF 模型管理 API 路由
"""

import logging
import os
from pathlib import Path
from typing import Any

import requests
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from .state import state

logger = logging.getLogger("mechforge.api.gguf")

router = APIRouter(prefix="/api/gguf", tags=["GGUF"])

# ── 配置 ──────────────────────────────────────────────────────────────────────

GGUF_SERVER_URL = os.getenv("GGUF_SERVER_URL", "http://127.0.0.1:11435")


# ── 数据模型 ──────────────────────────────────────────────────────────────────


class GGUFLoadRequest(BaseModel):
    """GGUF 加载请求"""

    model_path: str = Field(..., description="模型文件路径")


# ── API 端点 ──────────────────────────────────────────────────────────────────


@router.post("/start")
async def start_gguf_server(body: dict[str, Any]) -> dict:
    """启动 GGUF 模型服务器"""
    model_name = body.get("model_name", "")

    if not model_name:
        raise HTTPException(status_code=400, detail="model_name is required")

    try:
        from mechforge_core.local_model_manager import LocalModelManager

        manager = LocalModelManager()

        success = manager.start_gguf_server(model_name)
        if success:
            return {"success": True, "message": f"GGUF server started: {model_name}"}
        else:
            raise HTTPException(status_code=500, detail="Failed to start GGUF server")
    except Exception as e:
        logger.error(f"启动 GGUF 服务器失败: {e}")
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.post("/stop")
async def stop_gguf_server() -> dict:
    """停止 GGUF 模型服务器"""
    try:
        from mechforge_core.local_model_manager import LocalModelManager

        manager = LocalModelManager()
        success = manager.stop_gguf_server()
        return {
            "success": success,
            "message": "GGUF server stopped" if success else "No server to stop",
        }
    except Exception as e:
        logger.error(f"停止 GGUF 服务器失败: {e}")
        return {"success": False, "message": str(e)}


@router.get("/status")
async def get_gguf_status() -> dict:
    """获取 GGUF 服务器状态"""
    try:
        resp = requests.get(f"{GGUF_SERVER_URL}/health", timeout=2)
        if resp.status_code == 200:
            data = resp.json()
            return {
                "running": True,
                "model": data.get("model"),
                "status": data.get("status"),
            }
    except Exception:
        pass

    return {"running": False, "model": None, "status": "stopped"}


@router.post("/load")
async def load_gguf_model(body: dict[str, Any]) -> dict:
    """加载本地 GGUF 模型文件（使用 llama-cpp-python）"""
    model_path = body.get("model_path", "")

    if not model_path:
        raise HTTPException(status_code=400, detail="model_path is required")

    # 验证文件是否存在
    model_file = Path(model_path)
    if not model_file.exists():
        raise HTTPException(status_code=404, detail=f"Model file not found: {model_path}")

    try:
        # 尝试导入 llama_cpp
        from llama_cpp import Llama

        # 如果已有模型，先卸载
        if state.gguf_llm is not None:
            del state.gguf_llm
            state.gguf_llm = None

        # 加载模型
        logger.info(f"Loading GGUF model from: {model_path}")
        state.gguf_llm = Llama(
            model_path=model_path,
            n_ctx=2048,  # 可根据需要调整
            n_threads=4,  # CPU 线程数
            verbose=False,
        )
        state.gguf_model_path = model_path

        model_name = model_file.name
        logger.info(f"GGUF model loaded successfully: {model_name}")

        return {
            "success": True,
            "model": model_name,
            "model_path": str(model_path),
            "message": f"Model {model_name} loaded successfully",
        }

    except ImportError as e:
        raise HTTPException(
            status_code=500,
            detail="llama-cpp-python not installed. Run: pip install llama-cpp-python",
        ) from e
    except Exception as e:
        logger.error(f"Failed to load GGUF model: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to load model: {str(e)}") from e


@router.post("/unload")
async def unload_gguf_model() -> dict:
    """卸载当前加载的 GGUF 模型"""
    if state.gguf_llm is not None:
        del state.gguf_llm
        state.gguf_llm = None
        state.gguf_model_path = None
        logger.info("GGUF model unloaded")
        return {"success": True, "message": "Model unloaded"}
    return {"success": True, "message": "No model to unload"}


@router.get("/info")
async def get_gguf_info() -> dict:
    """获取当前加载的 GGUF 模型信息"""
    if state.gguf_llm is None:
        return {
            "loaded": False,
            "model": None,
            "model_path": None,
        }

    return {
        "loaded": True,
        "model": Path(state.gguf_model_path).name if state.gguf_model_path else None,
        "model_path": state.gguf_model_path,
    }


@router.get("/bundled/status")
async def bundled_model_status() -> dict:
    """检查内置模型状态（是否已下载、是否已加载）"""
    from .model_downloader import (
        BUNDLED_MODEL,
        download_state,
        get_bundled_model_path,
        is_bundled_model_ready,
    )

    ready = is_bundled_model_ready()
    loaded = (
        state.gguf_llm is not None
        and state.gguf_model_path == str(get_bundled_model_path())
    )
    return {
        "model_name": BUNDLED_MODEL["name"],
        "model_description": BUNDLED_MODEL["description"],
        "size_mb": round(BUNDLED_MODEL["size_bytes"] / 1024 / 1024),
        "ready": ready,
        "loaded": loaded,
        "download": download_state.to_dict(),
    }


@router.post("/bundled/download")
async def download_bundled_model() -> dict:
    """开始下载内置模型"""
    from .model_downloader import (
        auto_load_bundled_model,
        is_bundled_model_ready,
        start_download,
    )

    if is_bundled_model_ready():
        loaded = auto_load_bundled_model()
        return {"success": True, "message": "模型已存在", "already_ready": True, "loaded": loaded}

    def _on_complete(model_path):
        try:
            auto_load_bundled_model()
        except Exception as e:
            logger.error(f"下载完成后自动加载失败: {e}")

    started = start_download(on_complete=_on_complete)
    if started:
        return {"success": True, "message": "开始下载内置模型"}
    return {"success": False, "message": "下载已在进行中或模型已存在"}


@router.post("/bundled/cancel")
async def cancel_bundled_download() -> dict:
    """取消下载内置模型"""
    from .model_downloader import cancel_download
    cancel_download()
    return {"success": True, "message": "下载已取消"}


@router.get("/bundled/progress")
async def bundled_download_progress() -> dict:
    """获取下载进度"""
    from .model_downloader import download_state
    return download_state.to_dict()


@router.post("/bundled/load")
async def load_bundled_model() -> dict:
    """手动加载已下载的内置模型"""
    from .model_downloader import auto_load_bundled_model, is_bundled_model_ready

    if not is_bundled_model_ready():
        raise HTTPException(status_code=404, detail="内置模型尚未下载")

    success = auto_load_bundled_model()
    if success:
        return {"success": True, "message": "内置模型加载成功"}
    raise HTTPException(status_code=500, detail="内置模型加载失败")


@router.get("/scan")
async def scan_gguf_models(directory: str = "") -> dict:
    """扫描指定目录（或默认模型目录）中的 .gguf 文件"""
    scan_dir: Path | None = None

    if directory:
        scan_dir = Path(directory)
    else:
        try:
            from mechforge_core.config import get_config

            cfg = get_config()
            scan_dir = Path(cfg.provider.local.model_dir)
        except Exception:
            scan_dir = Path("./models")

    if not scan_dir or not scan_dir.exists():
        return {
            "success": True,
            "directory": str(scan_dir) if scan_dir else "",
            "models": [],
        }

    models = []
    for f in sorted(scan_dir.glob("*.gguf")):
        try:
            stat = f.stat()
            models.append(
                {
                    "name": f.stem,
                    "filename": f.name,
                    "path": str(f.resolve()),
                    "size": stat.st_size,
                    "loaded": (
                        state.gguf_model_path is not None
                        and Path(state.gguf_model_path).resolve() == f.resolve()
                    ),
                }
            )
        except OSError:
            continue

    return {
        "success": True,
        "directory": str(scan_dir.resolve()),
        "models": models,
    }
