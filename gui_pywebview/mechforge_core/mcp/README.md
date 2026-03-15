# Model Context Protocol (MCP) 支持

MechForge 实现了 MCP (Model Context Protocol)，允许 AI 模型通过标准化的方式调用外部工具。

## 什么是 MCP?

MCP 是 Anthropic 推出的开放协议，用于标准化 AI 模型与外部数据源、工具的集成。通过 MCP，AI 可以：

- 🔧 调用工程计算工具
- 📚 查询数据库和知识库
- 📁 读写文件系统
- 🌐 访问外部 API

## 快速开始

### 1. 使用内置工具

```python
from mechforge_ai.llm_client import LLMClient
from mechforge_core.mcp.tools import default_registry

# 创建 LLM 客户端
llm = LLMClient()

# 加载 MCP 工具
llm.load_mcp_tools(default_registry)

# 现在 LLM 可以在对话中使用这些工具
response = llm.call("计算悬臂梁挠度...", stream=False)
```

### 2. 创建自定义工具

```python
from mechforge_core.mcp.tools import tool

@tool(description="计算齿轮传动比")
def calculate_gear_ratio(
    teeth_driver: int,
    teeth_driven: int,
) -> str:
    """计算齿轮传动比"""
    ratio = teeth_driven / teeth_driver
    return f"传动比: {ratio:.2f}:1"

# 工具会自动注册到 default_registry
```

### 3. 连接外部 MCP 服务器

```python
# 连接文件系统服务器
llm.connect_mcp_server(
    command="npx",
    args=["-y", "@modelcontextprotocol/server-filesystem", "/home/user/docs"]
)

# 连接数据库服务器
llm.connect_mcp_server(
    command="uvx",
    args=["mcp-server-sqlite", "--db-path", "./engineering.db"]
)
```

## 内置工具

MechForge 提供以下工程计算工具：

### 结构力学

| 工具名 | 功能 | 参数 |
|--------|------|------|
| `calculate_cantilever_deflection` | 悬臂梁挠度 | length, force, width, height, E |
| `calculate_beam_stress` | 梁弯曲应力 | M, W |
| `calculate_spring_stiffness` | 弹簧刚度 | d, D, n, G |

### 材料

| 工具名 | 功能 | 参数 |
|--------|------|------|
| `query_material` | 查询材料属性 | name, property_type |

### 单位转换

| 工具名 | 功能 | 参数 |
|--------|------|------|
| `convert_stress_units` | 应力单位转换 | value, from_unit, to_unit |
| `convert_length_units` | 长度单位转换 | value, from_unit, to_unit |

## 架构

```
mechforge_core/mcp/
├── __init__.py      # 导出主要类
├── tools.py         # 工具定义和注册
├── client.py        # MCP 客户端（连接外部服务器）
└── server.py        # MCP 服务器（对外提供服务）
```

## 作为 MCP 服务器运行

MechForge 也可以作为 MCP 服务器，为其他 AI 客户端提供工程计算工具：

```bash
# 启动 MCP 服务器（stdio 模式）
python -m mechforge_core.mcp.server

# 在 Claude Desktop 配置中使用
{
  "mcpServers": {
    "mechforge": {
      "command": "python",
      "args": ["-m", "mechforge_core.mcp.server"]
    }
  }
}
```

## 可用的外部 MCP 服务器

| 服务器 | 安装命令 | 功能 |
|--------|----------|------|
| filesystem | `npx -y @modelcontextprotocol/server-filesystem /path` | 文件系统访问 |
| github | `npx -y @modelcontextprotocol/server-github` | GitHub API |
| postgres | `npx -y @modelcontextprotocol/server-postgres` | PostgreSQL |
| sqlite | `uvx mcp-server-sqlite` | SQLite 数据库 |
| fetch | `npx -y @modelcontextprotocol/server-fetch` | HTTP 请求 |

## API 参考

### Tool 类

```python
from mechforge_core.mcp.tools import Tool, ToolParameter

# 创建工具
tool = Tool(
    name="my_tool",
    description="工具描述",
    parameters=[
        ToolParameter(name="param1", description="参数1", type="string", required=True),
        ToolParameter(name="param2", description="参数2", type="number", required=False, default=10),
    ],
    handler=my_function,
)

# 执行工具
result = tool.execute(param1="value", param2=20)
```

### ToolRegistry 类

```python
from mechforge_core.mcp.tools import ToolRegistry

# 创建注册表
registry = ToolRegistry()

# 注册工具
registry.register(tool)

# 获取工具
tool = registry.get("tool_name")

# 列出所有工具
tools = registry.list_tools()
```

### MCPClient 类

```python
from mechforge_core.mcp.client import MCPClient

# 创建客户端
client = MCPClient(
    command="npx",
    args=["-y", "@modelcontextprotocol/server-filesystem", "/path"],
)

# 启动连接
if client.start():
    # 获取工具列表
    tools = client.tools

    # 调用工具
    result = client.call_tool("read_file", {"path": "/path/to/file.txt"})

    # 停止连接
    client.stop()
```

## 示例

参见 `examples/mcp_example.py` 获取完整示例代码。

## 参考

- [MCP 官方文档](https://modelcontextprotocol.io/)
- [MCP GitHub](https://github.com/modelcontextprotocol)
