"""
LLM 客户端模块 - 负责所有 AI 模型 API 调用

支持:
- 多 Provider 统一接口 (OpenAI, Anthropic, Ollama, Local GGUF)
- 流式输出 (Streaming)
- 工具调用 (Function Calling)
- 异步调用
- 自动重试和错误处理
"""

import json
import time
from abc import ABC, abstractmethod
from collections.abc import AsyncGenerator, Callable, Generator
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import (
    Any,
)

import requests
from rich.console import Console

from mechforge_ai.prompts import get_system_prompt
from mechforge_core.config import get_config
from mechforge_core.mcp.tools import ToolRegistry, default_registry


class ProviderType(Enum):
    """AI 提供商类型"""

    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    OLLAMA = "ollama"
    LOCAL = "local"
    LOCAL_GGUF = "local_gguf"  # 新增：GGUF HTTP 服务


@dataclass
class ToolDefinition:
    """工具定义"""

    name: str
    description: str
    parameters: dict[str, Any] = field(default_factory=dict)
    required: list[str] = field(default_factory=list)

    def to_openai_format(self) -> dict[str, Any]:
        """转换为 OpenAI 工具格式"""
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": {
                    "type": "object",
                    "properties": self.parameters,
                    "required": self.required,
                },
            },
        }

    def to_ollama_format(self) -> dict[str, Any]:
        """转换为 Ollama 工具格式"""
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": {
                    "type": "object",
                    "properties": self.parameters,
                    "required": self.required,
                },
            },
        }


@dataclass
class ToolCall:
    """工具调用"""

    id: str
    name: str
    arguments: dict[str, Any]


@dataclass
class LLMResponse:
    """LLM 响应"""

    content: str
    tool_calls: list[ToolCall] = field(default_factory=list)
    model: str = ""
    usage: dict[str, int] = field(default_factory=dict)
    finish_reason: str = ""


class BaseLLMProvider(ABC):
    """LLM Provider 基类"""

    def __init__(self, config: Any):
        self.config = config
        self.console = Console()

    @abstractmethod
    def chat(
        self,
        messages: list[dict[str, str]],
        tools: list[ToolDefinition] | None = None,
        stream: bool = False,
    ) -> LLMResponse | Generator[str, None, None]:
        """聊天接口"""
        pass

    @abstractmethod
    async def achat(
        self,
        messages: list[dict[str, str]],
        tools: list[ToolDefinition] | None = None,
        stream: bool = False,
    ) -> LLMResponse | AsyncGenerator[str, None]:
        """异步聊天接口"""
        pass

    def _build_messages(
        self, user_input: str, context: str = "", history: list[dict] | None = None
    ) -> list[dict[str, str]]:
        """构建消息列表"""
        messages = [{"role": "system", "content": get_system_prompt()}]

        if history:
            messages.extend(history[-10:])

        user_content = user_input
        if context:
            user_content = f"{user_input}\n\n相关上下文:\n{context}"

        messages.append({"role": "user", "content": user_content})
        return messages


class OpenAIProvider(BaseLLMProvider):
    """OpenAI Provider"""

    def __init__(self, config: Any):
        super().__init__(config)
        self.base_url = config.base_url.rstrip("/")
        self.headers = {
            "Authorization": f"Bearer {config.api_key}",
            "Content-Type": "application/json",
        }

    def _make_request(self, data: dict[str, Any]) -> requests.Response:
        """发送请求（带重试）"""
        max_retries = self.config.max_retries
        timeout = self.config.timeout

        for attempt in range(max_retries):
            try:
                resp = requests.post(
                    f"{self.base_url}/chat/completions",
                    headers=self.headers,
                    json=data,
                    timeout=timeout,
                    stream=data.get("stream", False),
                )
                if resp.status_code == 200:
                    return resp
                if resp.status_code == 429:  # Rate limit
                    wait_time = 2**attempt
                    self.console.print(f"[yellow]速率限制，等待 {wait_time}s 后重试...[/yellow]")
                    time.sleep(wait_time)
                    continue
                resp.raise_for_status()
            except requests.exceptions.Timeout as e:
                if attempt == max_retries - 1:
                    raise Exception(f"请求超时（{timeout}s）") from e
                self.console.print(
                    f"[yellow]请求超时，重试 {attempt + 1}/{max_retries}...[/yellow]"
                )
            except requests.exceptions.ConnectionError as e:
                if attempt == max_retries - 1:
                    raise Exception("连接错误，请检查网络") from e
                self.console.print(
                    f"[yellow]连接错误，重试 {attempt + 1}/{max_retries}...[/yellow]"
                )

        raise Exception("API 错误: 达到最大重试次数")

    def chat(
        self,
        messages: list[dict[str, str]],
        tools: list[ToolDefinition] | None = None,
        stream: bool = False,
    ) -> LLMResponse | Generator[str, None, None]:
        """聊天接口"""
        data = {
            "model": self.config.model,
            "messages": messages,
            "temperature": get_config().chat.temperature,
            "max_tokens": get_config().chat.max_tokens,
            "stream": stream,
        }

        if tools:
            data["tools"] = [t.to_openai_format() for t in tools]
            data["tool_choice"] = "auto"

        if stream:
            return self._stream_chat(data)

        resp = self._make_request(data)
        result = resp.json()
        choice = result["choices"][0]
        message = choice["message"]

        # 解析工具调用
        tool_calls = []
        if "tool_calls" in message:
            for tc in message["tool_calls"]:
                if tc["type"] == "function":
                    tool_calls.append(
                        ToolCall(
                            id=tc["id"],
                            name=tc["function"]["name"],
                            arguments=json.loads(tc["function"]["arguments"]),
                        )
                    )

        return LLMResponse(
            content=message.get("content", ""),
            tool_calls=tool_calls,
            model=result.get("model", ""),
            usage=result.get("usage", {}),
            finish_reason=choice.get("finish_reason", ""),
        )

    def _stream_chat(self, data: dict[str, Any]) -> Generator[str, None, None]:
        """流式聊天"""
        data["stream"] = True
        resp = self._make_request(data)

        for line in resp.iter_lines():
            if not line:
                continue
            line = line.decode("utf-8")
            if line.startswith("data: "):
                line = line[6:]
            if line == "[DONE]":
                break
            try:
                chunk = json.loads(line)
                delta = chunk["choices"][0].get("delta", {})
                if "content" in delta:
                    yield delta["content"]
            except (json.JSONDecodeError, KeyError):
                continue

    async def achat(
        self,
        messages: list[dict[str, str]],
        tools: list[ToolDefinition] | None = None,
        stream: bool = False,
    ) -> LLMResponse | AsyncGenerator[str, None]:
        """异步聊天接口"""
        import httpx

        data = {
            "model": self.config.model,
            "messages": messages,
            "temperature": get_config().chat.temperature,
            "max_tokens": get_config().chat.max_tokens,
            "stream": stream,
        }

        if tools:
            data["tools"] = [t.to_openai_format() for t in tools]

        if stream:
            return self._async_stream_chat(data)

        async with httpx.AsyncClient(timeout=self.config.timeout) as client:
            resp = await client.post(
                f"{self.base_url}/chat/completions",
                headers=self.headers,
                json=data,
            )
            resp.raise_for_status()
            result = resp.json()
            choice = result["choices"][0]
            message = choice["message"]

            tool_calls = []
            if "tool_calls" in message:
                for tc in message["tool_calls"]:
                    if tc["type"] == "function":
                        tool_calls.append(
                            ToolCall(
                                id=tc["id"],
                                name=tc["function"]["name"],
                                arguments=json.loads(tc["function"]["arguments"]),
                            )
                        )

            return LLMResponse(
                content=message.get("content", ""),
                tool_calls=tool_calls,
                model=result.get("model", ""),
                usage=result.get("usage", {}),
            )

    async def _async_stream_chat(self, data: dict[str, Any]) -> AsyncGenerator[str, None]:
        """异步流式聊天"""
        import httpx

        data["stream"] = True

        async with (
            httpx.AsyncClient(timeout=self.config.timeout) as client,
            client.stream(
                "POST",
                f"{self.base_url}/chat/completions",
                headers=self.headers,
                json=data,
            ) as resp,
        ):
            async for line in resp.aiter_lines():
                if not line:
                    continue
                if line.startswith("data: "):
                    line = line[6:]
                if line == "[DONE]":
                    break
                try:
                    chunk = json.loads(line)
                    delta = chunk["choices"][0].get("delta", {})
                    if "content" in delta:
                        yield delta["content"]
                except (json.JSONDecodeError, KeyError):
                    continue


class AnthropicProvider(BaseLLMProvider):
    """Anthropic Provider"""

    def __init__(self, config: Any):
        super().__init__(config)
        self.base_url = config.base_url.rstrip("/")
        self.headers = {
            "x-api-key": config.api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        }

    def chat(
        self,
        messages: list[dict[str, str]],
        tools: list[ToolDefinition] | None = None,
        stream: bool = False,
    ) -> LLMResponse | Generator[str, None, None]:
        """聊天接口"""
        # 分离 system message
        system_msg = ""
        chat_messages = []
        for msg in messages:
            if msg["role"] == "system":
                system_msg = msg["content"]
            else:
                chat_messages.append(msg)

        data = {
            "model": self.config.model,
            "max_tokens": get_config().chat.max_tokens,
            "temperature": get_config().chat.temperature,
            "messages": chat_messages,
            "stream": stream,
        }

        if system_msg:
            data["system"] = system_msg

        if tools:
            data["tools"] = [
                {"name": t.name, "description": t.description, "input_schema": t.parameters}
                for t in tools
            ]

        if stream:
            return self._stream_chat(data)

        resp = requests.post(
            f"{self.base_url}/v1/messages",
            headers=self.headers,
            json=data,
            timeout=self.config.timeout,
        )
        resp.raise_for_status()
        result = resp.json()

        content = ""
        tool_calls = []
        for block in result.get("content", []):
            if block["type"] == "text":
                content += block["text"]
            elif block["type"] == "tool_use":
                tool_calls.append(
                    ToolCall(
                        id=block["id"],
                        name=block["name"],
                        arguments=block["input"],
                    )
                )

        return LLMResponse(
            content=content,
            tool_calls=tool_calls,
            model=result.get("model", ""),
            usage=result.get("usage", {}),
        )

    def _stream_chat(self, data: dict[str, Any]) -> Generator[str, None, None]:
        """流式聊天"""
        data["stream"] = True
        resp = requests.post(
            f"{self.base_url}/v1/messages",
            headers=self.headers,
            json=data,
            timeout=self.config.timeout,
            stream=True,
        )
        resp.raise_for_status()

        for line in resp.iter_lines():
            if not line:
                continue
            line = line.decode("utf-8")
            if not line.startswith("data: "):
                continue
            line = line[6:]
            try:
                event = json.loads(line)
                if event["type"] == "content_block_delta":
                    delta = event.get("delta", {})
                    if delta.get("type") == "text_delta":
                        yield delta["text"]
            except (json.JSONDecodeError, KeyError):
                continue

    async def achat(
        self,
        messages: list[dict[str, str]],
        tools: list[ToolDefinition] | None = None,
        stream: bool = False,
    ) -> LLMResponse | AsyncGenerator[str, None]:
        """异步聊天接口"""
        # 简化实现：同步调用包装
        if stream:
            # 返回异步生成器
            async def async_gen():
                for chunk in self.chat(messages, tools, stream=True):
                    yield chunk

            return async_gen()
        return self.chat(messages, tools, stream=False)


class OllamaProvider(BaseLLMProvider):
    """Ollama Provider"""

    def __init__(self, config: Any, model: str | None = None):
        super().__init__(config)
        self.base_url = config.url.rstrip("/")
        self.model = model or config.model

    def _get_model(self) -> str:
        """获取可用模型"""
        try:
            resp = requests.get(f"{self.base_url}/api/tags", timeout=10)
            if resp.status_code == 200:
                models = resp.json().get("models", [])
                if models:
                    return models[0].get("name", self.model)
        except Exception:
            pass
        return self.model

    def chat(
        self,
        messages: list[dict[str, str]],
        tools: list[ToolDefinition] | None = None,
        stream: bool = False,
    ) -> LLMResponse | Generator[str, None, None]:
        """聊天接口"""
        model = self._get_model()

        data = {
            "model": model,
            "messages": messages,
            "stream": stream,
            "options": {
                "temperature": get_config().chat.temperature,
                "num_predict": get_config().chat.max_tokens,
            },
        }

        if tools:
            data["tools"] = [t.to_ollama_format() for t in tools]

        if stream:
            return self._stream_chat(data)

        resp = requests.post(
            f"{self.base_url}/api/chat",
            json=data,
            timeout=self.config.timeout,
        )
        resp.raise_for_status()
        result = resp.json()

        message = result.get("message", {})
        content = message.get("content", "")

        # 解析工具调用
        tool_calls = []
        if "tool_calls" in message:
            for tc in message["tool_calls"]:
                tool_calls.append(
                    ToolCall(
                        id=tc.get("function", {}).get("name", ""),
                        name=tc.get("function", {}).get("name", ""),
                        arguments=tc.get("function", {}).get("arguments", {}),
                    )
                )

        return LLMResponse(
            content=content,
            tool_calls=tool_calls,
            model=model,
        )

    def _stream_chat(self, data: dict[str, Any]) -> Generator[str, None, None]:
        """流式聊天"""
        data["stream"] = True
        resp = requests.post(
            f"{self.base_url}/api/chat",
            json=data,
            timeout=self.config.timeout,
            stream=True,
        )
        resp.raise_for_status()

        for line in resp.iter_lines():
            if not line:
                continue
            try:
                data = json.loads(line)
                if "message" in data and "content" in data["message"]:
                    yield data["message"]["content"]
                if data.get("done", False):
                    break
            except json.JSONDecodeError:
                continue

    async def achat(
        self,
        messages: list[dict[str, str]],
        tools: list[ToolDefinition] | None = None,
        stream: bool = False,
    ) -> LLMResponse | AsyncGenerator[str, None]:
        """异步聊天接口"""
        if stream:

            async def async_gen():
                for chunk in self.chat(messages, tools, stream=True):
                    yield chunk

            return async_gen()
        return self.chat(messages, tools, stream=False)


class UnifiedLocalProvider(BaseLLMProvider):
    """
    统一本地模型 Provider

    同时支持 Ollama 和 GGUF HTTP 服务，提供一致的接口。
    """

    def __init__(
        self, config: Any, base_url: str = "http://localhost:11434", model: str | None = None
    ):
        super().__init__(config)
        self.base_url = base_url.rstrip("/")
        self.model = model or getattr(config, "model", "unknown")
        self.provider_type = "ollama" if "11434" in base_url else "gguf"

    def _make_request(self, endpoint: str, data: dict) -> requests.Response:
        """发送 HTTP 请求"""
        url = f"{self.base_url}{endpoint}"
        response = requests.post(url, json=data, timeout=300)
        response.raise_for_status()
        return response

    def chat(
        self,
        messages: list[dict[str, str]],
        tools: list[ToolDefinition] | None = None,
        stream: bool = False,
    ) -> LLMResponse | Generator[str, None, None]:
        """聊天接口 - 兼容 Ollama 和 GGUF 服务器"""
        if stream:
            return self._stream_chat(messages, tools)

        data = {
            "model": self.model,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": get_config().chat.temperature,
                "num_predict": get_config().chat.max_tokens,
            },
        }

        if tools and self.provider_type == "ollama":
            data["tools"] = [t.to_ollama_format() for t in tools]

        response = self._make_request("/api/chat", data)
        result = response.json()

        message = result.get("message", {})
        content = message.get("content", "")

        # 解析工具调用
        tool_calls = []
        if "tool_calls" in message:
            for tc in message["tool_calls"]:
                tool_calls.append(
                    ToolCall(
                        id=tc.get("function", {}).get("name", ""),
                        name=tc.get("function", {}).get("name", ""),
                        arguments=tc.get("function", {}).get("arguments", {}),
                    )
                )

        return LLMResponse(
            content=content,
            tool_calls=tool_calls,
            model=self.model,
        )

    def _stream_chat(
        self, messages: list[dict[str, str]], tools: list[ToolDefinition] | None
    ) -> Generator[str, None, None]:
        """流式聊天"""
        data = {
            "model": self.model,
            "messages": messages,
            "stream": True,
            "options": {
                "temperature": get_config().chat.temperature,
                "num_predict": get_config().chat.max_tokens,
            },
        }

        response = requests.post(
            f"{self.base_url}/api/chat",
            json=data,
            stream=True,
            timeout=300,
        )
        response.raise_for_status()

        for line in response.iter_lines():
            if not line:
                continue
            try:
                chunk = json.loads(line)
                if "message" in chunk and "content" in chunk["message"]:
                    yield chunk["message"]["content"]
                if chunk.get("done", False):
                    break
            except json.JSONDecodeError:
                continue

    async def achat(
        self,
        messages: list[dict[str, str]],
        tools: list[ToolDefinition] | None = None,
        stream: bool = False,
    ) -> LLMResponse | AsyncGenerator[str, None]:
        """异步聊天接口"""
        if stream:

            async def async_gen():
                for chunk in self.chat(messages, tools, stream=True):
                    yield chunk

            return async_gen()
        return self.chat(messages, tools, stream=False)


class LocalGGUFProvider(BaseLLMProvider):
    """
    本地 GGUF 模型 Provider (直接加载模式)

    如果 GGUF HTTP 服务未运行，直接加载模型文件。
    作为 UnifiedLocalProvider 的备选方案。
    """

    def __init__(self, config: Any):
        super().__init__(config)
        self._llm: Any | None = None
        self._model_path = Path(config.model_dir) / config.llm_model

    def _load_model(self) -> Any:
        """加载模型"""
        if self._llm is not None:
            return self._llm

        try:
            from llama_cpp import Llama
        except ImportError as e:
            raise ImportError("请安装 llama-cpp-python: pip install llama-cpp-python") from e

        if not self._model_path.exists():
            raise FileNotFoundError(f"模型文件不存在: {self._model_path}")

        self.console.print("[spring_green3]加载本地模型中...[/spring_green3]")

        n_threads = getattr(self.config, "n_threads", None)

        self._llm = Llama(
            model_path=str(self._model_path),
            n_ctx=self.config.n_ctx,
            n_gpu_layers=self.config.n_gpu_layers,
            n_threads=n_threads,
            verbose=False,
        )
        return self._llm

    def chat(
        self,
        messages: list[dict[str, str]],
        tools: list[ToolDefinition] | None = None,
        stream: bool = False,
    ) -> LLMResponse | Generator[str, None, None]:
        """聊天接口"""
        llm = self._load_model()

        if stream:
            return self._stream_chat(llm, messages)

        output = llm.create_chat_completion(
            messages=messages,
            temperature=get_config().chat.temperature,
            max_tokens=get_config().chat.max_tokens,
        )

        message = output["choices"][0]["message"]
        return LLMResponse(
            content=message.get("content", ""),
            model=self.config.llm_model,
        )

    def _stream_chat(self, llm: Any, messages: list[dict[str, str]]) -> Generator[str, None, None]:
        """流式聊天"""
        output = llm.create_chat_completion(
            messages=messages,
            temperature=get_config().chat.temperature,
            max_tokens=get_config().chat.max_tokens,
            stream=True,
        )

        for chunk in output:
            delta = chunk["choices"][0].get("delta", {})
            if "content" in delta:
                yield delta["content"]

    async def achat(
        self,
        messages: list[dict[str, str]],
        tools: list[ToolDefinition] | None = None,
        stream: bool = False,
    ) -> LLMResponse | AsyncGenerator[str, None]:
        """异步聊天接口"""
        if stream:

            async def async_gen():
                for chunk in self.chat(messages, tools, stream=True):
                    yield chunk

            return async_gen()
        return self.chat(messages, tools, stream=False)


class LLMClient:
    """LLM 客户端 - 统一接口"""

    def __init__(self, model: str | None = None, use_local_manager: bool = True):
        self.config = get_config()
        self._model_override = model
        self._provider: BaseLLMProvider | None = None
        self.conversation_history: list[dict[str, str]] = []
        self._tools: list[ToolDefinition] = []
        self._tool_handlers: dict[str, Callable] = {}
        self._local_manager = None
        self._use_local_manager = use_local_manager

        if use_local_manager:
            self._init_local_manager()

    def _init_local_manager(self):
        """初始化本地模型管理器"""
        try:
            from mechforge_core.local_model_manager import LocalModelManager

            self._local_manager = LocalModelManager()
        except ImportError:
            pass

    def select_local_model(self) -> str | None:
        """交互式选择本地模型"""
        if self._local_manager:
            return self._local_manager.select_model_interactive()
        return None

    @property
    def provider(self) -> BaseLLMProvider:
        """获取当前 Provider 实例"""
        if self._provider is None:
            provider_type = self.config.provider.get_active_provider()
            provider_cfg = self.config.provider.get_config(provider_type)

            # 如果使用本地模型管理器，优先使用 UnifiedLocalProvider
            if (
                self._use_local_manager
                and provider_type in ["ollama", "local"]
                and self._local_manager
            ):
                # 扫描可用模型
                models = self._local_manager.scan_models()
                if models:
                    # 使用第一个可用的本地模型
                    first_model = models[0]
                    if first_model.provider == "ollama":
                        self._provider = UnifiedLocalProvider(
                            provider_cfg, base_url=first_model.url, model=first_model.name
                        )
                    elif first_model.provider == "gguf":
                        # 检查 GGUF 服务器是否运行
                        if first_model.loaded:
                            self._provider = UnifiedLocalProvider(
                                provider_cfg, base_url=first_model.url, model=first_model.name
                            )
                        else:
                            # 启动 GGUF 服务器
                            if self._local_manager.start_gguf_server(first_model.name):
                                self._provider = UnifiedLocalProvider(
                                    provider_cfg,
                                    base_url=first_model.url,
                                    model=first_model.name,
                                )
                            else:
                                # 回退到直接加载模式
                                self._provider = LocalGGUFProvider(provider_cfg)
                    return self._provider

            # 默认 Provider 映射
            providers = {
                "openai": OpenAIProvider,
                "anthropic": AnthropicProvider,
                "ollama": OllamaProvider,
                "local": LocalGGUFProvider,
            }

            provider_class = providers.get(provider_type, OllamaProvider)
            self._provider = provider_class(provider_cfg)

        return self._provider

    def register_tool(
        self,
        name: str,
        description: str,
        handler: Callable,
        parameters: dict[str, Any] | None = None,
        required: list[str] | None = None,
    ) -> None:
        """注册工具"""
        tool = ToolDefinition(
            name=name,
            description=description,
            parameters=parameters or {},
            required=required or [],
        )
        self._tools.append(tool)
        self._tool_handlers[name] = handler

    def load_mcp_tools(self, registry: ToolRegistry | None = None) -> int:
        """
        加载 MCP 工具到 LLM 客户端

        Args:
            registry: 工具注册表，默认使用 default_registry

        Returns:
            加载的工具数量
        """
        registry = registry or default_registry
        count = 0

        for tool in registry.list_tools():
            # 转换为 ToolDefinition
            tool_def = ToolDefinition(
                name=tool.name,
                description=tool.description,
                parameters=tool.to_schema()["parameters"]["properties"],
                required=tool.to_schema()["parameters"].get("required", []),
            )
            self._tools.append(tool_def)
            self._tool_handlers[tool.name] = tool.execute
            count += 1

        print(f"[MCP] 已加载 {count} 个工具")
        return count

    def connect_mcp_server(
        self,
        command: str,
        args: list[str] | None = None,
        env: dict[str, str] | None = None,
    ) -> bool:
        """
        连接外部 MCP 服务器并加载其工具

        Args:
            command: 服务器命令
            args: 命令参数
            env: 环境变量

        Returns:
            是否成功连接
        """
        from mechforge_core.mcp.client import MCPClient

        client = MCPClient(command, args, env)
        if client.start():
            # 将外部工具添加到 LLM
            for tool in client.tools:
                tool_def = ToolDefinition(
                    name=tool.name,
                    description=tool.description,
                    parameters=tool.to_schema()["parameters"]["properties"],
                    required=tool.to_schema()["parameters"].get("required", []),
                )
                self._tools.append(tool_def)

                # 使用闭包保持 client 引用
                def make_handler(t, c):
                    return lambda **kwargs: c.call_tool(t.name, kwargs)

                self._tool_handlers[tool.name] = make_handler(tool, client)

            print(f"[MCP] 已连接服务器，加载 {len(client.tools)} 个工具")
            return True

        return False

    def call(
        self,
        user_input: str,
        context: str = "",
        stream: bool = False,
        use_tools: bool = True,
    ) -> str | Generator[str, None, None]:
        """统一调用入口

        Args:
            user_input: 用户输入
            context: 上下文信息
            stream: 是否流式输出
            use_tools: 是否启用工具调用

        Returns:
            非流式: 完整响应字符串
            流式: 字符串生成器
        """
        messages = self.provider._build_messages(user_input, context, self.conversation_history)

        tools = self._tools if use_tools and self._tools else None

        if stream:
            return self._stream_response(messages, tools)

        response = self.provider.chat(messages, tools, stream=False)

        # 处理工具调用
        if isinstance(response, LLMResponse) and response.tool_calls:
            return self._handle_tool_calls(response, messages)

        if isinstance(response, LLMResponse):
            self.conversation_history.append({"role": "user", "content": user_input})
            self.conversation_history.append({"role": "assistant", "content": response.content})
            return response.content

        return str(response)

    def _stream_response(
        self, messages: list[dict[str, str]], tools: list[ToolDefinition] | None
    ) -> Generator[str, None, None]:
        """流式响应"""
        # 流式模式暂不支持工具调用
        stream = self.provider.chat(messages, None, stream=True)
        full_content = ""

        for chunk in stream:
            full_content += chunk
            yield chunk

        self.conversation_history.append({"role": "user", "content": messages[-1]["content"]})
        self.conversation_history.append({"role": "assistant", "content": full_content})

    def _handle_tool_calls(self, response: LLMResponse, messages: list[dict[str, str]]) -> str:
        """处理工具调用"""
        tool_results = []

        for tool_call in response.tool_calls:
            handler = self._tool_handlers.get(tool_call.name)
            if handler:
                try:
                    result = handler(**tool_call.arguments)
                    tool_results.append(
                        {"tool_call_id": tool_call.id, "name": tool_call.name, "result": result}
                    )
                except Exception as e:
                    tool_results.append(
                        {
                            "tool_call_id": tool_call.id,
                            "name": tool_call.name,
                            "error": str(e),
                        }
                    )

        # 添加工具调用结果到消息
        messages.append(
            {"role": "assistant", "content": response.content, "tool_calls": response.tool_calls}
        )

        for tr in tool_results:
            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tr["tool_call_id"],
                    "content": json.dumps({"result": tr.get("result"), "error": tr.get("error")}),
                }
            )

        # 再次调用获取最终响应
        final_response = self.provider.chat(messages, None, stream=False)
        if isinstance(final_response, LLMResponse):
            return final_response.content
        return str(final_response)

    async def acall(
        self,
        user_input: str,
        context: str = "",
        stream: bool = False,
        use_tools: bool = True,
    ) -> str | AsyncGenerator[str, None]:
        """异步调用入口"""
        messages = self.provider._build_messages(user_input, context, self.conversation_history)

        tools = self._tools if use_tools and self._tools else None

        if stream:
            return self._async_stream_response(messages)

        response = await self.provider.achat(messages, tools, stream=False)

        if isinstance(response, LLMResponse) and response.tool_calls:
            # 简化处理：返回工具调用信息
            return f"[工具调用: {', '.join(t.name for t in response.tool_calls)}]"

        if isinstance(response, LLMResponse):
            self.conversation_history.append({"role": "user", "content": user_input})
            self.conversation_history.append({"role": "assistant", "content": response.content})
            return response.content

        return str(response)

    async def _async_stream_response(
        self, messages: list[dict[str, str]]
    ) -> AsyncGenerator[str, None]:
        """异步流式响应"""
        stream = await self.provider.achat(messages, None, stream=True)
        full_content = ""

        async for chunk in stream:
            full_content += chunk
            yield chunk

        self.conversation_history.append({"role": "user", "content": messages[-1]["content"]})
        self.conversation_history.append({"role": "assistant", "content": full_content})

    def get_current_model_name(self) -> str:
        """获取当前模型名称"""
        provider_type = self.config.provider.get_active_provider()
        provider_cfg = self.config.provider.get_config(provider_type)

        if provider_type == "ollama":
            try:
                resp = requests.get(f"{self.config.provider.ollama.url}/api/tags", timeout=5)
                if resp.status_code == 200:
                    models = resp.json().get("models", [])
                    if models:
                        return models[0].get("name", provider_cfg.model)
            except Exception:
                pass
            return self._model_override or provider_cfg.model

        if provider_type == "local":
            return provider_cfg.llm_model

        return provider_cfg.model

    def get_api_type(self) -> str:
        """获取 API 类型名称"""
        provider_type = self.config.provider.get_active_provider()
        provider_names = {
            "openai": "OpenAI",
            "anthropic": "Anthropic",
            "ollama": "Ollama",
            "local": "Local GGUF",
        }
        return provider_names.get(provider_type, "Ollama")
