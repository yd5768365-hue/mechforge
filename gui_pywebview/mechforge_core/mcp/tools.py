"""
MCP 工具定义和注册
"""

import json
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any, TypeVar

T = TypeVar("T")


@dataclass
class ToolParameter:
    """工具参数定义"""

    name: str
    description: str
    type: str = "string"
    required: bool = True
    default: Any = None
    enum: list[str] | None = None

    def to_schema(self) -> dict[str, Any]:
        """转换为 JSON Schema"""
        schema = {
            "type": self.type,
            "description": self.description,
        }
        if self.enum:
            schema["enum"] = self.enum
        if self.default is not None:
            schema["default"] = self.default
        return schema


@dataclass
class Tool:
    """MCP 工具定义"""

    name: str
    description: str
    parameters: list[ToolParameter] = field(default_factory=list)
    handler: Callable | None = None
    returns: str = "string"

    def to_schema(self) -> dict[str, Any]:
        """转换为 MCP 工具 Schema"""
        properties = {}
        required = []

        for param in self.parameters:
            properties[param.name] = param.to_schema()
            if param.required:
                required.append(param.name)

        return {
            "name": self.name,
            "description": self.description,
            "parameters": {
                "type": "object",
                "properties": properties,
                "required": required,
            },
        }

    def execute(self, **kwargs) -> Any:
        """执行工具"""
        if self.handler is None:
            raise RuntimeError(f"工具 {self.name} 没有处理器")

        # 验证必需参数
        for param in self.parameters:
            if param.required and param.name not in kwargs:
                if param.default is not None:
                    kwargs[param.name] = param.default
                else:
                    raise ValueError(f"缺少必需参数: {param.name}")

        return self.handler(**kwargs)


class ToolRegistry:
    """工具注册表"""

    def __init__(self):
        self._tools: dict[str, Tool] = {}

    def register(self, tool: Tool) -> Tool:
        """注册工具"""
        self._tools[tool.name] = tool
        return tool

    def unregister(self, name: str) -> bool:
        """注销工具"""
        if name in self._tools:
            del self._tools[name]
            return True
        return False

    def get(self, name: str) -> Tool | None:
        """获取工具"""
        return self._tools.get(name)

    def list_tools(self) -> list[Tool]:
        """列出所有工具"""
        return list(self._tools.values())

    def to_schema(self) -> list[dict[str, Any]]:
        """获取所有工具的 Schema"""
        return [tool.to_schema() for tool in self._tools.values()]

    def clear(self):
        """清空注册表"""
        self._tools.clear()


# 全局工具注册表
default_registry = ToolRegistry()


def tool(
    name: str | None = None,
    description: str | None = None,
    registry: ToolRegistry | None = None,
):
    """
    工具装饰器

    用法:
        @tool()
        def my_function(param1: str, param2: int = 10) -> str:
            return f"Result: {param1}, {param2}"
    """
    registry = registry or default_registry

    def decorator(func: Callable) -> Tool:
        tool_name = name or func.__name__
        tool_desc = description or func.__doc__ or f"执行 {tool_name}"

        # 自动从函数签名提取参数
        import inspect

        sig = inspect.signature(func)
        parameters = []

        for param_name, param in sig.parameters.items():
            param_type = "string"
            if param.annotation != inspect.Parameter.empty:
                if param.annotation in (int, float):
                    param_type = "number"
                elif param.annotation is bool:
                    param_type = "boolean"

            default = param.default if param.default != inspect.Parameter.empty else None

            parameters.append(
                ToolParameter(
                    name=param_name,
                    description=f"参数 {param_name}",
                    type=param_type,
                    required=param.default == inspect.Parameter.empty,
                    default=default,
                )
            )

        tool_obj = Tool(
            name=tool_name,
            description=tool_desc,
            parameters=parameters,
            handler=func,
        )

        registry.register(tool_obj)
        return tool_obj

    return decorator


# 内置工具示例
@tool(description="计算悬臂梁端部挠度")
def calculate_cantilever_deflection(
    length: float,  # mm
    force: float,  # N
    width: float = 10.0,  # mm
    height: float = 10.0,  # mm
    youngs_modulus: float = 210000.0,  # MPa (钢)
) -> str:
    """计算悬臂梁在端部受力时的最大挠度"""
    # 惯性矩 moment = b*h^3 / 12
    _moment = width * height**3 / 12

    # 挠度公式: δ = FL^3 / (3EI)
    # 注意单位转换: length 是 mm, 需要转换为 m 计算
    length_m = length / 1000
    width_m = width / 1000
    height_m = height / 1000
    moment_m4 = width_m * height_m**3 / 12
    e_pa = youngs_modulus * 1e6

    deflection_m = (force * length_m**3) / (3 * e_pa * moment_m4)
    deflection_mm = deflection_m * 1000

    return json.dumps(
        {
            "deflection_mm": round(deflection_mm, 6),
            "deflection_m": round(deflection_m, 9),
            "formula": "δ = FL³ / (3EI)",
            "inputs": {
                "length_mm": length,
                "force_N": force,
                "width_mm": width,
                "height_mm": height,
                "E_MPa": youngs_modulus,
            },
        },
        ensure_ascii=False,
    )


@tool(description="查询材料属性")
def query_material(
    name: str,
    property_type: str | None = None,
) -> str:
    """查询工程材料的力学性能"""
    materials = {
        "steel": {
            "name": "结构钢",
            "youngs_modulus_MPa": 210000,
            "poisson_ratio": 0.3,
            "density_kg_m3": 7850,
            "yield_strength_MPa": 250,
            "description": "通用结构钢，强度高，成本低",
        },
        "aluminum": {
            "name": "铝合金",
            "youngs_modulus_MPa": 70000,
            "poisson_ratio": 0.33,
            "density_kg_m3": 2700,
            "yield_strength_MPa": 150,
            "description": "轻质高强，耐腐蚀，航空常用",
        },
        "titanium": {
            "name": "钛合金",
            "youngs_modulus_MPa": 116000,
            "poisson_ratio": 0.31,
            "density_kg_m3": 4500,
            "yield_strength_MPa": 800,
            "description": "高强度重量比，生物相容性好",
        },
    }

    material = materials.get(name.lower())
    if not material:
        available = ", ".join(materials.keys())
        return json.dumps(
            {"error": f"未找到材料 '{name}'", "available": available},
            ensure_ascii=False,
        )

    if property_type:
        value = material.get(property_type)
        if value is not None:
            return json.dumps({property_type: value}, ensure_ascii=False)
        else:
            available_props = ", ".join(material.keys())
            return json.dumps(
                {
                    "error": f"属性 '{property_type}' 不存在",
                    "available_properties": available_props,
                },
                ensure_ascii=False,
            )

    return json.dumps(material, ensure_ascii=False)


@tool(description="计算圆柱螺旋弹簧刚度")
def calculate_spring_stiffness(
    wire_diameter: float,  # mm
    mean_diameter: float,  # mm
    active_coils: int,
    shear_modulus: float = 80000.0,  # MPa (钢)
) -> str:
    """计算圆柱螺旋压缩弹簧的刚度系数 k = Gd⁴ / (8D³n)"""
    # k = Gd⁴ / (8D³n)
    # 单位转换为 N/mm
    g_n_mm2 = shear_modulus  # MPa = N/mm²
    d_mm = wire_diameter
    d_mean_mm = mean_diameter
    n = active_coils

    k = (g_n_mm2 * d_mm**4) / (8 * d_mean_mm**3 * n)

    return json.dumps(
        {
            "stiffness_N_mm": round(k, 4),
            "stiffness_N_m": round(k * 1000, 2),
            "formula": "k = Gd⁴ / (8D³n)",
            "inputs": {
                "wire_diameter_mm": wire_diameter,
                "mean_diameter_mm": mean_diameter,
                "active_coils": active_coils,
                "shear_modulus_MPa": shear_modulus,
            },
        },
        ensure_ascii=False,
    )
