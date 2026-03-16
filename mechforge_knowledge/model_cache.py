"""
模型缓存模块 - 用于缓存 SentenceTransformer 和 CrossEncoder 模型，避免重复加载

使用单例模式确保模型只加载一次，提升性能
"""

from functools import lru_cache
from typing import Any, Optional

# 全局模型缓存
_model_cache: dict[str, Any] = {}


def get_sentence_transformer(model_name: str = "all-MiniLM-L6-v2") -> Any:
    """获取 SentenceTransformer 模型，使用缓存避免重复加载

    Args:
        model_name: 模型名称，默认 all-MiniLM-L6-v2

    Returns:
        SentenceTransformer 模型实例
    """
    cache_key = f"sentence_transformer:{model_name}"

    if cache_key not in _model_cache:
        from sentence_transformers import SentenceTransformer
        _model_cache[cache_key] = SentenceTransformer(model_name)

    return _model_cache[cache_key]


def get_cross_encoder(model_name: str = "cross-encoder/ms-marco-MiniLM-L-6-v2") -> Any:
    """获取 CrossEncoder 模型，使用缓存避免重复加载

    Args:
        model_name: 模型名称，默认 cross-encoder/ms-marco-MiniLM-L-6-v2

    Returns:
        CrossEncoder 模型实例
    """
    cache_key = f"cross_encoder:{model_name}"

    if cache_key not in _model_cache:
        from sentence_transformers import CrossEncoder
        _model_cache[cache_key] = CrossEncoder(model_name)

    return _model_cache[cache_key]


def clear_model_cache() -> None:
    """清空模型缓存"""
    global _model_cache
    _model_cache.clear()


def get_cache_stats() -> dict[str, int]:
    """获取缓存统计信息

    Returns:
        缓存的模型数量
    """
    return {
        "cached_models": len(_model_cache),
        "model_names": list(_model_cache.keys()),
    }
