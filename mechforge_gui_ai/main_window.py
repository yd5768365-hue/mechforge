"""
主窗口 - Modern Dark Glassmorphism GUI
"""

import json
import random
from pathlib import Path
from typing import TYPE_CHECKING

from PySide6.QtCore import QEvent, QThread, QUrl, Signal, Slot, QTimer, Qt
from PySide6.QtGui import QAction, QColor, QFont, QKeySequence, QTextCursor, QDesktopServices
from PySide6.QtWidgets import (
    QApplication,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPlainTextEdit,
    QProgressBar,
    QPushButton,
    QScrollArea,
    QSplitter,
    QStatusBar,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from mechforge_gui_ai.theme import (
    THEME, FONT_FAMILY, FONT_FAMILY_UI, FONT_FAMILY_TITLE, FONT_FAMILY_CN, FONT_FAMILY_TERMINAL,
    FONT_SIZE, WINDOW, get_stylesheet
)

if TYPE_CHECKING:
    from mechforge_ai.llm_client import LLMClient
    from mechforge_ai.rag_engine import RAGEngine


class APICallThread(QThread):
    """API 调用线程"""
    response_ready = Signal(str)
    error_occurred = Signal(str)
    
    def __init__(self, llm_client: "LLMClient", user_input: str, context: str = ""):
        super().__init__()
        self.llm_client = llm_client
        self.user_input = user_input
        self.context = context
    
    def run(self):
        try:
            response = self.llm_client.call(self.user_input, self.context)
            self.response_ready.emit(response)
        except Exception as e:
            self.error_occurred.emit(str(e))


class MessageWidget(QWidget):
    """消息显示组件 - 精致气泡式布局"""

    def __init__(self, role: str, content: str, parent=None):
        super().__init__(parent)
        self.role = role
        self.content = content
        self._setup_ui()

    def _setup_ui(self):
        """设置气泡式消息 UI"""
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(12, 5, 12, 5)
        main_layout.setSpacing(10)

        is_user = self.role == "user"
        is_assistant = self.role == "assistant"

        # 头像（仅 AI 消息显示在左侧）
        avatar = QLabel()
        avatar.setFixedSize(36, 36)
        avatar.setAlignment(Qt.AlignCenter)

        if is_assistant:
            avatar.setText("AI")
            avatar_font = QFont("Segoe UI", 9, QFont.Bold)
            avatar.setFont(avatar_font)
            avatar.setStyleSheet(f"""
                QLabel {{
                    background: qlineargradient(
                        x1: 0, y1: 0, x2: 1, y2: 1,
                        stop: 0 rgba(34, 211, 238, 0.22),
                        stop: 1 rgba(34, 211, 238, 0.08)
                    );
                    color: {THEME['accent_cyan']};
                    border-radius: 18px;
                    border: 1px solid rgba(34, 211, 238, 0.45);
                    font-weight: bold;
                    font-family: "Segoe UI";
                    font-size: 9px;
                    letter-spacing: 1px;
                }}
            """)
        elif is_user:
            avatar.setText("ME")
            avatar_font = QFont("Segoe UI", 9, QFont.Bold)
            avatar.setFont(avatar_font)
            avatar.setStyleSheet(f"""
                QLabel {{
                    background: qlineargradient(
                        x1: 0, y1: 0, x2: 1, y2: 1,
                        stop: 0 rgba(129, 140, 248, 0.22),
                        stop: 1 rgba(129, 140, 248, 0.08)
                    );
                    color: {THEME['accent_purple']};
                    border-radius: 18px;
                    border: 1px solid rgba(129, 140, 248, 0.45);
                    font-weight: bold;
                    font-family: "Segoe UI";
                    font-size: 9px;
                    letter-spacing: 1px;
                }}
            """)
        else:
            avatar.setText("SYS")
            avatar_font = QFont("Segoe UI", 8, QFont.Bold)
            avatar.setFont(avatar_font)
            avatar.setStyleSheet(f"""
                QLabel {{
                    background: rgba(129, 140, 248, 0.10);
                    color: {THEME['system_color']};
                    border-radius: 18px;
                    border: 1px solid rgba(129, 140, 248, 0.30);
                    font-family: "Segoe UI";
                    font-size: 8px;
                    letter-spacing: 0.5px;
                }}
            """)

        # 消息气泡容器
        bubble_container = QWidget()
        bubble_layout = QVBoxLayout(bubble_container)
        bubble_layout.setContentsMargins(0, 0, 0, 0)
        bubble_layout.setSpacing(5)
        # 限制气泡最大宽度，实现更精致的聊天布局
        if is_user:
            bubble_container.setMaximumWidth(620)
        elif is_assistant:
            bubble_container.setMaximumWidth(700)
        else:
            bubble_container.setMaximumWidth(560)

        # 角色名称
        name_label = QLabel()
        if is_user:
            name_label.setText("你")
            name_label.setAlignment(Qt.AlignRight)
            name_label.setStyleSheet(f"""
                color: rgba(129, 140, 248, 0.75);
                font-size: 10px;
                font-weight: 600;
                font-family: "Segoe UI";
                padding-right: 4px;
                letter-spacing: 0.5px;
            """)
        elif is_assistant:
            name_label.setText("MechForge AI")
            name_label.setAlignment(Qt.AlignLeft)
            name_label.setStyleSheet(f"""
                color: rgba(34, 211, 238, 0.75);
                font-size: 10px;
                font-weight: 600;
                font-family: "Segoe UI";
                padding-left: 4px;
                letter-spacing: 0.5px;
            """)
        else:
            name_label.setText("系统")
            name_label.setAlignment(Qt.AlignCenter)
            name_label.setStyleSheet(f"""
                color: rgba(129, 140, 248, 0.60);
                font-size: 10px;
                font-family: "Segoe UI";
            """)

        # 消息气泡
        bubble = QTextEdit()
        bubble.setPlainText(self.content)
        bubble.setReadOnly(True)
        bubble.setMaximumHeight(500)
        bubble.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        bubble.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        # 气泡样式
        if is_user:
            # 用户消息 - 右侧，精致紫色调
            bubble.setStyleSheet(f"""
                QTextEdit {{
                    background: qlineargradient(
                        x1: 0, y1: 0, x2: 1, y2: 1,
                        stop: 0 rgba(129, 140, 248, 0.13),
                        stop: 1 rgba(99, 102, 241, 0.06)
                    );
                    color: {THEME['text_primary']};
                    border: 1px solid rgba(129, 140, 248, 0.28);
                    border-radius: 18px;
                    border-top-right-radius: 5px;
                    padding: 12px 18px;
                    font-family: "{FONT_FAMILY}";
                    font-size: {FONT_SIZE['medium']}px;
                    line-height: 1.65;
                }}
                QScrollBar:vertical {{
                    background: transparent;
                    width: 3px;
                }}
                QScrollBar::handle:vertical {{
                    background: rgba(129, 140, 248, 0.40);
                    border-radius: 1px;
                }}
            """)
        elif is_assistant:
            # AI 消息 - 左侧，精致青色调
            bubble.setStyleSheet(f"""
                QTextEdit {{
                    background: qlineargradient(
                        x1: 0, y1: 0, x2: 1, y2: 1,
                        stop: 0 rgba(34, 211, 238, 0.10),
                        stop: 1 rgba(14, 165, 233, 0.04)
                    );
                    color: {THEME['text_primary']};
                    border: 1px solid rgba(34, 211, 238, 0.22);
                    border-radius: 18px;
                    border-top-left-radius: 5px;
                    padding: 12px 18px;
                    font-family: "{FONT_FAMILY}";
                    font-size: {FONT_SIZE['medium']}px;
                    line-height: 1.65;
                }}
                QScrollBar:vertical {{
                    background: transparent;
                    width: 3px;
                }}
                QScrollBar::handle:vertical {{
                    background: rgba(34, 211, 238, 0.35);
                    border-radius: 1px;
                }}
            """)
        else:
            # 系统消息 - 居中，精致暗色调
            bubble.setStyleSheet(f"""
                QTextEdit {{
                    background-color: rgba(129, 140, 248, 0.07);
                    color: rgba(129, 140, 248, 0.85);
                    border: 1px solid rgba(129, 140, 248, 0.18);
                    border-radius: 10px;
                    padding: 8px 16px;
                    font-family: "{FONT_FAMILY}";
                    font-size: {FONT_SIZE['small']}px;
                }}
            """)

        bubble_layout.addWidget(name_label)
        bubble_layout.addWidget(bubble)

        # 布局：AI 左对齐，用户右对齐
        if is_user:
            main_layout.addStretch()
            main_layout.addWidget(bubble_container)
            main_layout.addWidget(avatar)
        elif is_assistant:
            main_layout.addWidget(avatar)
            main_layout.addWidget(bubble_container)
            main_layout.addStretch()
        else:
            main_layout.addStretch()
            main_layout.addWidget(bubble_container)
            main_layout.addStretch()


# 随机欢迎词列表
WELCOME_MESSAGES = [
    {
        "title": "⚡ 欢迎来到 MechForge AI",
        "subtitle": "机械设计师的本地智能工作台",
        "content": "我是你的专属 MechBot，真正懂机械、敢说真话、能真算的 AI 助手。无论你是计算悬臂梁挠度、查询材料属性、检索知识库，还是进行有限元分析，我都能用可靠工具、标准公式和真实数据帮你搞定。避免幻觉，直击工程痛点！\n\n试试输入问题，比如：\"计算一个长100mm的悬臂梁挠度，截面10x10mm，受力1000N\" 或 \"分析钢材的应力分布\"。\n\n准备好了吗？MechBot 已就位 —— 请输入指令开始吧！ 🚀"
    },
    {
        "title": "🔧 机械工程智能助手已启动",
        "subtitle": "精准计算 · 标准公式 · 真实数据",
        "content": "你好！我是 MechBot，专注于机械工程领域的 AI 助手。我内置了材料力学、机械设计、有限元分析等专业工具，可以帮你解决实际工程问题。\n\n💡 你可以问我：\n• 计算齿轮模数、齿数、强度\n• 查询材料属性（弹性模量、屈服强度等）\n• 梁的挠度、应力计算\n• 轴承选型与寿命计算\n• 知识库检索（机械设计手册）\n\n输入 /help 查看所有命令。开始你的工程计算之旅吧！ ⚙️"
    },
    {
        "title": "⚙️ MechForge 系统就绪",
        "subtitle": "本地 AI + 知识库 + CAE 工作台",
        "content": "欢迎回来！MechForge 是你的全能机械设计助手。\n\n🎯 核心功能：\n• AI 对话 - 多模型支持（OpenAI/Anthropic/Ollama/GGUF）\n• 知识库检索 - RAG 技术 + 机械设计手册\n• CAE 工作台 - Gmsh 网格 + CalculiX 求解\n\n💬 示例问题：\n\"Q235钢的屈服强度是多少？\"\n\"计算简支梁中点挠度，跨度500mm，载荷2000N\"\n\"生成一个M10螺栓的网格模型\"\n\n随时输入问题，MechBot 7x24 小时在线！ 💪"
    },
    {
        "title": "🚀 机械设计 AI 助手上线",
        "subtitle": "告别幻觉，拥抱工程精度",
        "content": "你好，工程师！我是 MechBot，一个说真话、会计算、懂标准的 AI 助手。\n\n✨ 我的特点：\n• 不瞎编材料参数 - 只给标准数据\n• 不忽悠计算公式 - 展示完整推导\n• 不空谈理论 - 结合工程实践\n\n📐 试试这些：\n• \"45钢调质后的力学性能\"\n• \"设计一个减速器输入轴，功率5kW，转速1500rpm\"\n• \"/rag 启用知识库检索\"\n\n让工程计算变得简单可靠！ 🔩"
    },
    {
        "title": "💡 智能工程助手已激活",
        "subtitle": "你的私人机械设计顾问",
        "content": "欢迎来到 MechForge！我是你的 AI 工程助手 MechBot。\n\n🔍 我能帮你：\n• 材料选型与性能查询\n• 结构强度与刚度计算\n• 公差配合与工艺设计\n• 标准件选型（轴承、螺栓、键等）\n• 有限元分析前处理\n\n📝 快捷命令：\n/status - 查看系统状态\n/rag - 开关知识库检索\n/model - 配置 AI 模型\n/clear - 清空对话\n\n有什么工程问题？尽管问我！ 🎓"
    },
    {
        "title": "🔩 机械工程师的 AI 伙伴",
        "subtitle": "专业、可靠、本地化的智能助手",
        "content": "你好！MechForge 已准备就绪。我是懂机械、会计算、有依据的 MechBot。\n\n🛠️ 支持功能：\n• 力学计算（材料力学、弹性力学）\n• 机械设计（齿轮、轴、轴承、弹簧）\n• 材料数据库（金属、非金属、热处理）\n• 标准查询（GB、ISO、DIN）\n• 知识库 RAG 检索\n\n🌟 特色：本地运行，数据安全；多模型支持，灵活选择；工具调用，结果可靠。\n\n开始你的第一个工程咨询吧！ 📊"
    },
    {
        "title": "⚡ MechBot 已连接",
        "subtitle": "为机械设计而生的 AI 助手",
        "content": "欢迎！我是 MechBot，你的专业机械工程助手。\n\n📚 知识覆盖：\n• 理论力学、材料力学、流体力学\n• 机械原理、机械设计、制造工艺\n• 材料科学、热处理、表面处理\n• CAD/CAE/CAM 技术\n\n🔧 实用工具：\n• 单位换算、公式计算\n• 工程图表查询\n• 代码生成（Python/MATLAB）\n• 技术文档检索\n\n输入你的问题，或试试 /help 查看所有功能！ 🎯"
    },
    {
        "title": "🎓 工程智能助手就绪",
        "subtitle": "从理论到实践，全程陪伴",
        "content": "欢迎来到 MechForge AI！我是 MechBot，一个专注于机械工程的智能助手。\n\n💻 技术栈：\n• 本地 LLM 支持（Ollama/GGUF）\n• 云端 API 接入（OpenAI/Anthropic）\n• 向量数据库（ChromaDB）\n• 有限元引擎（Gmsh + CalculiX）\n\n🎯 使用场景：\n• 学生：课程作业辅助、概念讲解\n• 工程师：设计计算、标准查询\n• 研究人员：文献检索、代码生成\n\n无论你是谁，我都能提供专业帮助！ 🌟"
    }
]


class ChatArea(QWidget):
    """聊天显示区域 - 深空蓝背景 + 精致网格"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._typing_timer = None
        self._welcome_widget = None
        self._current_welcome = None
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # 设置纯色背景（通过 paintEvent 绘制）
        self.setStyleSheet(f"background-color: {THEME['bg_primary']};")

        # 滚动区域
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scroll_area.setFrameShape(QFrame.NoFrame)

        # 精致滚动条
        self.scroll_area.setStyleSheet(f"""
            QScrollArea {{
                background: transparent;
                border: none;
            }}
            QScrollBar:vertical {{
                background: transparent;
                width: 4px;
                margin: 6px 2px;
            }}
            QScrollBar::handle:vertical {{
                background: rgba(34, 211, 238, 0.22);
                min-height: 32px;
                border-radius: 2px;
            }}
            QScrollBar::handle:vertical:hover {{
                background: rgba(34, 211, 238, 0.50);
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0px;
            }}
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
                background: transparent;
            }}
        """)

        # 消息容器
        self.message_container = QWidget()
        self.message_container.setStyleSheet("background: transparent;")
        self.message_layout = QVBoxLayout(self.message_container)
        self.message_layout.setAlignment(Qt.AlignTop)
        self.message_layout.setSpacing(2)
        self.message_layout.setContentsMargins(20, 20, 20, 20)

        self.scroll_area.setWidget(self.message_container)
        layout.addWidget(self.scroll_area)

        # 显示打字机动画欢迎语
        self._show_typing_welcome()

    def _show_typing_welcome(self):
        """显示欢迎语 - 使用 QTextEdit 确保多行文本清晰显示"""
        # 随机选择一条欢迎词
        self._current_welcome = random.choice(WELCOME_MESSAGES)

        self._welcome_widget = QWidget()
        welcome_layout = QVBoxLayout(self._welcome_widget)
        welcome_layout.setAlignment(Qt.AlignCenter)
        welcome_layout.setSpacing(12)
        welcome_layout.setContentsMargins(40, 60, 40, 60)

        # 主标题 - 使用科幻标题字体
        title = QLabel(self._current_welcome["title"])
        title.setAlignment(Qt.AlignCenter)
        title_font = QFont(FONT_FAMILY_TITLE, 22, QFont.Bold)
        title.setFont(title_font)
        title.setStyleSheet(f"""
            color: {THEME['accent_cyan']};
            background: transparent;
            padding: 0 20px;
            letter-spacing: 1px;
        """)

        # 副标题 - 使用中文科技字体
        subtitle = QLabel(self._current_welcome["subtitle"])
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle_font = QFont(FONT_FAMILY_CN, 11)
        subtitle.setFont(subtitle_font)
        subtitle.setStyleSheet(f"""
            color: {THEME['accent_purple']};
            background: transparent;
            padding: 0 20px;
        """)

        # 内容区域 - 使用 QTextEdit 确保长文本清晰显示
        content = QTextEdit()
        content.setReadOnly(True)
        content.setPlainText(self._current_welcome["content"])
        content.setMaximumWidth(580)
        content.setMinimumHeight(180)
        content.setMaximumHeight(350)
        content.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        content.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        content.setStyleSheet(f"""
            QTextEdit {{
                background: rgba(15, 23, 42, 0.60);
                color: {THEME['text_primary']};
                border: 1px solid rgba(34, 211, 238, 0.20);
                border-radius: 12px;
                padding: 16px 20px;
                font-family: "{FONT_FAMILY_TERMINAL}";
                font-size: {FONT_SIZE['normal']}px;
                line-height: 1.6;
            }}
            QScrollBar:vertical {{
                background: transparent;
                width: 4px;
                margin: 4px;
            }}
            QScrollBar::handle:vertical {{
                background: rgba(34, 211, 238, 0.30);
                border-radius: 2px;
                min-height: 30px;
            }}
        """)

        welcome_layout.addWidget(title)
        welcome_layout.addWidget(subtitle)
        welcome_layout.addWidget(content)

        self.message_layout.addWidget(self._welcome_widget)

    def _fade_out_welcome(self):
        """渐隐欢迎语"""
        if self._welcome_widget:
            # 创建透明度动画
            from PySide6.QtCore import QPropertyAnimation
            from PySide6.QtWidgets import QGraphicsOpacityEffect

            opacity_effect = QGraphicsOpacityEffect(self._welcome_widget)
            self._welcome_widget.setGraphicsEffect(opacity_effect)

            self._fade_anim = QPropertyAnimation(opacity_effect, b"opacity")
            self._fade_anim.setDuration(1000)
            self._fade_anim.setStartValue(1.0)
            self._fade_anim.setEndValue(0.0)
            self._fade_anim.finished.connect(self._remove_welcome)
            self._fade_anim.start()

    def _remove_welcome(self):
        """移除欢迎语"""
        if self._welcome_widget:
            self._welcome_widget.deleteLater()
            self._welcome_widget = None
            self._welcome_title = None
            self._welcome_subtitle = None
            self._welcome_content = None

    def add_message(self, role: str, content: str):
        """添加消息"""
        # 不显示系统消息
        if role == "system":
            return

        msg_widget = MessageWidget(role, content)
        self.message_layout.addWidget(msg_widget)

        # 滚动到底部
        QTimer.singleShot(100, self._scroll_to_bottom)

    def _scroll_to_bottom(self):
        """滚动到底部"""
        scrollbar = self.scroll_area.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def clear_messages(self):
        """清空消息"""
        while self.message_layout.count():
            item = self.message_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        # 重新显示欢迎语
        self._show_typing_welcome()

    def paintEvent(self, event):
        """绘制深空蓝背景 + 精致网格线"""
        from PySide6.QtGui import QPainter, QPen, QColor, QLinearGradient
        from PySide6.QtCore import QPointF

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # 深空蓝渐变背景（更精致的色调）
        gradient = QLinearGradient(0, 0, 0, self.height())
        gradient.setColorAt(0, QColor("#070D1A"))
        gradient.setColorAt(0.45, QColor("#0A1221"))
        gradient.setColorAt(1, QColor("#0F172A"))
        painter.fillRect(self.rect(), gradient)

        # 微妙的径向中心光晕
        from PySide6.QtGui import QRadialGradient
        center_gradient = QRadialGradient(
            self.width() / 2, self.height() / 2,
            max(self.width(), self.height()) * 0.75
        )
        center_gradient.setColorAt(0, QColor(34, 130, 180, 10))
        center_gradient.setColorAt(0.5, QColor(20, 80, 120, 4))
        center_gradient.setColorAt(1, QColor(0, 0, 0, 0))
        painter.fillRect(self.rect(), center_gradient)

        # 绘制极淡网格线（更克制、更现代）
        grid_spacing = 44
        line_opacity = 14  # 大幅降低不透明度

        from PySide6.QtGui import QBrush

        for i in range(-1, int(self.width() / grid_spacing) + 2):
            x = i * grid_spacing
            center_x = self.width() / 2
            dist_from_center = abs(x - center_x) / max(self.width() / 2, 1)
            opacity = int(line_opacity * (1 - dist_from_center * 0.75))
            if opacity <= 0:
                continue

            line_gradient = QLinearGradient(x, 0, x, self.height())
            line_gradient.setColorAt(0, QColor(34, 211, 238, 0))
            line_gradient.setColorAt(0.25, QColor(34, 211, 238, opacity))
            line_gradient.setColorAt(0.75, QColor(34, 211, 238, opacity))
            line_gradient.setColorAt(1, QColor(34, 211, 238, 0))

            pen = QPen(QBrush(line_gradient), 1)
            painter.setPen(pen)
            painter.drawLine(int(x), 0, int(x), self.height())

        for i in range(-1, int(self.height() / grid_spacing) + 2):
            y = i * grid_spacing
            center_y = self.height() / 2
            dist_from_center = abs(y - center_y) / max(self.height() / 2, 1)
            opacity = int(line_opacity * (1 - dist_from_center * 0.75))
            if opacity <= 0:
                continue

            line_gradient = QLinearGradient(0, y, self.width(), y)
            line_gradient.setColorAt(0, QColor(34, 211, 238, 0))
            line_gradient.setColorAt(0.25, QColor(34, 211, 238, opacity))
            line_gradient.setColorAt(0.75, QColor(34, 211, 238, opacity))
            line_gradient.setColorAt(1, QColor(34, 211, 238, 0))

            pen = QPen(QBrush(line_gradient), 1)
            painter.setPen(pen)
            painter.drawLine(0, int(y), self.width(), int(y))

        # 仅在中心区域绘制极淡交叉点（更克制）
        painter.setPen(Qt.NoPen)
        for i in range(0, int(self.width() / grid_spacing) + 1):
            for j in range(0, int(self.height() / grid_spacing) + 1):
                x = i * grid_spacing
                y = j * grid_spacing
                center_x, center_y = self.width() / 2, self.height() / 2
                dist = ((x - center_x) ** 2 + (y - center_y) ** 2) ** 0.5
                max_dist = ((center_x) ** 2 + (center_y) ** 2) ** 0.5
                intensity = max(0, 1 - dist / max_dist)

                if intensity > 0.45:
                    dot_size = 1.5 + intensity * 1.5
                    dot_color = QColor(34, 211, 238, int(22 * intensity))
                    painter.setBrush(dot_color)
                    painter.drawEllipse(
                        QPointF(x - dot_size/2, y - dot_size/2),
                        dot_size, dot_size
                    )

        painter.end()


class InputArea(QWidget):
    """输入区域"""
    
    message_sent = Signal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._history: list[str] = []
        self._history_index = -1
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 10, 16, 14)
        layout.setSpacing(0)

        # 精致玻璃态输入容器
        input_container = QWidget()
        input_container.setMinimumHeight(50)
        input_container.setStyleSheet(f"""
            QWidget {{
                background: qlineargradient(
                    x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 rgba(22, 33, 55, 0.75),
                    stop: 1 rgba(15, 23, 42, 0.85)
                );
                border: 1px solid rgba(34, 211, 238, 0.18);
                border-bottom: 1px solid rgba(34, 211, 238, 0.25);
                border-radius: 14px;
            }}
        """)
        container_layout = QHBoxLayout(input_container)
        container_layout.setContentsMargins(14, 10, 10, 10)
        container_layout.setSpacing(10)

        # 提示符 - 更精致
        prompt_label = QLabel(">_")
        prompt_label.setStyleSheet(f"""
            color: rgba(34, 211, 238, 0.65);
            font-weight: bold;
            font-size: 13px;
            font-family: "{FONT_FAMILY}";
            background: transparent;
            letter-spacing: -1px;
        """)
        prompt_label.setFixedWidth(24)

        # 输入框 - 透明无边框
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("输入消息或 /命令...")
        self.input_field.returnPressed.connect(self._on_send)
        self.input_field.installEventFilter(self)
        self.input_field.setStyleSheet(f"""
            QLineEdit {{
                background: transparent;
                color: {THEME['text_primary']};
                border: none;
                font-family: "{FONT_FAMILY}";
                font-size: {FONT_SIZE['medium']}px;
                padding: 2px 4px;
            }}
            QLineEdit[text=""] {{
                color: {THEME['text_muted']};
            }}
        """)

        # 发送按钮 - 渐变精致风格
        self.send_button = QPushButton("发 送")
        self.send_button.setFixedSize(68, 34)
        self.send_button.setStyleSheet(f"""
            QPushButton {{
                background: qlineargradient(
                    x1: 0, y1: 0, x2: 1, y2: 1,
                    stop: 0 rgba(34, 211, 238, 0.20),
                    stop: 1 rgba(14, 165, 233, 0.12)
                );
                color: {THEME['accent_cyan']};
                border: 1px solid rgba(34, 211, 238, 0.35);
                border-radius: 10px;
                font-family: "{FONT_FAMILY_UI}";
                font-size: 12px;
                font-weight: 600;
                letter-spacing: 2px;
            }}
            QPushButton:hover {{
                background: qlineargradient(
                    x1: 0, y1: 0, x2: 1, y2: 1,
                    stop: 0 rgba(34, 211, 238, 0.32),
                    stop: 1 rgba(14, 165, 233, 0.20)
                );
                border-color: rgba(34, 211, 238, 0.65);
                color: #FFFFFF;
            }}
            QPushButton:pressed {{
                background: rgba(34, 211, 238, 0.45);
                color: {THEME['bg_primary']};
            }}
            QPushButton:disabled {{
                background: rgba(34, 211, 238, 0.05);
                border-color: rgba(34, 211, 238, 0.10);
                color: rgba(34, 211, 238, 0.25);
            }}
        """)
        self.send_button.clicked.connect(self._on_send)

        container_layout.addWidget(prompt_label)
        container_layout.addWidget(self.input_field, stretch=1)
        container_layout.addWidget(self.send_button)

        layout.addWidget(input_container)
    
    def eventFilter(self, obj, event):
        """事件过滤器 - 处理上下键历史记录"""
        if obj == self.input_field and event.type() == QEvent.KeyPress:
            if event.key() == Qt.Key_Up:
                self._navigate_history(-1)
                return True
            elif event.key() == Qt.Key_Down:
                self._navigate_history(1)
                return True
        return super().eventFilter(obj, event)
    
    def _navigate_history(self, direction: int):
        """导航历史记录"""
        if not self._history:
            return
        
        self._history_index += direction
        self._history_index = max(-1, min(self._history_index, len(self._history) - 1))
        
        if self._history_index == -1:
            self.input_field.clear()
        else:
            self.input_field.setText(self._history[-(self._history_index + 1)])
    
    def _on_send(self):
        """发送消息"""
        text = self.input_field.text().strip()
        if text:
            self._history.append(text)
            self._history_index = -1
            self.input_field.clear()
            self.message_sent.emit(text)
    
    def _on_clear(self):
        """清空输入"""
        self.input_field.clear()
    
    def set_enabled(self, enabled: bool):
        """设置启用状态"""
        self.input_field.setEnabled(enabled)
        self.send_button.setEnabled(enabled)


class MainWindow(QMainWindow):
    """主窗口"""
    
    def __init__(self):
        super().__init__()
        
        # 状态
        self.conversation_history: list[dict] = []
        self.command_history: list[str] = []
        self.rag_enabled = False
        self._api_thread: APICallThread | None = None
        
        # 延迟加载的模块
        self._llm_client: "LLMClient | None" = None
        self._rag_engine: "RAGEngine | None" = None
        self._config = None
        
        self._setup_ui()
        self._setup_statusbar()
        self._load_history()
        
        # 延迟初始化核心模块
        QTimer.singleShot(100, self._init_core_modules)
    
    def _setup_ui(self):
        """设置 UI"""
        self.setWindowTitle(WINDOW["title"])
        self.setMinimumSize(WINDOW["min_width"], WINDOW["min_height"])
        self.resize(WINDOW["width"], WINDOW["height"])
        
        # 应用样式
        self.setStyleSheet(get_stylesheet())
        
        # 中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Banner 区域
        self._create_banner(layout)
        
        # 聊天区域
        self.chat_area = ChatArea()
        layout.addWidget(self.chat_area, 1)
        
        # 分隔线
        separator = QWidget()
        separator.setFixedHeight(1)
        separator.setStyleSheet(f"background-color: {THEME['border_color']};")
        layout.addWidget(separator)
        
        # 输入区域
        self.input_area = InputArea()
        self.input_area.message_sent.connect(self._on_message_sent)
        layout.addWidget(self.input_area)
    
    def _create_banner(self, parent_layout):
        """创建标题栏 - Dark Glassmorphism 玻璃态设计"""
        banner = QWidget()
        banner.setFixedHeight(58)
        # 精致玻璃态 Banner
        banner.setStyleSheet(f"""
            QWidget {{
                background: qlineargradient(
                    x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 rgba(22, 33, 62, 0.92),
                    stop: 0.6 rgba(15, 23, 42, 0.88),
                    stop: 1 rgba(12, 18, 34, 0.85)
                );
                border-bottom: 1px solid rgba(34, 211, 238, 0.18);
            }}
        """)

        banner_layout = QHBoxLayout(banner)
        banner_layout.setContentsMargins(18, 0, 16, 0)
        banner_layout.setSpacing(0)

        # 左侧：Logo + 标题 + 版本
        logo_widget = QWidget()
        logo_layout = QHBoxLayout(logo_widget)
        logo_layout.setContentsMargins(0, 0, 0, 0)
        logo_layout.setSpacing(10)

        # Logo 图标 - 精致齿轮
        logo_icon = QLabel("⚙")
        logo_icon_font = QFont("Segoe UI Emoji", 17)
        logo_icon.setFont(logo_icon_font)
        logo_icon.setStyleSheet(f"""
            color: {THEME['accent_cyan']};
            background: transparent;
        """)
        logo_icon.setFixedSize(26, 26)
        logo_icon.setAlignment(Qt.AlignCenter)

        # 标题 + 副标题 竖排
        title_group = QWidget()
        title_group_layout = QVBoxLayout(title_group)
        title_group_layout.setContentsMargins(0, 0, 0, 0)
        title_group_layout.setSpacing(0)

        title_label = QLabel("MechForge AI")
        title_font = QFont(FONT_FAMILY_TITLE, 14, QFont.Bold)
        title_label.setFont(title_font)
        title_label.setStyleSheet(f"""
            color: {THEME['text_primary']};
            background: transparent;
            letter-spacing: 1px;
        """)

        subtitle_label = QLabel("机械设计智能助手")
        subtitle_font = QFont(FONT_FAMILY_CN, 9)
        subtitle_label.setFont(subtitle_font)
        subtitle_label.setStyleSheet(f"""
            color: rgba(34, 211, 238, 0.55);
            background: transparent;
            letter-spacing: 1px;
        """)

        title_group_layout.addWidget(title_label)
        title_group_layout.addWidget(subtitle_label)

        logo_layout.addWidget(logo_icon)
        logo_layout.addWidget(title_group)

        # 右侧：工具栏按钮
        toolbar_widget = QWidget()
        toolbar_layout = QHBoxLayout(toolbar_widget)
        toolbar_layout.setContentsMargins(0, 0, 0, 0)
        toolbar_layout.setSpacing(6)
        toolbar_layout.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

        # 创建胶囊按钮
        self._create_pill_button(toolbar_layout, "＋  新建", "新建会话 (Ctrl+N)", self._new_session)
        self._create_pill_button(toolbar_layout, "⌫  清空", "清空对话 (Ctrl+L)", self._clear_conversation)
        self._create_pill_button(toolbar_layout, "  RAG", "开关知识库 (Ctrl+R)", self._toggle_rag)
        self._create_pill_button(toolbar_layout, "?  帮助", "查看帮助", self._show_help)
        self._create_pill_button(toolbar_layout, "×  退出", "退出程序", self.close, is_danger=True)

        banner_layout.addWidget(logo_widget, stretch=1)
        banner_layout.addWidget(toolbar_widget)

        parent_layout.addWidget(banner)

    def _create_pill_button(self, layout, text, tooltip, callback, is_danger=False):
        """创建胶囊按钮 - 精致现代风格"""
        btn = QPushButton(text)
        btn.setCursor(Qt.PointingHandCursor)
        btn.setToolTip(tooltip)
        btn.setFixedHeight(30)
        btn.setMinimumWidth(68)

        # 颜色配置
        if is_danger:
            bg_normal  = "rgba(248, 113, 113, 0.07)"
            bg_hover   = "rgba(248, 113, 113, 0.16)"
            bg_pressed = "rgba(248, 113, 113, 0.35)"
            border_n   = "rgba(248, 113, 113, 0.25)"
            border_h   = "rgba(248, 113, 113, 0.55)"
            text_color = "#F87171"
        else:
            bg_normal  = "rgba(34, 211, 238, 0.06)"
            bg_hover   = "rgba(34, 211, 238, 0.14)"
            bg_pressed = "rgba(34, 211, 238, 0.28)"
            border_n   = "rgba(34, 211, 238, 0.18)"
            border_h   = "rgba(34, 211, 238, 0.50)"
            text_color = "rgba(34, 211, 238, 0.90)"

        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {bg_normal};
                color: {text_color};
                border: 1px solid {border_n};
                border-radius: 15px;
                font-size: 12px;
                font-family: "{FONT_FAMILY_UI}";
                font-weight: 600;
                padding: 0 14px;
                letter-spacing: 0.5px;
            }}
            QPushButton:hover {{
                background-color: {bg_hover};
                border-color: {border_h};
                color: {'#FFFFFF' if not is_danger else '#FCA5A5'};
            }}
            QPushButton:pressed {{
                background-color: {bg_pressed};
                border-color: {border_h};
            }}
        """)

        btn.clicked.connect(callback)
        layout.addWidget(btn)

    def _setup_statusbar(self):
        """设置状态栏 - 精致 Chip 指示器风格"""
        self.statusbar = QStatusBar()
        self.statusbar.setFixedHeight(30)
        self.statusbar.setStyleSheet(f"""
            QStatusBar {{
                background: rgba(7, 13, 26, 0.95);
                color: {THEME['text_secondary']};
                border-top: 1px solid rgba(34, 211, 238, 0.10);
                font-size: {FONT_SIZE['small']}px;
                font-family: "{FONT_FAMILY}";
                padding: 0 8px;
            }}
            QStatusBar::item {{
                border: none;
            }}
        """)
        self.setStatusBar(self.statusbar)

        # 通用 chip 样式生成函数
        def make_chip(label_text, dot_color, text_color=None):
            container = QWidget()
            container.setStyleSheet("background: transparent;")
            h = QHBoxLayout(container)
            h.setContentsMargins(8, 3, 8, 3)
            h.setSpacing(5)
            container.setFixedHeight(22)

            dot = QLabel("●")
            dot.setStyleSheet(f"""
                color: {dot_color};
                font-size: 7px;
                background: transparent;
            """)

            lbl = QLabel(label_text)
            lbl.setStyleSheet(f"""
                color: {text_color or THEME['text_secondary']};
                font-size: 10px;
                font-family: "{FONT_FAMILY}";
                background: transparent;
            """)

            h.addWidget(dot)
            h.addWidget(lbl)
            return container, lbl, dot

        # API 指示器
        api_chip, self.api_label, self.api_indicator = make_chip(
            "API: --", "#334155", THEME['text_secondary'])

        # 模型指示器
        model_chip, self.model_label, self.model_indicator = make_chip(
            "模型: --", "#334155", THEME['text_secondary'])

        # RAG 指示器
        rag_chip, self.rag_label, self.rag_indicator = make_chip(
            "RAG: OFF", "#334155", THEME['text_dim'])
        self._rag_chip = rag_chip

        # 消息计数
        msg_chip, self.msg_label, _ = make_chip(
            "消息: 0", "rgba(34,211,238,0.25)", THEME['text_secondary'])

        # 分隔
        def sep():
            s = QLabel("·")
            s.setStyleSheet(f"color: rgba(34,211,238,0.15); font-size: 14px; background: transparent;")
            return s

        self.statusbar.addWidget(api_chip)
        self.statusbar.addWidget(sep())
        self.statusbar.addWidget(model_chip)
        self.statusbar.addWidget(sep())
        self.statusbar.addWidget(rag_chip)
        self.statusbar.addWidget(sep())
        self.statusbar.addWidget(msg_chip)
    
    def _init_core_modules(self):
        """初始化核心模块"""
        try:
            from mechforge_core.config import get_config
            from mechforge_ai.llm_client import LLMClient
            
            self._config = get_config()
            self._llm_client = LLMClient()
            self._llm_client.conversation_history = self.conversation_history
            
            # 更新状态栏
            self._update_status()
            
            # 显示欢迎消息
            self.chat_area.add_message("system", "欢迎使用 MechForge AI！输入 /help 查看可用命令。")
            
        except Exception as e:
            self.chat_area.add_message("error", f"初始化失败: {e}")
    
    def _update_status(self):
        """更新状态栏"""
        if self._llm_client:
            api_type = self._llm_client.get_api_type()
            model_name = self._llm_client.get_current_model_name()
            
            self.api_label.setText(f"API: {api_type}")
            self.api_indicator.setStyleSheet(
                f"color: {THEME['accent_green']}; font-size: 7px; background: transparent;"
            )
            self.model_label.setText(f"模型: {model_name}")
            self.model_indicator.setStyleSheet(
                f"color: {THEME['accent_cyan']}; font-size: 7px; background: transparent;"
            )
        
        if self.rag_enabled:
            rag_color = THEME['accent_green']
            rag_text_color = THEME['accent_green']
        else:
            rag_color = "#334155"
            rag_text_color = THEME['text_dim']
        
        self.rag_label.setText(f"RAG: {'ON' if self.rag_enabled else 'OFF'}")
        self.rag_label.setStyleSheet(
            f"color: {rag_text_color}; font-size: 10px; font-family: '{FONT_FAMILY}'; background: transparent;"
        )
        self.rag_indicator.setStyleSheet(
            f"color: {rag_color}; font-size: 7px; background: transparent;"
        )
        
        self.msg_label.setText(f"消息: {len(self.conversation_history)}")
    
    @property
    def rag_engine(self) -> "RAGEngine | None":
        """延迟加载 RAG 引擎"""
        if self._rag_engine is None and self._config:
            try:
                from mechforge_ai.rag_engine import RAGEngine
                from pathlib import Path
                
                knowledge_path = Path(self._config.knowledge.path)
                if knowledge_path.exists() and list(knowledge_path.glob("*.md")):
                    self._rag_engine = RAGEngine(
                        knowledge_path=knowledge_path,
                        top_k=self._config.knowledge.rag.top_k
                    )
            except Exception:
                pass
        return self._rag_engine
    
    def _on_message_sent(self, text: str):
        """处理消息发送"""
        # 命令处理
        if text.startswith("/"):
            self._handle_command(text)
            return
        
        # 添加用户消息
        self.chat_area.add_message("user", text)
        self.conversation_history.append({"role": "user", "content": text})
        
        # 调用 API
        self._call_api(text)
    
    def _handle_command(self, command: str):
        """处理命令"""
        cmd = command.lower().strip()
        
        if cmd in ["/help", "/h"]:
            self._show_help()
        elif cmd == "/status":
            self._show_status()
        elif cmd == "/info":
            self._show_info()
        elif cmd == "/rag":
            self._toggle_rag()
        elif cmd == "/clear":
            self._clear_conversation()
        elif cmd == "/history":
            self._show_history()
        elif cmd == "/model":
            self._show_model_config()
        elif cmd in ["/exit", "/quit", "/q"]:
            self.close()
        else:
            self.chat_area.add_message("system", f"未知命令: {command}\n输入 /help 查看可用命令。")
    
    def _call_api(self, user_input: str):
        """调用 API"""
        if not self._llm_client:
            self.chat_area.add_message("error", "LLM 客户端未初始化")
            return
        
        # 禁用输入
        self.input_area.set_enabled(False)
        
        # 检查 RAG
        context = ""
        use_rag = self.rag_enabled
        if use_rag and self.rag_engine and self.rag_engine.is_available:
            self.chat_area.add_message("system", "📚 正在检索知识库...")
            context = self.rag_engine.search(user_input)
        
        # 显示思考状态
        self.statusbar.showMessage("⚙️ 思考中...", 0)
        
        # 启动 API 调用线程
        self._api_thread = APICallThread(self._llm_client, user_input, context)
        self._api_thread.response_ready.connect(self._on_response_ready)
        self._api_thread.error_occurred.connect(self._on_error)
        self._api_thread.start()
    
    @Slot(str)
    def _on_response_ready(self, response: str):
        """响应就绪"""
        self.chat_area.add_message("assistant", response)
        self.conversation_history.append({"role": "assistant", "content": response})
        
        self.input_area.set_enabled(True)
        self.statusbar.clearMessage()
        self._update_status()
        self._save_history()
    
    @Slot(str)
    def _on_error(self, error: str):
        """错误处理"""
        self.chat_area.add_message("error", f"错误: {error}")
        self.input_area.set_enabled(True)
        self.statusbar.clearMessage()
    
    def _show_help(self):
        """显示帮助"""
        help_text = """
可用命令:
  /help, /h    显示帮助
  /status      查看系统状态
  /info        显示会话信息
  /rag         开关 RAG 知识库检索
  /history     查看对话历史
  /clear       清除对话历史
  /model       配置 AI 模型
  /exit        退出程序

快捷键:
  Ctrl+N       新建会话
  Ctrl+L       清空对话
  Ctrl+M       模型配置
  Ctrl+R       切换 RAG
  ↑/↓          历史记录导航
  Enter        发送消息
"""
        self.chat_area.add_message("system", help_text)
    
    def _show_status(self):
        """显示状态"""
        if not self._llm_client:
            self.chat_area.add_message("system", "系统未初始化")
            return
        
        api_type = self._llm_client.get_api_type()
        model_name = self._llm_client.get_current_model_name()
        
        kb_status = "未配置"
        if self.rag_engine and self.rag_engine.is_available:
            kb_status = str(self.rag_engine.knowledge_path)
        
        status_text = f"""
系统状态:
  API 类型: {api_type}
  当前模型: {model_name}
  RAG 状态: {'启用' if self.rag_enabled else '禁用'}
  知识库: {kb_status}
  消息数: {len(self.conversation_history)}
"""
        self.chat_area.add_message("system", status_text)
    
    def _show_info(self):
        """显示会话信息"""
        info_text = f"""
会话信息:
  对话轮数: {len(self.conversation_history) // 2}
  消息数: {len(self.conversation_history)}
  命令历史: {len(self.command_history)}
  RAG: {'启用' if self.rag_enabled else '禁用'}
"""
        self.chat_area.add_message("system", info_text)
    
    def _toggle_rag(self):
        """切换 RAG - 检查知识库模块并让用户选择路径"""
        # 首先检查知识库模块是否安装
        if not self._check_knowledge_module():
            return

        # 检查知识库路径是否存在
        from mechforge_core.config import find_knowledge_path
        kb_path = find_knowledge_path()

        # 如果没有找到知识库，让用户选择
        if not kb_path or not kb_path.exists() or not self._has_documents(kb_path):
            kb_path = self._select_knowledge_folder()
            if not kb_path:
                return  # 用户取消了选择

        # 切换 RAG 状态
        self.rag_enabled = not self.rag_enabled
        status = "启用" if self.rag_enabled else "禁用"

        # 在状态栏显示提示
        self.statusbar.showMessage(f"RAG 已{status} | 知识库: {kb_path}", 5000)
        self._update_status()

    def _has_documents(self, path: Path) -> bool:
        """检查路径是否包含文档文件"""
        if not path or not path.exists():
            return False
        return bool(list(path.glob("*.md")) or list(path.glob("*.txt")))

    def _select_knowledge_folder(self) -> Path | None:
        """让用户选择知识库文件夹"""
        from PySide6.QtWidgets import QFileDialog

        # 显示信息提示
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("选择知识库文件夹")
        msg_box.setIcon(QMessageBox.Question)
        msg_box.setText("请选择知识库文件夹")
        msg_box.setInformativeText(
            "知识库文件夹应包含 .md 或 .txt 格式的文档。\n"
            "您可以选择已有文件夹或创建新文件夹。"
        )
        msg_box.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)

        if msg_box.exec() != QMessageBox.Ok:
            return None

        # 打开文件夹选择对话框
        folder_path = QFileDialog.getExistingDirectory(
            self,
            "选择知识库文件夹",
            str(Path.home()),
            QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks
        )

        if not folder_path:
            return None

        selected_path = Path(folder_path)

        # 检查是否有文档
        if not self._has_documents(selected_path):
            # 询问是否创建示例文档
            create_msg = QMessageBox(self)
            create_msg.setWindowTitle("知识库为空")
            create_msg.setIcon(QMessageBox.Question)
            create_msg.setText("所选文件夹为空或没有支持的文档")
            create_msg.setInformativeText(
                f"路径: {selected_path}\n\n"
                f"是否创建示例文档？\n"
                f"您也可以手动添加 .md 或 .txt 文件到此文件夹。"
            )
            create_msg.setStandardButtons(
                QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel
            )

            result = create_msg.exec()
            if result == QMessageBox.Yes:
                self._create_sample_document(selected_path)
            elif result == QMessageBox.Cancel:
                return None

        # 保存到配置
        self._save_knowledge_path(selected_path)

        # 重新初始化 RAG 引擎
        self._rag_engine = None

        return selected_path

    def _create_sample_document(self, path: Path):
        """创建示例知识库文档"""
        path.mkdir(parents=True, exist_ok=True)

        sample_file = path / "欢迎使用.md"
        sample_content = """# 欢迎使用 MechForge 知识库

这是您的知识库文件夹。

## 支持的文件格式

- **Markdown (.md)** - 推荐格式，支持标题、列表、代码块等
- **纯文本 (.txt)** - 简单文本格式

## 如何使用

1. 将您的技术文档、手册、笔记等放入此文件夹
2. 在 AI 对话中启用 RAG 功能
3. AI 会自动检索相关知识并回答您的问题

## 示例内容

### 材料力学公式

- 胡克定律: σ = Eε
- 剪切应力: τ = Gγ
- 泊松比: ν = -ε_transverse / ε_axial

### 常用材料属性

| 材料 | 弹性模量 (GPa) | 屈服强度 (MPa) |
|------|---------------|---------------|
| 钢   | 200           | 250-500       |
| 铝   | 70            | 50-300        |
| 钛   | 116           | 200-800       |

---

*提示：您可以删除此文件并添加自己的文档。*
"""
        sample_file.write_text(sample_content, encoding="utf-8")

    def _save_knowledge_path(self, path: Path):
        """保存知识库路径到配置"""
        try:
            from mechforge_core.config import save_config

            if self._config:
                self._config.knowledge.path = str(path)
                save_config(self._config)
        except Exception as e:
            print(f"保存配置失败: {e}")

    def _check_knowledge_module(self) -> bool:
        """检查知识库模块是否安装，未安装则提示用户"""
        try:
            import mechforge_knowledge
            return True
        except ImportError:
            # 显示安装提示对话框
            msg_box = QMessageBox(self)
            msg_box.setWindowTitle("知识库模块未安装")
            msg_box.setIcon(QMessageBox.Information)
            msg_box.setText("知识库检索功能需要安装知识库模块")
            msg_box.setInformativeText(
                "您可以通过以下命令安装：\n\n"
                "pip install mechforge-ai[rag]\n\n"
                "或完整安装：\n\n"
                "pip install mechforge-ai[all]"
            )
            msg_box.setStandardButtons(QMessageBox.Ok)
            msg_box.setDefaultButton(QMessageBox.Ok)

            # 设置样式匹配主题
            msg_box.setStyleSheet(f"""
                QMessageBox {{
                    background-color: {THEME['bg_secondary']};
                    color: {THEME['text_primary']};
                }}
                QMessageBox QLabel {{
                    color: {THEME['text_primary']};
                    font-family: "{FONT_FAMILY}";
                    font-size: {FONT_SIZE['normal']}px;
                }}
                QPushButton {{
                    background-color: rgba(34, 211, 238, 0.15);
                    color: {THEME['accent_cyan']};
                    border: 1px solid rgba(34, 211, 238, 0.35);
                    border-radius: 8px;
                    padding: 8px 20px;
                    font-family: "{FONT_FAMILY}";
                    font-weight: bold;
                }}
                QPushButton:hover {{
                    background-color: rgba(34, 211, 238, 0.25);
                }}
            """)

            msg_box.exec()
            return False
    
    def _clear_conversation(self):
        """清空对话"""
        self.conversation_history.clear()
        self.chat_area.clear_messages()
        self.chat_area.add_message("system", "✓ 对话历史已清除")
        self._update_status()
    
    def _show_history(self):
        """显示对话历史"""
        if not self.conversation_history:
            self.chat_area.add_message("system", "对话历史为空")
            return
        
        history_text = "最近对话:\n"
        for msg in self.conversation_history[-10:]:
            role = "你" if msg["role"] == "user" else "AI"
            content = msg["content"][:50]
            history_text += f"  [{role}]: {content}...\n"
        
        history_text += f"\n(显示最近 10 条，共 {len(self.conversation_history)} 条)"
        self.chat_area.add_message("system", history_text)
    
    def _show_model_config(self):
        """显示模型配置对话框"""
        from mechforge_gui_ai.dialogs import ModelConfigDialog
        
        dialog = ModelConfigDialog(self._config, self._llm_client, self)
        if dialog.exec():
            self._update_status()
            self.chat_area.add_message("system", "✓ 模型配置已更新")
    
    def _new_session(self):
        """新建会话"""
        self._save_history()
        self.conversation_history.clear()
        self.chat_area.clear_messages()
        self.chat_area.add_message("system", "✓ 新会话已创建")
        self._update_status()
    
    def _show_about(self):
        """显示关于对话框"""
        QMessageBox.about(
            self,
            "关于 MechForge AI",
            """<h2>MechForge AI</h2>
            <p>版本 0.4.0</p>
            <p>机械设计 AI 垂直助手</p>
            <p>支持多模型 AI 对话、知识库检索、CAE 工作台</p>
            <hr>
            <p><a href="https://github.com/yd5768365-hue/mechforge">GitHub</a></p>
            """
        )
    
    def _load_history(self):
        """加载历史"""
        try:
            # 加载对话历史
            conv_file = Path.home() / ".mechforge" / "conversation.json"
            if conv_file.exists():
                with open(conv_file, encoding="utf-8") as f:
                    self.conversation_history = json.load(f)
            
            # 加载命令历史
            cmd_file = Path.home() / ".mechforge" / "history"
            if cmd_file.exists():
                with open(cmd_file, encoding="utf-8") as f:
                    self.command_history = [line.strip() for line in f if line.strip()]
        except Exception:
            pass
    
    def _save_history(self):
        """保存历史"""
        try:
            data_dir = Path.home() / ".mechforge"
            data_dir.mkdir(parents=True, exist_ok=True)
            
            # 保存对话历史
            conv_file = data_dir / "conversation.json"
            with open(conv_file, "w", encoding="utf-8") as f:
                json.dump(self.conversation_history[-50:], f, ensure_ascii=False, indent=2)
            
            # 保存命令历史
            cmd_file = data_dir / "history"
            with open(cmd_file, "w", encoding="utf-8") as f:
                for cmd in self.command_history[-100:]:
                    f.write(f"{cmd}\n")
        except Exception:
            pass
    
    def closeEvent(self, event):
        """关闭事件"""
        self._save_history()
        
        # 等待 API 线程结束
        if self._api_thread and self._api_thread.isRunning():
            self._api_thread.wait(1000)
        
        event.accept()
