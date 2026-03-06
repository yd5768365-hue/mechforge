"""
RAGFlow 后端实现

通过 API 调用 RAGFlow 服务，获得高级文档解析能力：
- OCR 文字识别
- 表格解析
- 版面分析
- 智能分块
"""

import asyncio
import os
from pathlib import Path
from typing import Any

import httpx

from mechforge_knowledge.backends.base import Document, KnowledgeBackend, SearchResult


class RAGFlowBackend(KnowledgeBackend):
    """
    RAGFlow API 后端

    通过 HTTP API 调用 RAGFlow 服务，支持：
    - 多格式文档上传（PDF、Word、图片等）
    - OCR 文字识别
    - 表格提取
    - 智能检索
    """

    def __init__(
        self,
        base_url: str = "http://localhost:9380",
        api_key: str = "",
        kb_id: str = "",
        timeout: int = 300,
    ):
        """
        初始化 RAGFlow 后端

        Args:
            base_url: RAGFlow 服务地址
            api_key: API 密钥
            kb_id: 知识库 ID
            timeout: 请求超时时间（秒）
        """
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.kb_id = kb_id
        self.timeout = timeout

    def _get_headers(self) -> dict[str, str]:
        """获取请求头"""
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    async def _request(
        self,
        method: str,
        endpoint: str,
        json_data: dict | None = None,
        files: dict | None = None,
    ) -> dict:
        """
        发送 HTTP 请求

        Args:
            method: HTTP 方法
            endpoint: API 端点
            json_data: JSON 数据
            files: 上传文件

        Returns:
            响应数据
        """
        url = f"{self.base_url}{endpoint}"
        headers = self._get_headers()

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            if method == "GET":
                response = await client.get(url, headers=headers)
            elif method == "POST":
                if files:
                    # 文件上传时不设置 Content-Type
                    headers.pop("Content-Type", None)
                    response = await client.post(url, headers=headers, files=files)
                else:
                    response = await client.post(url, headers=headers, json=json_data)
            elif method == "DELETE":
                response = await client.delete(url, headers=headers)
            else:
                raise ValueError(f"Unsupported method: {method}")

            response.raise_for_status()
            return response.json()

    async def add_document(self, file_path: str, metadata: dict[str, Any] | None = None) -> str:
        """
        上传文档到 RAGFlow 知识库

        Args:
            file_path: 文档文件路径
            metadata: 文档元数据（RAGFlow 暂不支持自定义元数据）

        Returns:
            文档 ID
        """
        if not self.kb_id:
            raise ValueError("Knowledge base ID (kb_id) is required")

        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        # 上传文件
        with open(file_path, "rb") as f:
            files = {"file": (file_path.name, f)}
            result = await self._request(
                "POST",
                f"/api/v1/dataset/{self.kb_id}/document",
                files=files,
            )

        # 提取文档 ID
        doc_id = result.get("data", {}).get("id", "")
        if not doc_id:
            # 尝试其他可能的响应格式
            doc_id = result.get("id", "")

        return doc_id

    async def add_text(self, content: str, title: str, metadata: dict[str, Any] | None = None) -> str:
        """
        添加文本内容到知识库

        RAGFlow 不直接支持文本上传，需要先创建临时文件再上传。

        Args:
            content: 文本内容
            title: 文档标题
            metadata: 文档元数据

        Returns:
            文档 ID
        """
        import tempfile

        # 创建临时文件
        with tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".md",
            delete=False,
            encoding="utf-8",
        ) as f:
            f.write(f"# {title}\n\n{content}")
            temp_path = f.name

        try:
            return await self.add_document(temp_path, metadata)
        finally:
            # 清理临时文件
            os.unlink(temp_path)

    async def search(self, query: str, top_k: int = 5) -> list[SearchResult]:
        """
        检索知识库

        Args:
            query: 查询文本
            top_k: 返回结果数量

        Returns:
            检索结果列表
        """
        if not self.kb_id:
            raise ValueError("Knowledge base ID (kb_id) is required")

        result = await self._request(
            "POST",
            "/api/v1/retrieval",
            json_data={
                "question": query,
                "dataset_ids": [self.kb_id],
                "top_k": top_k,
            },
        )

        # 解析结果
        results = []
        chunks = result.get("data", {}).get("chunks", [])
        if not chunks:
            chunks = result.get("data", [])

        for chunk in chunks:
            results.append(
                SearchResult(
                    content=chunk.get("content", chunk.get("text", "")),
                    score=chunk.get("similarity", chunk.get("score", 0.0)),
                    source=chunk.get("document_name", chunk.get("source", "")),
                    metadata={
                        "doc_id": chunk.get("document_id", chunk.get("doc_id", "")),
                        "chunk_id": chunk.get("id", chunk.get("chunk_id", "")),
                    },
                )
            )

        return results

    async def delete_document(self, doc_id: str) -> bool:
        """
        删除文档

        Args:
            doc_id: 文档 ID

        Returns:
            是否删除成功
        """
        if not self.kb_id:
            raise ValueError("Knowledge base ID (kb_id) is required")

        try:
            result = await self._request(
                "DELETE",
                f"/api/v1/dataset/{self.kb_id}/document/{doc_id}",
            )
            return result.get("code", -1) == 0 or result.get("success", False)
        except Exception:
            return False

    async def list_documents(self, limit: int = 100, offset: int = 0) -> list[Document]:
        """
        列出知识库中的文档

        Args:
            limit: 返回数量限制
            offset: 偏移量

        Returns:
            文档列表
        """
        if not self.kb_id:
            raise ValueError("Knowledge base ID (kb_id) is required")

        result = await self._request(
            "GET",
            f"/api/v1/dataset/{self.kb_id}/document?page={offset // limit + 1}&page_size={limit}",
        )

        documents = []
        docs = result.get("data", {}).get("docs", result.get("data", []))

        for doc in docs:
            documents.append(
                Document(
                    id=doc.get("id", ""),
                    title=doc.get("name", doc.get("title", "")),
                    content="",  # 列表接口通常不返回内容
                    source=doc.get("location", doc.get("source", "")),
                    metadata={
                        "status": doc.get("status", ""),
                        "chunk_count": doc.get("chunk_num", doc.get("chunk_count", 0)),
                        "create_time": doc.get("create_time", ""),
                    },
                )
            )

        return documents

    async def get_stats(self) -> dict[str, Any]:
        """
        获取知识库统计信息

        Returns:
            统计信息字典
        """
        if not self.kb_id:
            return {"status": "not_configured", "kb_id": ""}

        try:
            result = await self._request(
                "GET",
                f"/api/v1/dataset/{self.kb_id}",
            )
            data = result.get("data", {})
            return {
                "status": "connected",
                "kb_id": self.kb_id,
                "kb_name": data.get("name", ""),
                "document_count": data.get("document_count", 0),
                "chunk_count": data.get("chunk_count", 0),
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "kb_id": self.kb_id,
            }

    async def health_check(self) -> bool:
        """
        检查 RAGFlow 服务健康状态

        Returns:
            是否健康
        """
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.get(f"{self.base_url}/api/v1/health")
                return response.status_code == 200
        except Exception:
            return False

    # ==================== RAGFlow 特有方法 ====================

    async def create_knowledge_base(self, name: str, description: str = "") -> str:
        """
        创建知识库

        Args:
            name: 知识库名称
            description: 知识库描述

        Returns:
            知识库 ID
        """
        result = await self._request(
            "POST",
            "/api/v1/dataset",
            json_data={
                "name": name,
                "description": description,
            },
        )
        return result.get("data", {}).get("id", "")

    async def list_knowledge_bases(self) -> list[dict[str, Any]]:
        """
        列出所有知识库

        Returns:
            知识库列表
        """
        result = await self._request("GET", "/api/v1/dataset")
        return result.get("data", [])

    async def set_knowledge_base(self, kb_id: str) -> None:
        """
        设置当前使用的知识库

        Args:
            kb_id: 知识库 ID
        """
        self.kb_id = kb_id