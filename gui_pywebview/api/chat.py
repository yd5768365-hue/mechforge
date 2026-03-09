"""
聊天 API 路由
"""

import json
import logging
from pathlib import Path
from typing import Any, Dict, Optional

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from .deps import get_llm_client, retrieve_context, should_use_rag
from .state import state

logger = logging.getLogger("mechforge.api.chat")

router = APIRouter(prefix="/api", tags=["聊天"])


# ── 数据模型 ──────────────────────────────────────────────────────────────────


class ChatRequest(BaseModel):
    """聊天请求"""

    message: str = Field(..., min_length=1, description="用户消息")
    rag: bool = Field(False, description="是否启用 RAG 检索")
    stream: bool = Field(False, description="是否使用流式响应")


class ChatResponse(BaseModel):
    """聊天响应"""

    response: str
    model: str
    rag_used: bool = False
    context: Optional[str] = None


# ── API 端点 ──────────────────────────────────────────────────────────────────


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    """非流式聊天 - 根据 current_provider 决定使用哪个后端"""
    user_message = request.message.strip()
    state.conversation_history.append({"role": "user", "content": user_message})

    context, rag_used = "", False
    if should_use_rag(request.rag):
        context, rag_used = retrieve_context(user_message)

    # 根据当前 provider 决定使用哪个后端
    if state.current_provider == "gguf":
        return await _chat_with_gguf(user_message, context, rag_used)
    else:
        return await _chat_with_ollama(user_message, context, rag_used)


async def _chat_with_gguf(
    user_message: str, context: str, rag_used: bool
) -> ChatResponse:
    """使用 GGUF 后端进行聊天"""
    if state.gguf_llm is None:
        raise HTTPException(
            status_code=503,
            detail="GGUF model not loaded. Please enter model path and click Load in API selector.",
        )

    try:
        messages = state.conversation_history[-10:]
        output = state.gguf_llm.create_chat_completion(
            messages=messages,
            temperature=0.7,
            max_tokens=2048,
        )
        response_text = output["choices"][0]["message"]["content"]
        model_name = (
            Path(state.gguf_model_path).name
            if state.gguf_model_path
            else "gguf-local"
        )
    except Exception as e:
        logger.error(f"GGUF 调用失败: {e}")
        raise HTTPException(status_code=500, detail=f"GGUF 调用失败: {str(e)}")

    state.conversation_history.append({"role": "assistant", "content": response_text})

    return ChatResponse(
        response=response_text,
        model=model_name,
        rag_used=rag_used,
        context=context if rag_used else None,
    )


async def _chat_with_ollama(
    user_message: str, context: str, rag_used: bool
) -> ChatResponse:
    """使用 Ollama 后端进行聊天"""
    llm = get_llm_client()
    try:
        response_text = llm.call(user_message, context)
    except Exception as e:
        logger.error(f"LLM 调用失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"LLM 调用失败: {e}")

    model_name = (
        llm.get_current_model_name()
        if hasattr(llm, "get_current_model_name")
        else "unknown"
    )

    state.conversation_history.append({"role": "assistant", "content": response_text})

    return ChatResponse(
        response=response_text,
        model=model_name,
        rag_used=rag_used,
        context=context if rag_used else None,
    )


@router.post("/chat/stream")
async def chat_stream(request: ChatRequest):
    """流式聊天（SSE）- 根据 current_provider 决定使用哪个后端"""
    user_message = request.message.strip()
    state.conversation_history.append({"role": "user", "content": user_message})

    context, rag_used = "", False
    if should_use_rag(request.rag):
        context, rag_used = retrieve_context(user_message)

    # 构建消息列表（最近 10 条历史）
    messages = [{"role": "system", "content": "You are a helpful AI assistant."}]
    messages.extend(state.conversation_history[-10:])
    if context:
        messages[-1]["content"] = f"{user_message}\n\n相关上下文:\n{context}"

    # 根据当前 provider 选择后端
    if state.current_provider == "gguf":
        return await _stream_with_gguf(messages)
    else:
        return await _stream_with_ollama(messages)


async def _stream_with_gguf(messages: list):
    """使用 GGUF 后端进行流式聊天"""

    if state.gguf_llm is None:
        raise HTTPException(
            status_code=503,
            detail="GGUF model not loaded. Please enter model path and click Load in API selector.",
        )

    async def generate():
        try:
            for chunk in state.gguf_llm.create_chat_completion(
                messages=messages,
                temperature=0.7,
                max_tokens=2048,
                stream=True,
            ):
                if "choices" in chunk and len(chunk["choices"]) > 0:
                    delta = chunk["choices"][0].get("delta", {})
                    content = delta.get("content", "")
                    if content:
                        data = json.dumps({"choices": [{"delta": {"content": content}}]})
                        yield f"data: {data}\n\n"
            yield "data: [DONE]\n\n"
        except Exception as e:
            logger.error(f"GGUF 流式调用失败: {e}")
            yield f"data: {json.dumps({'error': str(e)})}\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


async def _stream_with_ollama(messages: list):
    """使用 Ollama 后端进行流式聊天"""
    llm = get_llm_client()

    async def generate():
        full_response = ""
        try:
            for chunk in llm.provider.chat(messages, stream=True):
                if chunk:
                    full_response += chunk
                    yield f"data: {json.dumps({'content': chunk})}\n\n"
            yield "data: [DONE]\n\n"
            state.conversation_history.append(
                {"role": "assistant", "content": full_response}
            )
        except Exception as e:
            logger.error(f"流式生成失败: {e}", exc_info=True)
            yield f"data: {json.dumps({'error': str(e)})}\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@router.get("/chat/history")
async def get_history() -> dict:
    """获取对话历史"""
    return {"history": state.conversation_history}


@router.delete("/chat/history")
async def clear_history() -> dict:
    """清空对话历史"""
    state.conversation_history.clear()
    logger.info("对话历史已清空")
    return {"success": True, "message": "History cleared"}