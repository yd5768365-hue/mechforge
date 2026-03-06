"""
MCP 服务器实现

将 MechForge 功能作为 MCP 服务器提供给外部
"""

import json
import sys
from typing import Any

from .tools import ToolRegistry, default_registry


class MCPServer:
    """
    MCP 服务器（stdio 模式）

    通过标准输入输出与客户端通信
    """

    def __init__(self, tool_registry: ToolRegistry | None = None):
        self.registry = tool_registry or default_registry
        self.initialized = False

    def run(self):
        """运行服务器（阻塞）"""
        while True:
            try:
                line = sys.stdin.readline()
                if not line:
                    break

                request = json.loads(line)
                response = self._handle_request(request)

                if response:
                    print(json.dumps(response), flush=True)

            except json.JSONDecodeError:
                self._send_error(None, -32700, "Parse error")
            except Exception as e:
                self._send_error(None, -32603, f"Internal error: {e}")

    def _handle_request(self, request: dict) -> dict | None:
        """处理请求"""
        request_id = request.get("id")
        method = request.get("method", "")
        params = request.get("params", {})

        handlers = {
            "initialize": self._handle_initialize,
            "tools/list": self._handle_tools_list,
            "tools/call": self._handle_tools_call,
        }

        handler = handlers.get(method)
        if handler:
            return handler(request_id, params)

        return self._send_error(request_id, -32601, f"Method not found: {method}")

    def _handle_initialize(self, request_id: Any, params: dict) -> dict:
        """处理初始化请求"""
        self.initialized = True

        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {}},
                "serverInfo": {"name": "mechforge-mcp-server", "version": "0.5.0"},
            },
        }

    def _handle_tools_list(self, request_id: Any, params: dict) -> dict:
        """处理工具列表请求"""
        tools = self.registry.to_schema()

        return {"jsonrpc": "2.0", "id": request_id, "result": {"tools": tools}}

    def _handle_tools_call(self, request_id: Any, params: dict) -> dict:
        """处理工具调用请求"""
        tool_name = params.get("name")
        arguments = params.get("arguments", {})

        tool = self.registry.get(tool_name)
        if not tool:
            return self._send_error(request_id, -32602, f"Tool not found: {tool_name}")

        try:
            result = tool.execute(**arguments)

            # 确保结果是字符串
            if not isinstance(result, str):
                result = json.dumps(result, ensure_ascii=False)

            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {"content": [{"type": "text", "text": result}]},
            }

        except Exception as e:
            return self._send_error(request_id, -32603, str(e))

    def _send_error(self, request_id: Any, code: int, message: str) -> dict:
        """发送错误响应"""
        return {"jsonrpc": "2.0", "id": request_id, "error": {"code": code, "message": message}}


def main():
    """MCP 服务器入口点"""
    server = MCPServer()
    server.run()


if __name__ == "__main__":
    main()
