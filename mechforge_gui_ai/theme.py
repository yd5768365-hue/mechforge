"""
GUI 主题样式 - Dark Glassmorphism 赛博朋克风格

设计特点：
- 深海军蓝渐变背景 (#0A0F1C → #121A2E)
- 玻璃态效果 (Glassmorphism)
- 淡青色霓虹强调 (#00F5FF)
- 六边形蜂窝网格纹理
"""

# Dark Glassmorphism 配色方案
THEME = {
    # 背景色 - 深海军蓝渐变
    "bg_primary": "#0A0F1C",       # 主背景（深海军蓝）
    "bg_secondary": "#121A2E",     # 次背景（稍浅海军蓝）
    "bg_tertiary": "#080C14",      # 输入区背景（更深）
    "bg_gradient_start": "#0A0F1C",  # 渐变起点
    "bg_gradient_end": "#121A2E",    # 渐变终点

    # 玻璃态效果
    "glass_bg": "rgba(18, 26, 46, 0.7)",
    "glass_border": "rgba(0, 245, 255, 0.15)",
    "glass_highlight": "rgba(0, 245, 255, 0.3)",

    # 文字颜色
    "text_primary": "#E8F0F8",     # 主文字（淡蓝白）
    "text_secondary": "#8A9BB0",   # 次文字（灰蓝）
    "text_dim": "#4A5A70",         # 暗淡文字
    "text_muted": "#6A7A90",       # 弱化文字（placeholder等）

    # 霓虹强调色
    "accent_cyan": "#00F5FF",      # 电光青（主强调）
    "accent_cyan_dim": "#00A0A8",  # 暗青色
    "accent_purple": "#A855F7",    # 霓虹紫
    "accent_pink": "#F472B6",      # 霓虹粉
    "accent_green": "#00FF88",     # 霓虹绿（成功）
    "accent_orange": "#FF8C00",    # 霓虹橙（警告）
    "accent_red": "#FF4444",       # 霓虹红（错误）

    # 网格颜色
    "grid_color": "rgba(0, 245, 255, 0.08)",  # 蜂窝网格

    # 用户角色颜色
    "user_color": "#00FF88",       # 用户消息（绿）
    "assistant_color": "#00F5FF",  # AI 消息（青）
    "system_color": "#A855F7",     # 系统消息（紫）
    "error_color": "#FF4444",      # 错误消息（红）

    # 边框
    "border_color": "rgba(0, 245, 255, 0.1)",
    "border_highlight": "rgba(0, 245, 255, 0.4)",
}

# 字体设置
FONT_FAMILY = "Consolas"  # 等宽字体
FONT_SIZE = {
    "small": 10,
    "normal": 12,
    "large": 14,
    "title": 16,
    "header": 20,
}

# 窗口设置
WINDOW = {
    "title": "MechForge AI",
    "width": 1100,
    "height": 750,
    "min_width": 900,
    "min_height": 600,
}


def get_stylesheet() -> str:
    """获取全局样式表 - Glassmorphism 风格"""
    return f"""
    /* 全局样式 */
    QWidget {{
        background-color: {THEME['bg_primary']};
        color: {THEME['text_primary']};
        font-family: "{FONT_FAMILY}";
        font-size: {FONT_SIZE['normal']}px;
    }}

    /* 主窗口 */
    QMainWindow {{
        background: qlineargradient(
            x1: 0, y1: 0, x2: 0, y2: 1,
            stop: 0 {THEME['bg_gradient_start']},
            stop: 1 {THEME['bg_gradient_end']}
        );
    }}

    /* 滚动区域 */
    QScrollArea {{
        background: transparent;
        border: none;
    }}

    /* 玻璃态面板 */
    QFrame#glassPanel {{
        background-color: {THEME['glass_bg']};
        border: 1px solid {THEME['glass_border']};
        border-radius: 12px;
    }}

    /* 文本编辑区 - 玻璃态 */
    QTextEdit, QPlainTextEdit {{
        background-color: rgba(8, 12, 20, 0.6);
        color: {THEME['text_primary']};
        border: 1px solid {THEME['border_color']};
        border-radius: 8px;
        padding: 10px;
        font-family: "{FONT_FAMILY}";
        font-size: {FONT_SIZE['normal']}px;
    }}

    QTextEdit:focus, QPlainTextEdit:focus {{
        border-color: {THEME['accent_cyan']};
        background-color: rgba(8, 12, 20, 0.8);
    }}

    /* 输入框 - 玻璃态 */
    QLineEdit {{
        background-color: rgba(8, 12, 20, 0.6);
        color: {THEME['text_primary']};
        border: 1px solid {THEME['border_color']};
        border-radius: 8px;
        padding: 10px 14px;
        font-family: "{FONT_FAMILY}";
    }}

    QLineEdit:focus {{
        border-color: {THEME['accent_cyan']};
        background-color: rgba(8, 12, 20, 0.8);
    }}

    /* 按钮 - 霓虹风格 */
    QPushButton {{
        background-color: rgba(0, 245, 255, 0.08);
        color: {THEME['text_primary']};
        border: 1px solid rgba(0, 245, 255, 0.2);
        border-radius: 8px;
        padding: 8px 16px;
        font-family: "{FONT_FAMILY}";
        font-weight: bold;
    }}

    QPushButton:hover {{
        background-color: rgba(0, 245, 255, 0.15);
        border-color: {THEME['accent_cyan']};
        color: {THEME['accent_cyan']};
    }}

    QPushButton:pressed {{
        background-color: {THEME['accent_cyan']};
        color: {THEME['bg_primary']};
    }}

    /* 主按钮 - 霓虹填充 */
    QPushButton#primaryButton {{
        background-color: rgba(0, 245, 255, 0.2);
        color: {THEME['accent_cyan']};
        border: 1px solid {THEME['accent_cyan']};
    }}

    QPushButton#primaryButton:hover {{
        background-color: rgba(0, 245, 255, 0.3);
        box-shadow: 0 0 15px rgba(0, 245, 255, 0.4);
    }}

    /* 标签 */
    QLabel {{
        background: transparent;
        color: {THEME['text_primary']};
        font-family: "{FONT_FAMILY}";
    }}

    /* 状态栏 - 玻璃态 */
    QStatusBar {{
        background-color: rgba(10, 15, 28, 0.8);
        color: {THEME['text_secondary']};
        border-top: 1px solid {THEME['border_color']};
        font-size: {FONT_SIZE['small']}px;
    }}

    /* 分隔线 */
    QFrame[frameShape="4"] {{  /* HLine */
        background-color: {THEME['border_color']};
        max-height: 1px;
    }}

    /* 进度条 - 霓虹 */
    QProgressBar {{
        background-color: rgba(8, 12, 20, 0.6);
        border: 1px solid {THEME['border_color']};
        border-radius: 4px;
        text-align: center;
        color: {THEME['text_primary']};
    }}

    QProgressBar::chunk {{
        background-color: {THEME['accent_cyan']};
        border-radius: 4px;
    }}

    /* 工具提示 - 玻璃态 */
    QToolTip {{
        background-color: rgba(18, 26, 46, 0.95);
        color: {THEME['accent_cyan']};
        border: 1px solid {THEME['accent_cyan']};
        border-radius: 6px;
        padding: 6px 10px;
        font-family: "{FONT_FAMILY}";
    }}
    """
