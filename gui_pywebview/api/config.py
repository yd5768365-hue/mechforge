"""
配置 API 路由
"""

import logging
from typing import Any

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

    ai: dict[str, Any]
    rag: dict[str, Any]
    ui: dict[str, Any]


# ── API 端点 ──────────────────────────────────────────────────────────────────


@router.get("/config", response_model=ConfigResponse)
async def get_config_api() -> ConfigResponse:
    """获取当前配置"""
    provider_name, provider_config = get_active_provider_config()
    base_url = getattr(provider_config, "url", None) or getattr(provider_config, "base_url", "")
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
async def update_config(config: dict[str, Any]) -> dict:
    """更新配置"""
    # TODO: 实现配置持久化
    return {"success": True}


@router.post("/config/provider")
async def switch_provider(body: dict[str, Any]) -> dict:
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
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.post("/config/model")
async def switch_model(body: dict[str, Any]) -> dict:
    """切换模型（支持 Ollama 和 GGUF）"""
    model_name = body.get("model")
    provider = body.get("provider", "ollama")

    if not model_name:
        raise HTTPException(status_code=400, detail="model is required")

    try:
        # 映射前端 provider 名称到后端
        provider_map = {"ollama": "ollama", "gguf": "local"}
        backend_provider = provider_map.get(provider)
        
        if not backend_provider:
            raise HTTPException(status_code=400, detail=f"Unsupported provider: {provider}")

        # 切换 provider（如果需要）
        if state.current_provider != provider:
            state.current_provider = provider
            state.config.provider.default = backend_provider
            logger.info(f"Provider switched to: {provider}")

        # 根据 provider 类型切换模型
        if provider == "ollama":
            # 更新 Ollama 配置中的模型
            ollama_config = state.config.provider.get_config("ollama")
            if hasattr(ollama_config, "model"):
                ollama_config.model = model_name
            elif hasattr(ollama_config, "llm_model"):
                ollama_config.llm_model = model_name
            
            # 清空 LLM 客户端以重新初始化
            state.llm_client = None
            
            logger.info(f"Ollama model switched to: {model_name}")
            
            return {
                "success": True,
                "provider": provider,
                "model": model_name,
                "message": f"已切换到 {model_name}",
            }
        
        elif provider == "gguf":
            # 对于 GGUF，需要加载模型
            from mechforge_core.local_model_manager import LocalModelManager
            
            manager = LocalModelManager()
            gguf_models = manager.scan_models()
            
            # 查找匹配的模型
            target_model = None
            for m in gguf_models:
                if m.name == model_name and m.provider == "gguf":
                    target_model = m
                    break
            
            if not target_model:
                raise HTTPException(
                    status_code=404,
                    detail=f"GGUF model not found: {model_name}"
                )
            
            # 启动或加载模型
            if not target_model.loaded:
                success = manager.start_gguf_server(model_name)
                if not success:
                    raise HTTPException(
                        status_code=500,
                        detail=f"Failed to load GGUF model: {model_name}"
                    )
            
            # 更新状态
            state.gguf_model_path = target_model.path
            state.current_provider = "gguf"
            state.config.provider.default = "local"
            state.llm_client = None
            
            logger.info(f"GGUF model switched to: {model_name}")
            
            return {
                "success": True,
                "provider": provider,
                "model": model_name,
                "message": f"已切换到 {model_name}",
            }
        
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported provider: {provider}")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"模型切换失败: {e}")
        raise HTTPException(status_code=500, detail=f"模型切换失败: {str(e)}") from e


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
