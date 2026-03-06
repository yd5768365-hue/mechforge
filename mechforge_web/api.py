"""
MechForge Web API 路由

RESTful API + WebSocket 支持
"""

import uuid

from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect
from pydantic import BaseModel

from mechforge_ai.llm_client import LLMClient
from mechforge_ai.rag_engine import RAGEngine
from mechforge_core.config import get_config
from mechforge_work.cae_core import CAEEngine

router = APIRouter()

# ==================== 数据模型 ====================


class ChatRequest(BaseModel):
    message: str
    model: str | None = None
    rag: bool = False
    stream: bool = True


class ChatResponse(BaseModel):
    success: bool
    message: str
    message_id: str | None = None


class KnowledgeSearchRequest(BaseModel):
    query: str
    top_k: int = 5


class KnowledgeSearchResponse(BaseModel):
    results: list[dict]
    total: int


class CAEMeshRequest(BaseModel):
    size: float = 5.0
    mesh_type: str = "tet"


class CAESolveRequest(BaseModel):
    analysis_type: str = "static"
    material: str = "steel"


# ==================== 全局实例 ====================

_llm_client: LLMClient | None = None
_rag_engine: RAGEngine | None = None
_cae_engine: CAEEngine | None = None


def get_llm_client() -> LLMClient:
    global _llm_client
    if _llm_client is None:
        _llm_client = LLMClient()
    return _llm_client


def get_rag_engine() -> RAGEngine:
    global _rag_engine
    if _rag_engine is None:
        config = get_config()
        _rag_engine = RAGEngine(
            knowledge_path=config.knowledge.path,
            top_k=config.knowledge.rag.top_k,
        )
    return _rag_engine


def get_cae_engine() -> CAEEngine:
    global _cae_engine
    if _cae_engine is None:
        _cae_engine = CAEEngine()
    return _cae_engine


# ==================== WebSocket 处理 ====================


class ConnectionManager:
    """WebSocket 连接管理器"""

    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def send_message(self, websocket: WebSocket, message: dict):
        await websocket.send_json(message)


manager = ConnectionManager()


@router.websocket("/ws/chat")
async def websocket_chat(websocket: WebSocket):
    """WebSocket 聊天端点"""
    await manager.connect(websocket)

    try:
        while True:
            # 接收消息
            data = await websocket.receive_json()

            message = data.get("message", "")
            use_rag = data.get("rag", False)
            _model = data.get("model", "ollama")

            if not message:
                continue

            # 生成消息 ID
            message_id = str(uuid.uuid4())[:8]

            # 发送确认
            await manager.send_message(websocket, {"type": "ack", "messageId": message_id})

            # 获取 LLM 客户端
            llm = get_llm_client()

            # RAG 检索
            context = ""
            if use_rag:
                rag = get_rag_engine()
                if rag.is_available:
                    context = rag.search(message)

            # 流式响应
            try:
                # 开始流式传输
                await manager.send_message(
                    websocket, {"type": "stream_start", "messageId": message_id}
                )

                # 调用 LLM (流式)
                full_response = ""
                for chunk in llm.call(message, context, stream=True):
                    full_response += chunk
                    await manager.send_message(
                        websocket,
                        {"type": "stream", "messageId": message_id, "content": full_response},
                    )

                # 流式结束
                await manager.send_message(
                    websocket, {"type": "stream_end", "messageId": message_id}
                )

                # 保存到历史
                llm.conversation_history.append({"role": "user", "content": message})
                llm.conversation_history.append({"role": "assistant", "content": full_response})

            except Exception as e:
                await manager.send_message(websocket, {"type": "error", "message": str(e)})

    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        await manager.send_message(
            websocket, {"type": "error", "message": f"WebSocket 错误: {str(e)}"}
        )
        manager.disconnect(websocket)


# ==================== REST API 路由 ====================


@router.get("/health")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "version": "0.5.0",
        "services": {"llm": True, "rag": get_rag_engine().is_available, "cae": True},
    }


@router.get("/config")
async def get_configuration():
    """获取配置"""
    config = get_config()
    return {
        "provider": config.provider.default,
        "model": (
            config.provider.get_config().model
            if hasattr(config.provider.get_config(), "model")
            else "unknown"
        ),
        "rag_enabled": config.knowledge.rag.enabled,
        "knowledge_path": str(config.knowledge.path),
    }


# ----- 聊天 API -----


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """非流式聊天 API"""
    try:
        llm = get_llm_client()

        # RAG
        context = ""
        if request.rag:
            rag = get_rag_engine()
            if rag.is_available:
                context = rag.search(request.message)

        # 调用 LLM (非流式)
        response = llm.call(request.message, context, stream=False)

        return ChatResponse(success=True, message=response, message_id=str(uuid.uuid4())[:8])

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/chat/history")
async def get_chat_history(limit: int = 50):
    """获取对话历史"""
    llm = get_llm_client()
    history = llm.conversation_history[-limit:]
    return {"history": history}


@router.delete("/chat/history")
async def clear_chat_history():
    """清空对话历史"""
    llm = get_llm_client()
    llm.conversation_history = []
    return {"success": True}


# ----- 知识库 API -----


@router.post("/knowledge/search", response_model=KnowledgeSearchResponse)
async def search_knowledge(request: KnowledgeSearchRequest):
    """知识库搜索"""
    try:
        rag = get_rag_engine()

        if not rag.is_available:
            raise HTTPException(status_code=503, detail="知识库不可用")

        # 执行搜索
        context = rag.search(request.query)

        # 解析结果为结构化格式
        results = []
        # 这里简化处理，实际应该返回结构化结果
        if context:
            results.append(
                {"title": "相关文档", "content": context[:500], "source": "知识库", "score": 0.95}
            )

        return KnowledgeSearchResponse(results=results, total=len(results))

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/knowledge/status")
async def get_knowledge_status():
    """获取知识库状态"""
    rag = get_rag_engine()
    return {
        "available": rag.is_available,
        "document_count": rag.doc_count,
        "path": str(rag.knowledge_path) if rag.knowledge_path else None,
    }


# ----- CAE API -----


@router.post("/cae/demo")
async def run_cae_demo():
    """运行 CAE 示例"""
    try:
        engine = get_cae_engine()

        # 创建悬臂梁示例
        success = engine.setup_cantilever_beam(
            length=100.0, width=10.0, height=10.0, mesh_size=2.0, force=1000.0
        )

        if success:
            return {
                "success": True,
                "geometry": {"filename": "cantilever_beam.step", "dimensions": [100, 10, 10]},
                "message": "示例模型已加载",
            }
        else:
            raise HTTPException(status_code=500, detail="示例加载失败")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.post("/cae/mesh")
async def generate_cae_mesh(request: CAEMeshRequest):
    """生成网格"""
    try:
        engine = get_cae_engine()

        if not engine.geometry_file:
            raise HTTPException(status_code=400, detail="请先加载几何模型")

        mesh = engine.generate_mesh(
            mesh_size=request.size,
            mesh_type=request.mesh_type,  # type: ignore
        )

        return {
            "success": True,
            "mesh": {
                "nodes": mesh.num_nodes,
                "elements": mesh.num_elements,
                "type": mesh.element_type,
            },
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.post("/cae/solve")
async def solve_cae(request: CAESolveRequest):
    """执行求解"""
    try:
        engine = get_cae_engine()

        if not engine.mesh:
            raise HTTPException(status_code=400, detail="请先生成网格")

        # 设置材料（如果不存在）
        if not engine.materials:
            from mechforge_work.cae_core import Material

            engine.add_material(Material(name="Steel", youngs_modulus=210000, poisson_ratio=0.3))

        # 执行求解
        result = engine.solve()

        if result.success:
            return {
                "success": True,
                "results": {
                    "max_displacement": result.max_displacement,
                    "max_von_mises": result.max_von_mises,
                    "message": result.message,
                },
            }
        else:
            raise HTTPException(status_code=500, detail=result.message)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/cae/results")
async def get_cae_results():
    """获取 CAE 结果"""
    engine = get_cae_engine()

    if not engine.result:
        raise HTTPException(status_code=404, detail="尚未求解")

    return {
        "success": engine.result.success,
        "max_displacement": engine.result.max_displacement,
        "max_von_mises": engine.result.max_von_mises,
        "message": engine.result.message,
    }


@router.get("/cae/export/{format}")
async def export_cae_results(format: str):
    """导出 CAE 结果"""
    # TODO: 实现结果导出
    return {"success": True, "format": format}


# ----- 系统 API -----


@router.get("/system/status")
async def get_system_status():
    """获取系统状态"""
    import psutil

    return {
        "cpu_percent": psutil.cpu_percent(),
        "memory_percent": psutil.virtual_memory().percent,
        "disk_usage": psutil.disk_usage("/").percent,
        "connections": len(manager.active_connections),
    }
