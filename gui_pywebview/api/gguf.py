"""
GGUF 模型管理 API 路由
"""

import json
import logging
from pathlib import Path
from typing import Any, Dict, Optional

import requests
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from .state import state

logger = logging.getLogger("mechforge.api.gguf")

router = APIRouter(prefix="/api/gguf", tags=["GGUF"])


# ── 数据模型 ──────────────────────────────────────────────────────────────────


class GGUFLoadRequest(BaseModel):
    """GGUF 加载请求"""

    model_path: str = Field(..., description="模型文件路径")


# ── API 端点 ──────────────────────────────────────────────────────────────────


@router.post("/start")
async def start_gguf_server(body: Dict[str, Any]) -> dict:
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
        raise HTTPException(status_code=500, detail=str(e))


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
        gguf_url = "http://127.0.0.1:11435"
        resp = requests.get(f"{gguf_url}/health", timeout=2)
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
async def load_gguf_model(body: Dict[str, Any]) -> dict:
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

    except ImportError:
        raise HTTPException(
            status_code=500,
            detail="llama-cpp-python not installed. Run: pip install llama-cpp-python",
        )
    except Exception as e:
        logger.error(f"Failed to load GGUF model: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to load model: {str(e)}")


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