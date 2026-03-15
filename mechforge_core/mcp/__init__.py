"""
Model Context Protocol (MCP) 实现

支持:
- MCP 客户端：连接外部 MCP 服务器
- MCP 服务器：提供 MechForge 功能给外部
- 工具调用：标准化工具定义和执行

参考: https://modelcontextprotocol.io/
"""

from .client import MCPClient
from .server import MCPServer
from .tools import Tool, ToolParameter, ToolRegistry

__all__ = ["MCPClient", "MCPServer", "Tool", "ToolParameter", "ToolRegistry"]
