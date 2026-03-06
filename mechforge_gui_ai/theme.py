"""
GUI 主题样式 - Modern Dark Glassmorphism

设计特点：
- 深空蓝渐变背景 (#070D1A → #0F172A)
- 精致玻璃态效果 (Refined Glassmorphism)
- 星光青霓虹强调 (#22D3EE)
- 微妙网格纹理与光晕
"""

# Dark Glassmorphism 配色方案 - 深空蓝主题
THEME = {
    # 背景色 - 深空蓝渐变
    "bg_primary": "#070D1A",       # 主背景（深黑蓝）
    "bg_secondary": "#0F172A",     # 次背景（午夜蓝）
    "bg_tertiary": "#1A2740",      # 输入区背景（深空蓝）
    "bg_gradient_start": "#070D1A",  # 渐变起点（深黑蓝）
    "bg_gradient_end": "#0F172A",    # 渐变终点（午夜蓝）

    # 玻璃态效果
    "glass_bg": "rgba(15, 23, 42, 0.75)",
    "glass_border": "rgba(34, 211, 238, 0.12)",
    "glass_highlight": "rgba(34, 211, 238, 0.25)",

    # 文字颜色
    "text_primary": "#E8F4FF",     # 主文字（冷白）
    "text_secondary": "#7A92AA",   # 次文字（灰蓝）
    "text_dim": "#3D5470",         # 暗淡文字
    "text_muted": "#556070",       # 弱化文字（placeholder等）

    # 霓虹强调色
    "accent_cyan": "#22D3EE",      # 星光青（主强调，更精致）
    "accent_cyan_dim": "#0891B2",  # 暗青色
    "accent_purple": "#818CF8",    # 柔和紫（indigo-400）
    "accent_pink": "#F472B6",      # 霓虹粉
    "accent_green": "#34D399",     # 翡翠绿（更精致）
    "accent_orange": "#FB923C",    # 琥珀橙
    "accent_red": "#F87171",       # 柔和红

    # 网格颜色
    "grid_color": "rgba(34, 211, 238, 0.05)",  # 极淡网格

    # 用户角色颜色
    "user_color": "#34D399",       # 用户消息（翡翠绿）
    "assistant_color": "#22D3EE",  # AI 消息（星光青）
    "system_color": "#818CF8",     # 系统消息（柔和紫）
    "error_color": "#F87171",      # 错误消息（柔和红）

    # 边框
    "border_color": "rgba(34, 211, 238, 0.08)",
    "border_highlight": "rgba(34, 211, 238, 0.35)",
}

# 字体设置 - 科幻控制台风格
FONT_FAMILY = "JetBrains Mono"     # 终端/代码字体（打字机感）
FONT_FAMILY_UI = "Rajdhani"        # UI 按钮字体（短小精悍）
FONT_FAMILY_TITLE = "Orbitron"     # 标题字体（科幻硬朗）
FONT_FAMILY_CN = "Noto Sans SC"    # 中文字体（思源黑体）
FONT_FAMILY_TERMINAL = "Share Tech Mono"  # 终端提示文字

FONT_SIZE = {
    "tiny": 9,
    "small": 10,
    "normal": 12,
    "medium": 13,
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

# 圆角半径
RADIUS = {
    "small": 6,
    "normal": 10,
    "large": 14,
    "bubble": 18,
    "pill": 16,
}


def get_stylesheet() -> str:
    """获取全局样式表 - 精致 Glassmorphism 风格"""
    return f"""
    /* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
       全局基础样式
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */
    QWidget {{
        background-color: {THEME['bg_primary']};
        color: {THEME['text_primary']};
        font-family: "{FONT_FAMILY_UI}", "{FONT_FAMILY}";
        font-size: {FONT_SIZE['normal']}px;
        selection-background-color: rgba(34, 211, 238, 0.25);
        selection-color: {THEME['text_primary']};
    }}

    /* 主窗口 */
    QMainWindow {{
        background: qlineargradient(
            x1: 0, y1: 0, x2: 0, y2: 1,
            stop: 0 {THEME['bg_gradient_start']},
            stop: 1 {THEME['bg_gradient_end']}
        );
    }}

    /* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
       滚动区域
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */
    QScrollArea {{
        background: transparent;
        border: none;
    }}

    QScrollBar:vertical {{
        background: transparent;
        width: 4px;
        margin: 4px 0;
    }}
    QScrollBar::handle:vertical {{
        background: rgba(34, 211, 238, 0.25);
        min-height: 32px;
        border-radius: 2px;
    }}
    QScrollBar::handle:vertical:hover {{
        background: rgba(34, 211, 238, 0.55);
    }}
    QScrollBar::add-line:vertical,
    QScrollBar::sub-line:vertical {{
        height: 0px;
    }}
    QScrollBar::add-page:vertical,
    QScrollBar::sub-page:vertical {{
        background: transparent;
    }}

    QScrollBar:horizontal {{
        background: transparent;
        height: 4px;
        margin: 0 4px;
    }}
    QScrollBar::handle:horizontal {{
        background: rgba(34, 211, 238, 0.25);
        min-width: 32px;
        border-radius: 2px;
    }}
    QScrollBar::handle:horizontal:hover {{
        background: rgba(34, 211, 238, 0.55);
    }}
    QScrollBar::add-line:horizontal,
    QScrollBar::sub-line:horizontal {{
        width: 0px;
    }}

    /* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
       玻璃态面板
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */
    QFrame#glassPanel {{
        background-color: {THEME['glass_bg']};
        border: 1px solid {THEME['glass_border']};
        border-radius: {RADIUS['large']}px;
    }}

    /* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
       文本编辑区
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */
    QTextEdit, QPlainTextEdit {{
        background-color: rgba(7, 13, 26, 0.65);
        color: {THEME['text_primary']};
        border: 1px solid {THEME['border_color']};
        border-radius: {RADIUS['normal']}px;
        padding: 10px 14px;
        font-family: "{FONT_FAMILY}";
        font-size: {FONT_SIZE['normal']}px;
        line-height: 1.6;
    }}
    QTextEdit:focus, QPlainTextEdit:focus {{
        border-color: rgba(34, 211, 238, 0.35);
        background-color: rgba(7, 13, 26, 0.80);
        outline: none;
    }}

    /* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
       输入框
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */
    QLineEdit {{
        background-color: rgba(7, 13, 26, 0.65);
        color: {THEME['text_primary']};
        border: 1px solid {THEME['border_color']};
        border-radius: {RADIUS['normal']}px;
        padding: 8px 14px;
        font-family: "{FONT_FAMILY_UI}", "{FONT_FAMILY}";
        font-size: {FONT_SIZE['normal']}px;
    }}
    QLineEdit:focus {{
        border-color: rgba(34, 211, 238, 0.40);
        background-color: rgba(7, 13, 26, 0.85);
    }}
    QLineEdit::placeholder {{
        color: {THEME['text_muted']};
    }}

    /* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
       按钮
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */
    QPushButton {{
        background-color: rgba(34, 211, 238, 0.07);
        color: {THEME['text_primary']};
        border: 1px solid rgba(34, 211, 238, 0.18);
        border-radius: {RADIUS['normal']}px;
        padding: 7px 16px;
        font-family: "{FONT_FAMILY_UI}", "{FONT_FAMILY}";
        font-size: {FONT_SIZE['normal']}px;
        font-weight: 500;
    }}
    QPushButton:hover {{
        background-color: rgba(34, 211, 238, 0.14);
        border-color: rgba(34, 211, 238, 0.45);
        color: {THEME['accent_cyan']};
    }}
    QPushButton:pressed {{
        background-color: rgba(34, 211, 238, 0.25);
        border-color: {THEME['accent_cyan']};
    }}
    QPushButton:disabled {{
        background-color: rgba(34, 211, 238, 0.03);
        border-color: rgba(34, 211, 238, 0.08);
        color: {THEME['text_dim']};
    }}

    /* 主按钮 */
    QPushButton#primaryButton {{
        background-color: rgba(34, 211, 238, 0.15);
        color: {THEME['accent_cyan']};
        border: 1px solid rgba(34, 211, 238, 0.45);
        font-weight: 600;
    }}
    QPushButton#primaryButton:hover {{
        background-color: rgba(34, 211, 238, 0.25);
        border-color: {THEME['accent_cyan']};
    }}

    /* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
       标签
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */
    QLabel {{
        background: transparent;
        color: {THEME['text_primary']};
        font-family: "{FONT_FAMILY_UI}", "{FONT_FAMILY}";
    }}

    /* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
       状态栏
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */
    QStatusBar {{
        background-color: rgba(7, 13, 26, 0.90);
        color: {THEME['text_secondary']};
        border-top: 1px solid rgba(34, 211, 238, 0.10);
        font-size: {FONT_SIZE['small']}px;
        font-family: "{FONT_FAMILY}";
    }}
    QStatusBar::item {{
        border: none;
    }}

    /* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
       分隔线
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */
    QFrame[frameShape="4"] {{
        background-color: rgba(34, 211, 238, 0.08);
        max-height: 1px;
    }}

    /* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
       进度条
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */
    QProgressBar {{
        background-color: rgba(7, 13, 26, 0.70);
        border: 1px solid {THEME['border_color']};
        border-radius: 4px;
        text-align: center;
        color: {THEME['text_secondary']};
        font-size: {FONT_SIZE['tiny']}px;
    }}
    QProgressBar::chunk {{
        background: qlineargradient(
            x1: 0, y1: 0, x2: 1, y2: 0,
            stop: 0 rgba(34, 211, 238, 0.6),
            stop: 1 rgba(34, 211, 238, 1.0)
        );
        border-radius: 4px;
    }}

    /* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
       工具提示
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */
    QToolTip {{
        background-color: rgba(15, 23, 42, 0.97);
        color: {THEME['text_primary']};
        border: 1px solid rgba(34, 211, 238, 0.30);
        border-radius: {RADIUS['small']}px;
        padding: 6px 10px;
        font-family: "{FONT_FAMILY_UI}";
        font-size: {FONT_SIZE['small']}px;
    }}

    /* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
       对话框
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */
    QDialog {{
        background-color: {THEME['bg_secondary']};
        border: 1px solid rgba(34, 211, 238, 0.15);
        border-radius: {RADIUS['large']}px;
    }}

    /* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
       标签页
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */
    QTabWidget::pane {{
        background-color: rgba(7, 13, 26, 0.50);
        border: 1px solid rgba(34, 211, 238, 0.10);
        border-radius: {RADIUS['normal']}px;
        padding: 8px;
    }}
    QTabBar::tab {{
        background-color: transparent;
        color: {THEME['text_secondary']};
        border: 1px solid transparent;
        border-radius: {RADIUS['small']}px;
        padding: 6px 16px;
        margin: 2px 2px 0 2px;
        font-size: {FONT_SIZE['normal']}px;
    }}
    QTabBar::tab:selected {{
        background-color: rgba(34, 211, 238, 0.12);
        color: {THEME['accent_cyan']};
        border-color: rgba(34, 211, 238, 0.25);
    }}
    QTabBar::tab:hover:!selected {{
        background-color: rgba(34, 211, 238, 0.06);
        color: {THEME['text_primary']};
    }}

    /* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
       下拉框
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */
    QComboBox {{
        background-color: rgba(7, 13, 26, 0.70);
        color: {THEME['text_primary']};
        border: 1px solid {THEME['border_color']};
        border-radius: {RADIUS['normal']}px;
        padding: 6px 12px;
        font-family: "{FONT_FAMILY_UI}";
        min-height: 28px;
    }}
    QComboBox:hover {{
        border-color: rgba(34, 211, 238, 0.35);
    }}
    QComboBox:focus {{
        border-color: rgba(34, 211, 238, 0.45);
    }}
    QComboBox::drop-down {{
        border: none;
        width: 28px;
    }}
    QComboBox::down-arrow {{
        width: 10px;
        height: 10px;
        border-left: 2px solid rgba(34, 211, 238, 0.5);
        border-bottom: 2px solid rgba(34, 211, 238, 0.5);
        margin-right: 8px;
    }}
    QComboBox QAbstractItemView {{
        background-color: rgba(15, 23, 42, 0.97);
        color: {THEME['text_primary']};
        border: 1px solid rgba(34, 211, 238, 0.20);
        border-radius: {RADIUS['normal']}px;
        selection-background-color: rgba(34, 211, 238, 0.15);
        padding: 4px;
    }}

    /* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
       数字输入框
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */
    QSpinBox {{
        background-color: rgba(7, 13, 26, 0.70);
        color: {THEME['text_primary']};
        border: 1px solid {THEME['border_color']};
        border-radius: {RADIUS['normal']}px;
        padding: 5px 10px;
        font-family: "{FONT_FAMILY}";
    }}
    QSpinBox:focus {{
        border-color: rgba(34, 211, 238, 0.40);
    }}
    QSpinBox::up-button, QSpinBox::down-button {{
        background: transparent;
        border: none;
        width: 20px;
    }}

    /* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
       复选框
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */
    QCheckBox {{
        color: {THEME['text_primary']};
        spacing: 8px;
        font-family: "{FONT_FAMILY_UI}";
    }}
    QCheckBox::indicator {{
        width: 16px;
        height: 16px;
        border: 1px solid rgba(34, 211, 238, 0.30);
        border-radius: 4px;
        background: rgba(7, 13, 26, 0.70);
    }}
    QCheckBox::indicator:checked {{
        background-color: rgba(34, 211, 238, 0.25);
        border-color: {THEME['accent_cyan']};
        image: none;
    }}
    QCheckBox::indicator:hover {{
        border-color: rgba(34, 211, 238, 0.55);
    }}

    /* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
       表单布局
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */
    QFormLayout QLabel {{
        color: {THEME['text_secondary']};
        font-size: {FONT_SIZE['small']}px;
    }}

    /* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
       按钮盒子
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */
    QDialogButtonBox QPushButton {{
        min-width: 72px;
        min-height: 30px;
        border-radius: {RADIUS['small']}px;
    }}
    """
