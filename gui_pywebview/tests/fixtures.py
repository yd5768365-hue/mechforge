"""
Pytest fixtures for MechForge AI GUI tests
"""

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

# 添加项目根目录到 Python 路径
PROJECT_ROOT = Path(__file__).parent.parent.parent
GUI_DIR = Path(__file__).parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

if str(GUI_DIR) not in sys.path:
    sys.path.insert(0, str(GUI_DIR))


@pytest.fixture
def client():
    """创建测试客户端"""
    from server import app

    return TestClient(app)


@pytest.fixture
def mock_llm():
    """模拟 LLM 客户端"""
    with patch("api.deps.get_llm_client") as mock:
        llm = MagicMock()
        llm.get_current_model_name.return_value = "test-model"
        llm.get_api_type.return_value = "ollama"
        llm.call.return_value = "Test response"
        llm.conversation_history = []
        mock.return_value = llm
        yield llm


@pytest.fixture
def mock_rag():
    """模拟 RAG 引擎"""
    with patch("api.deps.get_rag_engine") as mock:
        rag = MagicMock()
        rag.is_available = True
        rag.doc_count = 100
        rag.check_trigger.return_value = True
        rag.search.return_value = "Test context"
        mock.return_value = rag
        yield rag


@pytest.fixture
def sample_chat_request():
    """示例聊天请求"""
    return {"message": "What is machine learning?", "rag": True, "stream": False}


@pytest.fixture
def sample_rag_search_request():
    """示例 RAG 搜索请求"""
    return {"query": "machine learning", "limit": 5}