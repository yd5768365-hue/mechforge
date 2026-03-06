"""
MechForge Theme - 颜色定义
"""

# 主题颜色
COLORS = {
    # 主色调
    "primary": "cyan",
    "secondary": "orange1",
    "accent": "spring_green3",
    # 文字颜色
    "text": "white",
    "dim": "dim",
    "success": "spring_green3",
    "warning": "yellow",
    "error": "red",
    "info": "cyan",
    # 状态颜色
    "enabled": "spring_green3",
    "disabled": "red",
    "active": "orange1",
    # 背景色
    "panel": "black",
    "panel_border": "dim cyan",
    # 代码颜色
    "code": "cyan",
    "code_bg": "black",
}


def get_color(name: str, default: str = "white") -> str:
    """获取颜色"""
    return COLORS.get(name, default)
