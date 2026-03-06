"""
MCP 客户端实现

用于连接外部 MCP 服务器
"""

import json
import subprocess
from typing import Any

from .tools import Tool, ToolParameter


class MCPClient:
    """
    MCP 客户端

    连接到外部 MCP 服务器（stdio 或 SSE 模式）
    """

    def __init__(
        self,
        command: str,
        args: list[str] | None = None,
        env: dict[str, str] | None = None,
    ):
        self.command = command
        self.args = args or []
        self.env = env
        self.process: subprocess.Popen | None = None
        self._tools: list[Tool] = []

    def start(self) -> bool:
        """启动 MCP 服务器进程"""
        try:
            self.process = subprocess.Popen(
                [self.command] + self.args,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                env=self.env,
            )

            # 发送初始化请求
            self._send_request(
                {
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "initialize",
                    "params": {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {},
                        "clientInfo": {"name": "mechforge-mcp-client", "version": "0.5.0"},
                    },
                }
            )

            # 读取响应
            response = self._read_response()
            if response and "result" in response:
                # 获取工具列表
                self._fetch_tools()
                return True

            return False

        except Exception as e:
            print(f"MCP 客户端启动失败: {e}")
            return False

    def stop(self):
        """停止 MCP 服务器进程"""
        if self.process:
            self.process.terminate()
            self.process.wait()
            self.process = None

    def _send_request(self, request: dict):
        """发送 JSON-RPC 请求"""
        if not self.process or not self.process.stdin:
            raise RuntimeError("MCP 进程未启动")

        data = json.dumps(request) + "\n"
        self.process.stdin.write(data)
        self.process.stdin.flush()

    def _read_response(self) -> dict | None:
        """读取 JSON-RPC 响应"""
        if not self.process or not self.process.stdout:
            return None

        try:
            line = self.process.stdout.readline()
            if line:
                return json.loads(line)
        except json.JSONDecodeError:
            pass

        return None

    def _fetch_tools(self):
        """获取工具列表"""
        self._send_request({"jsonrpc": "2.0", "id": 2, "method": "tools/list"})

        response = self._read_response()
        if response and "result" in response:
            tools_data = response["result"].get("tools", [])
            self._tools = []

            for tool_data in tools_data:
                parameters = []
                schema = tool_data.get("parameters", {})
                props = schema.get("properties", {})
                required = schema.get("required", [])

                for name, prop in props.items():
                    parameters.append(
                        ToolParameter(
                            name=name,
                            description=prop.get("description", ""),
                            type=prop.get("type", "string"),
                            required=name in required,
                        )
                    )

                tool = Tool(
                    name=tool_data["name"],
                    description=tool_data.get("description", ""),
                    parameters=parameters,
                )
                self._tools.append(tool)

    @property
    def tools(self) -> list[Tool]:
        """获取可用工具列表"""
        return self._tools

    def call_tool(self, name: str, arguments: dict[str, Any]) -> Any:
        """调用工具"""
        self._send_request(
            {
                "jsonrpc": "2.0",
                "id": 3,
                "method": "tools/call",
                "params": {"name": name, "arguments": arguments},
            }
        )

        response = self._read_response()
        if response:
            if "result" in response:
                return response["result"]
            elif "error" in response:
                raise RuntimeError(f"工具调用错误: {response['error']}")

        raise RuntimeError("无响应")


class MCPClientManager:
    """MCP 客户端管理器"""

    def __init__(self):
        self.clients: dict[str, MCPClient] = {}

    def add_client(self, name: str, client: MCPClient) -> bool:
        """添加客户端"""
        if client.start():
            self.clients[name] = client
            return True
        return False

    def remove_client(self, name: str):
        """移除客户端"""
        if name in self.clients:
            self.clients[name].stop()
            del self.clients[name]

    def get_all_tools(self) -> list[Tool]:
        """获取所有客户端的工具"""
        tools = []
        for client in self.clients.values():
            tools.extend(client.tools)
        return tools

    def call_tool(self, name: str, arguments: dict[str, Any]) -> Any:
        """调用工具（在所有客户端中查找）"""
        for client in self.clients.values():
            for tool in client.tools:
                if tool.name == name:
                    return client.call_tool(name, arguments)
        raise ValueError(f"未找到工具: {name}")

    def clear(self):
        """清理所有客户端"""
        for client in self.clients.values():
            client.stop()
        self.clients.clear()
