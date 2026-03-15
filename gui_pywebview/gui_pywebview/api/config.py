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
    knowledge: dict[str, Any] | None = None


# ── API 端点 ──────────────────────────────────────────────────────────────────


def _build_config_response() -> ConfigResponse:
    """构建配置响应（供 GET 复用）"""
    # Provider 与 model（前端用 gguf 表示 local）
    if state.current_provider == "gguf" and state.gguf_llm is not None:
        from pathlib import Path
        model_name = Path(state.gguf_model_path).stem if state.gguf_model_path else "gguf-local"
        provider_name = "gguf"
        base_url = "local"
    else:
        provider_name, provider_config = get_active_provider_config()
        if provider_name == "local":
            provider_name = "gguf"  # 前端统一用 gguf
        base_url = getattr(provider_config, "url", None) or getattr(provider_config, "base_url", "")
        model_name = getattr(provider_config, "model", "unknown")

    # UI 从 state.config 读取
    ui = state.config.ui
    theme = getattr(ui, "theme", "dark")
    language = getattr(ui, "language", "zh-CN")

    # 知识库路径
    kb_path = str(state.config.knowledge.path) if state.config.knowledge.path else "./knowledge"

    return ConfigResponse(
        ai={
            "provider": provider_name,
            "model": model_name,
            "base_url": base_url,
        },
        rag={
            "enabled": state.config.knowledge.rag.enabled,
            "backend": "local",
            "top_k": state.config.knowledge.rag.top_k,
            "embedding_model": state.config.knowledge.rag.embedding_model,
        },
        ui={"theme": theme, "language": language},
        knowledge={"path": kb_path},
    )


@router.get("/config", response_model=ConfigResponse)
async def get_config_api() -> ConfigResponse:
    """获取当前配置"""
    return _build_config_response()


@router.post("/config")
async def update_config(config: dict[str, Any]) -> dict:
    """更新配置并持久化到 config.yaml"""
    from pathlib import Path

    from mechforge_core.config import save_config

    try:
        # 1. Provider
        provider = config.get("provider", "ollama")
        provider_map = {"ollama": "ollama", "openai": "openai", "anthropic": "anthropic", "gguf": "local"}
        backend_provider = provider_map.get(provider, "ollama")
        state.config.provider.default = backend_provider

        # 若从 gguf 切走，清空 gguf 状态
        if provider != "gguf" and state.current_provider == "gguf":
            state.current_provider = "ollama"
            state.gguf_llm = None
            state.gguf_model_path = None

        # 2. API Key 与 model（按 provider 更新）
        api_key = config.get("apiKey", "")
        model = config.get("model", "")

        if provider == "openai":
            if api_key:
                state.config.provider.openai.api_key = api_key
            if model:
                state.config.provider.openai.model = model
        elif provider == "anthropic":
            if api_key:
                state.config.provider.anthropic.api_key = api_key
            if model:
                state.config.provider.anthropic.model = model
        elif provider == "ollama":
            if model:
                state.config.provider.ollama.model = model

        # 3. RAG
        if "ragEnabled" in config:
            state.config.knowledge.rag.enabled = bool(config["ragEnabled"])

        # 4. 知识库路径
        kb_path = config.get("kbPath")
        if kb_path:
            state.config.knowledge.path = Path(kb_path)

        # 5. UI（industrial 为前端扩展，持久化为 dark）
        theme = config.get("theme")
        if theme:
            if theme == "industrial":
                theme = "dark"
            if theme in ("dark", "light", "auto"):
                state.config.ui.theme = theme
        language = config.get("language")
        if language:
            state.config.ui.language = language

        # 6. 持久化
        save_config(state.config)
        logger.info("配置已保存到 config.yaml")

        # 7. 重置 LLM 客户端以应用新配置
        state.llm_client = None

        return {"success": True}
    except Exception as e:
        logger.error(f"保存配置失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e)) from e


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
            import os
            from pathlib import Path

            model_path = body.get("model_path", "")

            if not model_path:
                try:
                    from mechforge_core.local_model_manager import LocalModelManager
                    manager = LocalModelManager()
                    for m in manager.scan_models():
                        if m.name == model_name and m.provider == "gguf":
                            model_path = m.path
                            break
                except Exception:
                    pass

            if not model_path or not Path(model_path).exists():
                raise HTTPException(status_code=404, detail=f"GGUF 模型文件未找到: {model_name}")

            try:
                from llama_cpp import Llama
            except ImportError as exc:
                raise HTTPException(status_code=500, detail="llama-cpp-python 未安装") from exc

            if state.gguf_llm is not None:
                del state.gguf_llm
                state.gguf_llm = None

            state.gguf_llm = Llama(
                model_path=model_path,
                n_ctx=2048,
                n_threads=max(2, os.cpu_count() // 2 if os.cpu_count() else 2),
                verbose=False,
            )
            state.gguf_model_path = model_path
            state.current_provider = "gguf"
            state.config.provider.default = "local"
            state.llm_client = None

            logger.info(f"GGUF model loaded in-process: {model_name}")

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
