"""
配置 API 路由
"""

import logging
from typing import Any, Dict

import requests
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from .deps import get_active_provider_config, get_llm_client
from .state import state

logger = logging.getLogger("mechforge.api.config")

router = APIRouter(prefix="/api", tags=["配置"])


# ── 数据模型 ──────────────────────────────────────────────────────────────────


class ConfigResponse(BaseModel):
    """配置响应"""

    ai: Dict[str, Any]
    rag: Dict[str, Any]
    ui: Dict[str, Any]


# ── API 端点 ──────────────────────────────────────────────────────────────────


@router.get("/config", response_model=ConfigResponse)
async def get_config_api() -> ConfigResponse:
    """获取当前配置"""
    provider_name, provider_config = get_active_provider_config()
    base_url = getattr(provider_config, "url", None) or getattr(
        provider_config, "base_url", ""
    )
    model = getattr(provider_config, "model", "unknown")

    return ConfigResponse(
        ai={
            "provider": provider_name,
            "model": model,
            "base_url": base_url,
        },
        rag={
            "enabled": state.config.knowledge.rag.enabled,
            "backend": "local",
            "top_k": state.config.knowledge.rag.top_k,
            "embedding_model": state.config.knowledge.rag.embedding_model,
        },
        ui={"theme": "dark", "language": "zh-CN"},
    )


@router.post("/config")
async def update_config(config: Dict[str, Any]) -> dict:
    """更新配置"""
    # TODO: 实现配置持久化
    return {"success": True}


@router.post("/config/provider")
async def switch_provider(body: Dict[str, Any]) -> dict:
    """切换 AI provider (ollama / gguf)"""
    provider = body.get("provider", "ollama")

    # 保存当前使用的 provider
    state.current_provider = provider
    logger.info(f"Provider switched to: {provider}")

    # 映射前端 provider 名称到后端
    provider_map = {"ollama": "ollama", "gguf": "local"}

    backend_provider = provider_map.get(provider)
    if not backend_provider:
        raise HTTPException(status_code=400, detail=f"Unsupported provider: {provider}")

    try:
        # 更新配置
        state.config.provider.default = backend_provider
        logger.info(f"Backend provider set to: {backend_provider}")

        # 重新创建 LLM 客户端
        state.llm_client = None
        llm = get_llm_client()

        return {
            "success": True,
            "provider": provider,
            "backend": backend_provider,
            "model": (
                llm.get_current_model_name()
                if hasattr(llm, "get_current_model_name")
                else "unknown"
            ),
        }
    except Exception as e:
        logger.error(f"Provider 切换失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/models")
async def get_models() -> list:
    """获取可用模型列表，包括 Ollama 和本地 GGUF 模型"""
    all_models = []

    # 1. 尝试获取 Ollama 模型
    try:
        ollama_url = state.config.provider.ollama.url
        resp = requests.get(f"{ollama_url}/api/tags", timeout=5)
        if resp.status_code == 200:
            for m in resp.json().get("models", []):
                all_models.append(
                    {
                        "name": m["name"],
                        "provider": "ollama",
                        "size": m.get("size", 0),
                        "loaded": True,
                    }
                )
    except Exception:
        pass

    # 2. 获取本地 GGUF 模型
    try:
        from mechforge_core.local_model_manager import LocalModelManager

        manager = LocalModelManager()
        gguf_models = manager.scan_models()

        for m in gguf_models:
            if m.provider == "gguf":
                all_models.append(
                    {
                        "name": m.name,
                        "provider": "gguf",
                        "size": m.size,
                        "loaded": m.loaded,
                        "path": m.path,
                        "url": m.url,
                    }
                )
    except Exception as e:
        logger.warning(f"扫描 GGUF 模型失败: {e}")

    # 3. 如果没有模型，返回配置中的默认模型
    if not all_models:
        provider_name, provider_config = get_active_provider_config()
        all_models.append(
            {
                "name": getattr(
                    provider_config,
                    "model",
                    getattr(provider_config, "llm_model", "unknown"),
                ),
                "provider": provider_name,
            }
        )

    return all_models