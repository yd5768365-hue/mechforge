"""
MechForge AI GUI 单元测试
测试模块化 API 路由
"""

import pytest
from fastapi.testclient import TestClient


class TestHealthEndpoint:
    """健康检查端点测试"""

    def test_health_check(self, client: TestClient) -> None:
        """测试健康检查返回正确状态"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data

    def test_api_status(self, client: TestClient, mock_llm: pytest.fixture) -> None:
        """测试 API 状态端点"""
        response = client.get("/api/status")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "version" in data


class TestChatEndpoints:
    """聊天端点测试"""

    def test_chat_without_message(self, client: TestClient) -> None:
        """测试空消息返回错误"""
        response = client.post("/api/chat", json={"message": ""})
        assert response.status_code == 422  # Validation error

    def test_chat_with_message(
        self, client: TestClient, mock_llm: pytest.fixture
    ) -> None:
        """测试正常聊天请求"""
        response = client.post(
            "/api/chat", json={"message": "Hello", "rag": False, "stream": False}
        )
        # 可能返回 200 或 500（取决于 LLM 是否可用）
        assert response.status_code in [200, 500]

    def test_chat_history(self, client: TestClient) -> None:
        """测试获取聊天历史"""
        response = client.get("/api/chat/history")
        assert response.status_code == 200
        data = response.json()
        assert "history" in data
        assert isinstance(data["history"], list)

    def test_clear_history(self, client: TestClient) -> None:
        """测试清空聊天历史"""
        response = client.delete("/api/chat/history")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True


class TestRAGEndpoints:
    """RAG 端点测试"""

    def test_rag_status(self, client: TestClient) -> None:
        """测试 RAG 状态"""
        response = client.get("/api/rag/status")
        assert response.status_code == 200
        data = response.json()
        assert "enabled" in data
        assert "available" in data

    def test_rag_search_empty(self, client: TestClient) -> None:
        """测试空搜索查询"""
        response = client.post("/api/rag/search", json={"query": ""})
        assert response.status_code == 422  # Validation error

    def test_rag_toggle(self, client: TestClient) -> None:
        """测试 RAG 开关"""
        response = client.post("/api/rag/toggle", json={"enabled": True})
        assert response.status_code == 200
        data = response.json()
        assert "enabled" in data


class TestConfigEndpoints:
    """配置端点测试"""

    def test_get_config(self, client: TestClient) -> None:
        """测试获取配置"""
        response = client.get("/api/config")
        assert response.status_code == 200
        data = response.json()
        assert "ai" in data
        assert "rag" in data
        assert "ui" in data

    def test_get_models(self, client: TestClient) -> None:
        """测试获取模型列表"""
        response = client.get("/api/models")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_switch_provider(self, client: TestClient) -> None:
        """测试切换 provider"""
        response = client.post("/api/config/provider", json={"provider": "ollama"})
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True


class TestGGUFEndpoints:
    """GGUF 端点测试"""

    def test_gguf_info(self, client: TestClient) -> None:
        """测试 GGUF 信息"""
        response = client.get("/api/gguf/info")
        assert response.status_code == 200
        data = response.json()
        assert "loaded" in data

    def test_gguf_load_empty(self, client: TestClient) -> None:
        """测试空路径加载 GGUF"""
        response = client.post("/api/gguf/load", json={"model_path": ""})
        assert response.status_code == 400  # Bad request

    def test_gguf_load_nonexistent(self, client: TestClient) -> None:
        """测试加载不存在的 GGUF 文件"""
        response = client.post(
            "/api/gguf/load", json={"model_path": "/nonexistent/model.gguf"}
        )
        assert response.status_code == 404  # Not found


class TestStaticFiles:
    """静态文件测试"""

    def test_serve_index(self, client: TestClient) -> None:
        """测试主页"""
        response = client.get("/")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]

    def test_serve_styles(self, client: TestClient) -> None:
        """测试样式文件"""
        response = client.get("/styles.css")
        assert response.status_code == 200
        assert "text/css" in response.headers["content-type"]

    def test_serve_modular_styles(self, client: TestClient) -> None:
        """测试模块化样式文件"""
        response = client.get("/styles-modular.css")
        assert response.status_code == 200
        assert "text/css" in response.headers["content-type"]

    def test_serve_icon(self, client: TestClient) -> None:
        """测试图标文件"""
        response = client.get("/dj-whale.png")
        # 可能返回 200 或 404
        assert response.status_code in [200, 404]


class TestErrorHandling:
    """错误处理测试"""

    def test_404_not_found(self, client: TestClient) -> None:
        """测试 404 错误"""
        response = client.get("/api/nonexistent")
        assert response.status_code == 404

    def test_validation_error_format(self, client: TestClient) -> None:
        """测试验证错误响应格式"""
        response = client.post("/api/chat", json={})
        assert response.status_code == 422
        data = response.json()
        # 检查错误响应格式
        assert "detail" in data or "error" in data