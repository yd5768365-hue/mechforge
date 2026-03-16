"""
MCP 工具单元测试
"""

import pytest

from mechforge_core.mcp.tools import (
    Tool,
    ToolParameter,
    ToolRegistry,
    tool,
)


class TestToolParameter:
    """ToolParameter 单元测试"""

    def test_to_schema_basic(self):
        """测试基本 schema 生成"""
        param = ToolParameter(
            name="length",
            description="长度值",
            type="number",
            required=True,
        )
        schema = param.to_schema()

        assert schema["type"] == "number"
        assert schema["description"] == "长度值"
        assert "default" not in schema

    def test_to_schema_with_default(self):
        """测试带默认值的 schema"""
        param = ToolParameter(
            name="unit",
            description="单位",
            type="string",
            required=False,
            default="mm",
        )
        schema = param.to_schema()

        assert schema["default"] == "mm"

    def test_to_schema_with_enum(self):
        """测试带枚举的 schema"""
        param = ToolParameter(
            name="material",
            description="材料类型",
            type="string",
            required=True,
            enum=["steel", "aluminum", "titanium"],
        )
        schema = param.to_schema()

        assert schema["enum"] == ["steel", "aluminum", "titanium"]


class TestTool:
    """Tool 单元测试"""

    def test_to_schema_single_param(self):
        """测试单个参数的 schema 生成"""
        tool_def = Tool(
            name="test_tool",
            description="测试工具",
            parameters=[
                ToolParameter(
                    name="input",
                    description="输入值",
                    type="string",
                    required=True,
                )
            ],
        )
        schema = tool_def.to_schema()

        assert schema["name"] == "test_tool"
        assert schema["description"] == "测试工具"
        assert "input" in schema["parameters"]["properties"]
        assert "input" in schema["parameters"]["required"]

    def test_to_schema_multiple_params(self):
        """测试多个参数的 schema 生成"""
        tool_def = Tool(
            name="calc",
            description="计算工具",
            parameters=[
                ToolParameter(name="a", description="第一个数", type="number", required=True),
                ToolParameter(name="b", description="第二个数", type="number", required=True),
            ],
        )
        schema = tool_def.to_schema()

        assert len(schema["parameters"]["properties"]) == 2
        assert len(schema["parameters"]["required"]) == 2

    def test_execute_with_handler(self):
        """测试工具执行"""

        def add(a: int, b: int) -> int:
            return a + b

        tool_def = Tool(
            name="add",
            description="加法工具",
            parameters=[
                ToolParameter(name="a", description="第一个数", type="integer", required=True),
                ToolParameter(name="b", description="第二个数", type="integer", required=True),
            ],
            handler=add,
        )

        result = tool_def.execute(a=1, b=2)
        assert result == 3

    def test_execute_missing_required_param(self):
        """测试缺少必需参数时抛出异常"""

        def greet(name: str) -> str:
            return f"Hello, {name}!"

        tool_def = Tool(
            name="greet",
            description="问候工具",
            parameters=[
                ToolParameter(name="name", description="姓名", type="string", required=True),
            ],
            handler=greet,
        )

        with pytest.raises(ValueError, match="缺少必需参数"):
            tool_def.execute()

    def test_execute_use_default_value(self):
        """测试使用默认值"""

        def greet(name: str, greeting: str = "Hello") -> str:
            return f"{greeting}, {name}!"

        tool_def = Tool(
            name="greet",
            description="问候工具",
            parameters=[
                ToolParameter(name="name", description="姓名", type="string", required=True),
                ToolParameter(name="greeting", description="问候语", type="string", required=False, default="Hello"),
            ],
            handler=greet,
        )

        result = tool_def.execute(name="World")
        assert result == "Hello, World!"

    def test_execute_no_handler(self):
        """测试没有处理器时抛出异常"""
        tool_def = Tool(
            name="no_handler",
            description="无处理器工具",
            parameters=[],
        )

        with pytest.raises(RuntimeError, match="没有处理器"):
            tool_def.execute()


class TestToolRegistry:
    """ToolRegistry 单元测试"""

    def test_register_and_get(self):
        """测试工具注册和获取"""
        registry = ToolRegistry()

        tool = Tool(
            name="test",
            description="测试工具",
            parameters=[],
        )

        registry.register(tool)
        retrieved = registry.get("test")

        assert retrieved is not None
        assert retrieved.name == "test"

    def test_register_duplicate(self):
        """测试重复注册会覆盖"""
        registry = ToolRegistry()

        tool1 = Tool(name="test", description="工具1", parameters=[])
        tool2 = Tool(name="test", description="工具2", parameters=[])

        registry.register(tool1)
        registry.register(tool2)

        assert registry.get("test").description == "工具2"

    def test_unregister_existing(self):
        """测试注销存在的工具"""
        registry = ToolRegistry()
        tool = Tool(name="test", description="测试", parameters=[])

        registry.register(tool)
        result = registry.unregister("test")

        assert result is True
        assert registry.get("test") is None

    def test_unregister_not_exists(self):
        """测试注销不存在的工具"""
        registry = ToolRegistry()
        result = registry.unregister("not_exists")

        assert result is False

    def test_list_tools(self):
        """测试列出所有工具"""
        registry = ToolRegistry()

        tool1 = Tool(name="tool1", description="工具1", parameters=[])
        tool2 = Tool(name="tool2", description="工具2", parameters=[])

        registry.register(tool1)
        registry.register(tool2)

        tools = registry.list_tools()
        assert len(tools) == 2

    def test_to_schema(self):
        """测试生成所有工具的 schema"""
        registry = ToolRegistry()

        tool = Tool(
            name="test",
            description="测试工具",
            parameters=[
                ToolParameter(name="param", description="参数", type="string", required=True)
            ],
        )
        registry.register(tool)

        schemas = registry.to_schema()
        assert len(schemas) == 1
        assert schemas[0]["name"] == "test"

    def test_clear(self):
        """测试清空注册表"""
        registry = ToolRegistry()

        tool = Tool(name="test", description="测试", parameters=[])
        registry.register(tool)
        registry.clear()

        assert len(registry.list_tools()) == 0


class TestToolDecorator:
    """@tool 装饰器单元测试"""

    def test_decorator_basic(self):
        """测试基本装饰器用法"""

        @tool(name="add", description="加法")
        def add(a: int, b: int) -> int:
            """两个数相加"""
            return a + b

        assert add.name == "add"
        assert add.description == "加法"
        assert add.handler is not None

    def test_decorator_execute(self):
        """测试装饰器创建的工具可以执行"""

        @tool(name="multiply", description="乘法")
        def multiply(a: int, b: int) -> int:
            """两个数相乘"""
            return a * b

        result = multiply.execute(a=3, b=4)
        assert result == 12
