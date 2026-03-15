"""
聊天 API 路由
"""

import json
import logging
from pathlib import Path

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
    system_prompt: str | None = Field(None, description="自定义系统提示词（覆盖默认）")


class ChatResponse(BaseModel):
    """聊天响应"""

    response: str
    model: str
    rag_used: bool = False
    context: str | None = None


# ── API 端点 ──────────────────────────────────────────────────────────────────


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    """非流式聊天 - 根据 current_provider 决定使用哪个后端"""
    user_message = request.message.strip()
    state.conversation_history.append({"role": "user", "content": user_message})

    context, rag_used = "", False
    if should_use_rag(request.rag):
        context, rag_used = retrieve_context(user_message)
        if rag_used and state.mode != "knowledge":
            state.set_mode("knowledge")
            logger.info("Auto-switched to knowledge mode (RAG enabled)")

    custom_prompt = request.system_prompt

    if state.current_provider == "gguf":
        return await _chat_with_gguf(user_message, context, rag_used, custom_prompt)
    else:
        return await _chat_with_ollama(user_message, context, rag_used, custom_prompt)


async def _chat_with_gguf(
    user_message: str, context: str, rag_used: bool, custom_prompt: str | None = None
) -> ChatResponse:
    """使用 GGUF 后端进行聊天"""
    """使用 GGUF 后端进行聊天"""
    if state.gguf_llm is None:
        raise HTTPException(
            status_code=503,
            detail="本地模型未加载。请在聊天界面顶部点击「开始下载」获取内置模型，或在状态栏切换到 Ollama。",
        )

    try:
        system_prompt = custom_prompt or state.get_system_prompt()
        messages = [{"role": "system", "content": system_prompt}]
        messages.extend(state.conversation_history[-10:])

        # 如果有上下文，添加到消息中（不是直接修改 user_message）
        if context:
            context_message = f"\n\n【检索到的相关知识】\n{context}"
            messages.append({"role": "user", "content": context_message})

        output = state.gguf_llm.create_chat_completion(
            messages=messages,
            temperature=0.7,
            max_tokens=2048,
        )
        response_text = output["choices"][0]["message"]["content"]
        model_name = Path(state.gguf_model_path).name if state.gguf_model_path else "gguf-local"
    except Exception as e:
        logger.error(f"GGUF 调用失败: {e}")
        raise HTTPException(status_code=500, detail=f"GGUF 调用失败: {str(e)}") from e

    state.conversation_history.append({"role": "assistant", "content": response_text})

    return ChatResponse(
        response=response_text,
        model=model_name,
        rag_used=rag_used,
        context=context if rag_used else None,
    )


async def _chat_with_ollama(
    user_message: str, context: str, rag_used: bool, custom_prompt: str | None = None
) -> ChatResponse:
    """使用 Ollama 后端进行聊天"""
    llm = get_llm_client()
    try:
        system_prompt = custom_prompt or state.get_system_prompt()
        messages = [{"role": "system", "content": system_prompt}]

        # 添加历史记录
        messages.extend(state.conversation_history[-10:])

        # 如果有上下文，添加到消息中（不是直接修改 user_message）
        if context:
            context_message = f"\n\n【检索到的相关知识】\n{context}"
            messages.append({"role": "user", "content": context_message})

        # 使用 chat 方法调用
        response_text = llm.provider.chat(messages)
    except Exception as e:
        logger.error(f"LLM 调用失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"LLM 调用失败: {e}") from e

    model_name = (
        llm.get_current_model_name() if hasattr(llm, "get_current_model_name") else "unknown"
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
        if rag_used and state.mode != "knowledge":
            state.set_mode("knowledge")
            logger.info("Auto-switched to knowledge mode (RAG enabled)")

    system_prompt = request.system_prompt or state.get_system_prompt()
    messages = [{"role": "system", "content": system_prompt}]
    messages.extend(state.conversation_history[-10:])

    # 如果有上下文，添加到消息中（不修改原始 user_message）
    if context:
        context_message = f"\n\n【检索到的相关知识】\n{context}"
        messages.append({"role": "user", "content": context_message})

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
            detail="本地模型未加载。请先下载内置模型或在状态栏切换到 Ollama。",
        )

    async def generate():
        full_response = ""
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
                        full_response += content
                        yield f"data: {json.dumps({'content': content})}\n\n"
            yield "data: [DONE]\n\n"
            state.conversation_history.append({"role": "assistant", "content": full_response})
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
            state.conversation_history.append({"role": "assistant", "content": full_response})
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


# ── 模式管理 ──────────────────────────────────────────────────────────────────


class ModeRequest(BaseModel):
    """模式切换请求"""

    mode: str = Field(..., description="模式: 'chat' 或 'knowledge'")


class ModeResponse(BaseModel):
    """模式响应"""

    mode: str
    is_knowledge_mode: bool
    system_prompt_preview: str


@router.get("/mode", response_model=ModeResponse)
async def get_mode() -> ModeResponse:
    """获取当前模式"""
    current_mode = state.get_mode()
    system_prompt = state.get_system_prompt()
    # 只返回前100字符作为预览
    preview = system_prompt[:100] + "..." if len(system_prompt) > 100 else system_prompt
    return ModeResponse(
        mode=current_mode,
        is_knowledge_mode=state.is_knowledge_mode(),
        system_prompt_preview=preview,
    )


@router.post("/mode", response_model=ModeResponse)
async def set_mode(request: ModeRequest) -> ModeResponse:
    """设置当前模式"""
    if request.mode not in ["chat", "knowledge"]:
        raise HTTPException(
            status_code=400, detail=f"Invalid mode: {request.mode}. Must be 'chat' or 'knowledge'"
        )

    success = state.set_mode(request.mode)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to set mode")

    logger.info(f"Mode switched to: {request.mode}")

    current_mode = state.get_mode()
    system_prompt = state.get_system_prompt()
    preview = system_prompt[:100] + "..." if len(system_prompt) > 100 else system_prompt

    return ModeResponse(
        mode=current_mode,
        is_knowledge_mode=state.is_knowledge_mode(),
        system_prompt_preview=preview,
    )


@router.post("/mode/reset")
async def reset_mode() -> dict:
    """重置为默认模式（chat）"""
    state.set_mode("chat")
    logger.info("Mode reset to default: chat")
    return {"success": True, "mode": "chat", "message": "Mode reset to default"}
