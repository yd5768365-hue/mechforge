"""
MechForge Theme - Rich 样式定义
"""

# 样式定义
STYLES = {
    # 基础样式
    "banner": "cyan bold",
    "title": "orange1 bold",
    "subtitle": "dim italic",
    "prompt": "spring_green3",
    "help": "spring_green3",
    # 状态样式
    "enabled": "bold spring_green3",
    "disabled": "red",
    "warning": "yellow",
    "error": "bold red",
    # 边框样式
    "panel": "cyan",
    "panel_title": "bold orange1",
    # 表格样式
    "table_header": "bold magenta",
    "table_cell": "spring_green3",
    # 代码样式
    "code": "cyan",
    "code_block": "black on cyan",
}


def get_style(name: str, default: str = "") -> str:
    """获取样式"""
    return STYLES.get(name, default)
