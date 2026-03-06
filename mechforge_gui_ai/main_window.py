"""
主窗口 - 终端风格 GUI
"""

import json
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

from mechforge_gui_ai.theme import THEME, FONT_FAMILY, FONT_SIZE, WINDOW, get_stylesheet

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
    """消息显示组件 - 气泡式布局"""

    def __init__(self, role: str, content: str, parent=None):
        super().__init__(parent)
        self.role = role
        self.content = content
        self._setup_ui()

    def _setup_ui(self):
        """设置气泡式消息 UI"""
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 8, 0, 8)
        main_layout.setSpacing(12)

        is_user = self.role == "user"
        is_assistant = self.role == "assistant"

        # 头像（仅 AI 消息显示在左侧）
        avatar = QLabel()
        avatar.setFixedSize(36, 36)
        avatar.setAlignment(Qt.AlignCenter)

        if is_assistant:
            avatar.setText("◉")
            avatar_font = QFont("Segoe UI Symbol", 16, QFont.Bold)
            avatar.setFont(avatar_font)
            avatar.setStyleSheet(f"""
                QLabel {{
                    background: qradialgradient(
                        cx: 0.5, cy: 0.5, radius: 0.5,
                        stop: 0 {THEME['accent_cyan']},
                        stop: 1 transparent
                    );
                    color: {THEME['accent_cyan']};
                    border-radius: 18px;
                    border: 2px solid {THEME['accent_cyan']};
                }}
            """)
        elif is_user:
            avatar.setText("◆")
            avatar_font = QFont("Segoe UI Symbol", 14, QFont.Bold)
            avatar.setFont(avatar_font)
            avatar.setStyleSheet(f"""
                QLabel {{
                    background: qradialgradient(
                        cx: 0.5, cy: 0.5, radius: 0.5,
                        stop: 0 {THEME['accent_purple']},
                        stop: 1 transparent
                    );
                    color: {THEME['accent_purple']};
                    border-radius: 18px;
                    border: 2px solid {THEME['accent_purple']};
                }}
            """)
        else:
            avatar.setText("⚙")
            avatar.setStyleSheet(f"""
                QLabel {{
                    background-color: {THEME['bg_secondary']};
                    color: {THEME['system_color']};
                    border-radius: 18px;
                    border: 1px solid {THEME['system_color']};
                }}
            """)

        # 消息气泡容器
        bubble_container = QWidget()
        bubble_layout = QVBoxLayout(bubble_container)
        bubble_layout.setContentsMargins(0, 0, 0, 0)
        bubble_layout.setSpacing(4)

        # 角色名称
        name_label = QLabel()
        if is_user:
            name_label.setText("你")
            name_label.setAlignment(Qt.AlignRight)
            name_label.setStyleSheet(f"color: {THEME['accent_purple']}; font-size: 11px; font-weight: bold;")
        elif is_assistant:
            name_label.setText("MechForge AI")
            name_label.setAlignment(Qt.AlignLeft)
            name_label.setStyleSheet(f"color: {THEME['accent_cyan']}; font-size: 11px; font-weight: bold;")
        else:
            name_label.setText("系统")
            name_label.setAlignment(Qt.AlignCenter)
            name_label.setStyleSheet(f"color: {THEME['system_color']}; font-size: 11px;")

        # 消息气泡
        bubble = QTextEdit()
        bubble.setPlainText(self.content)
        bubble.setReadOnly(True)
        bubble.setMaximumHeight(500)
        bubble.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        bubble.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        # 气泡样式
        if is_user:
            # 用户消息 - 右侧紫色气泡
            bubble.setStyleSheet(f"""
                QTextEdit {{
                    background: qlineargradient(
                        x1: 0, y1: 0, x2: 1, y2: 1,
                        stop: 0 rgba(160, 32, 240, 0.15),
                        stop: 1 rgba(160, 32, 240, 0.05)
                    );
                    color: {THEME['text_primary']};
                    border: 1px solid rgba(160, 32, 240, 0.4);
                    border-radius: 16px;
                    border-top-right-radius: 4px;
                    padding: 12px 16px;
                    font-family: "{FONT_FAMILY}";
                    font-size: {FONT_SIZE['normal']}px;
                }}
                QScrollBar:vertical {{
                    background: transparent;
                    width: 4px;
                }}
                QScrollBar::handle:vertical {{
                    background: rgba(160, 32, 240, 0.5);
                    border-radius: 2px;
                }}
            """)
        elif is_assistant:
            # AI 消息 - 左侧青色气泡
            bubble.setStyleSheet(f"""
                QTextEdit {{
                    background: qlineargradient(
                        x1: 0, y1: 0, x2: 1, y2: 1,
                        stop: 0 rgba(0, 245, 255, 0.12),
                        stop: 1 rgba(0, 245, 255, 0.03)
                    );
                    color: {THEME['text_primary']};
                    border: 1px solid rgba(0, 245, 255, 0.3);
                    border-radius: 16px;
                    border-top-left-radius: 4px;
                    padding: 12px 16px;
                    font-family: "{FONT_FAMILY}";
                    font-size: {FONT_SIZE['normal']}px;
                }}
                QScrollBar:vertical {{
                    background: transparent;
                    width: 4px;
                }}
                QScrollBar::handle:vertical {{
                    background: rgba(0, 245, 255, 0.5);
                    border-radius: 2px;
                }}
            """)
        else:
            # 系统消息 - 居中橙色
            bubble.setStyleSheet(f"""
                QTextEdit {{
                    background-color: rgba(255, 140, 0, 0.1);
                    color: {THEME['system_color']};
                    border: 1px solid rgba(255, 140, 0, 0.3);
                    border-radius: 12px;
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


import random


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
    """聊天显示区域 - 电路板纹理背景 + 打字机动画"""

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

        # 设置纯色背景（电路板纹理通过 paintEvent 绘制）
        self.setStyleSheet(f"background-color: {THEME['bg_primary']};")

        # 滚动区域
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scroll_area.setFrameShape(QFrame.NoFrame)

        # 超细 cyan 发光滚动条
        self.scroll_area.setStyleSheet(f"""
            QScrollArea {{
                background: transparent;
                border: none;
            }}
            QScrollBar:vertical {{
                background: transparent;
                width: 3px;
                margin: 0px;
            }}
            QScrollBar::handle:vertical {{
                background: qlineargradient(
                    x1: 0, y1: 0, x2: 1, y2: 0,
                    stop: 0 rgba(0, 245, 255, 0.3),
                    stop: 0.5 rgba(0, 245, 255, 0.8),
                    stop: 1 rgba(0, 245, 255, 0.3)
                );
                min-height: 30px;
                border-radius: 1px;
            }}
            QScrollBar::handle:vertical:hover {{
                background: qlineargradient(
                    x1: 0, y1: 0, x2: 1, y2: 0,
                    stop: 0 rgba(0, 245, 255, 0.5),
                    stop: 0.5 rgba(0, 245, 255, 1.0),
                    stop: 1 rgba(0, 245, 255, 0.5)
                );
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
        self.message_layout.setSpacing(0)
        self.message_layout.setContentsMargins(16, 16, 16, 16)

        self.scroll_area.setWidget(self.message_container)
        layout.addWidget(self.scroll_area)

        # 显示打字机动画欢迎语
        self._show_typing_welcome()

    def _show_typing_welcome(self):
        """显示打字机动画欢迎语 - 随机选择"""
        # 随机选择一条欢迎词
        self._current_welcome = random.choice(WELCOME_MESSAGES)

        self._welcome_widget = QWidget()
        welcome_layout = QVBoxLayout(self._welcome_widget)
        welcome_layout.setAlignment(Qt.AlignCenter)
        welcome_layout.setSpacing(12)

        # 主标题
        self._welcome_title = QLabel()
        self._welcome_title.setAlignment(Qt.AlignCenter)
        title_font = QFont(FONT_FAMILY, 20, QFont.Bold)
        self._welcome_title.setFont(title_font)
        self._welcome_title.setStyleSheet(f"""
            color: {THEME['accent_cyan']};
            background: transparent;
            padding: 0 20px;
        """)

        # 副标题
        self._welcome_subtitle = QLabel()
        self._welcome_subtitle.setAlignment(Qt.AlignCenter)
        subtitle_font = QFont(FONT_FAMILY, 12)
        self._welcome_subtitle.setFont(subtitle_font)
        self._welcome_subtitle.setStyleSheet(f"""
            color: {THEME['accent_purple']};
            background: transparent;
            padding: 0 20px;
        """)

        # 内容区域（使用 QTextEdit 支持多行）- 霓虹发光边框
        self._welcome_content = QTextEdit()
        self._welcome_content.setReadOnly(True)
        self._welcome_content.setMaximumWidth(600)
        self._welcome_content.setMinimumHeight(200)
        # 玻璃态 + 霓虹发光边框
        self._welcome_content.setStyleSheet(f"""
            QTextEdit {{
                background: rgba(16, 24, 45, 0.70);
                color: {THEME['text_primary']};
                border: 1px solid rgba(0, 245, 255, 0.40);
                border-radius: 16px;
                padding: 20px 24px;
                font-family: "{FONT_FAMILY}";
                font-size: {FONT_SIZE['normal']}px;
                line-height: 1.7;
            }}
            QTextEdit:focus {{
                border: 1px solid rgba(0, 245, 255, 0.80);
            }}
        """)
        # 添加外发光效果
        from PySide6.QtWidgets import QGraphicsDropShadowEffect
        glow_effect = QGraphicsDropShadowEffect()
        glow_effect.setBlurRadius(30)
        glow_effect.setColor(QColor(0, 245, 255, 100))
        glow_effect.setOffset(0, 0)
        self._welcome_content.setGraphicsEffect(glow_effect)

        welcome_layout.addWidget(self._welcome_title)
        welcome_layout.addWidget(self._welcome_subtitle)
        welcome_layout.addWidget(self._welcome_content)

        self.message_layout.addWidget(self._welcome_widget)

        # 打字机动画序列
        self._type_text(self._welcome_title, self._current_welcome["title"], 0, lambda:
            self._type_text(self._welcome_subtitle, self._current_welcome["subtitle"], 0, lambda:
                self._type_text_content(self._welcome_content, self._current_welcome["content"], 0)))

    def _type_text(self, label: QLabel, text: str, index: int, callback=None):
        """打字机效果 - 单行文本"""
        try:
            # 检查标签是否还存在
            if not label or not label.parentWidget():
                return

            if index <= len(text):
                label.setText(text[:index] + "▋")
                QTimer.singleShot(50, lambda: self._type_text(label, text, index + 1, callback))
            else:
                label.setText(text)
                if callback:
                    callback()
        except (RuntimeError, AttributeError):
            # 对象已被删除，忽略
            pass

    def _type_text_content(self, text_edit: QTextEdit, text: str, index: int):
        """打字机效果 - 多行内容（带渐隐）"""
        try:
            # 检查控件是否还存在
            if not text_edit or not text_edit.parentWidget():
                return

            if index <= len(text):
                # 显示当前文本 + 光标
                current_text = text[:index]
                # 使用 HTML 格式添加闪烁光标
                html_content = current_text.replace("\n", "<br>")
                html_content += '<span style="color: #00F5FF;">▋</span>'
                text_edit.setHtml(f'<div style="color: {THEME["text_primary"]};">{html_content}</div>')

                # 计算延迟（标点符号稍微停顿）
                delay = 30 if index < len(text) and text[index] in '。！？.!?\n' else 15
                QTimer.singleShot(delay, lambda: self._type_text_content(text_edit, text, index + 1))
            else:
                # 打字完成，显示最终文本
                final_text = text.replace("\n", "<br>")
                text_edit.setHtml(f'<div style="color: {THEME["text_primary"]};">{final_text}</div>')
                # 3秒后渐隐
                QTimer.singleShot(3000, self._fade_out_welcome)
        except (RuntimeError, AttributeError):
            # 对象已被删除，忽略
            pass

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
        # 如果有欢迎语，先移除
        if self._welcome_widget:
            self._remove_welcome()

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
        """绘制 Dark Glassmorphism 六边形蜂窝网格背景"""
        from PySide6.QtGui import QPainter, QPen, QColor, QPolygonF, QLinearGradient
        from PySide6.QtCore import QPointF

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # 绘制深海军蓝渐变背景
        gradient = QLinearGradient(0, 0, 0, self.height())
        gradient.setColorAt(0, QColor(THEME['bg_primary']))
        gradient.setColorAt(1, QColor(THEME['bg_secondary']))
        painter.fillRect(self.rect(), gradient)

        # 绘制六边形蜂窝网格
        hex_size = 25  # 六边形半径
        hex_height = hex_size * 1.732  # 六边形高度 (√3)
        opacity = 25  # 极淡的透明度

        pen = QPen(QColor(0, 245, 255, opacity))
        pen.setWidth(1)
        painter.setPen(pen)
        painter.setBrush(Qt.NoBrush)

        # 计算六边形顶点
        def draw_hexagon(cx, cy, size):
            points = []
            for i in range(6):
                angle = 60 * i - 30  # 从顶部开始
                x = cx + size * 0.866 * (1 if i in [0, 3] else (-0.5 if i in [1, 2] else 0.5))
                y = cy + size * (0 if i in [0, 3] else (-0.866 if i in [1, 5] else 0.866))
                # 修正计算
                rad = 3.14159 / 180 * (60 * i - 30)
                px = cx + size * (1 if i == 0 else -0.5 if i in [1, 5] else -0.5 if i == 2 else -1 if i == 3 else 0.5 if i == 4 else 0.5)
                py = cy + size * (0 if i in [0, 3] else -0.866 if i in [1, 5] else 0.866)
            
            # 正确的六边形顶点计算
            for i in range(6):
                angle_deg = 60 * i - 30
                angle_rad = 3.14159 / 180 * angle_deg
                px = cx + size * (1 if i == 0 else 0.5 if i == 1 else -0.5 if i == 2 else -1 if i == 3 else -0.5 if i == 4 else 0.5)
                py = cy + size * (0 if i in [0, 3] else -0.866 if i in [1, 5] else 0.866)
                points.append(QPointF(px, py))
            
            polygon = QPolygonF(points)
            painter.drawPolygon(polygon)

        # 绘制蜂窝网格
        row_height = hex_height * 0.75
        for row in range(-1, int(self.height() / row_height) + 2):
            for col in range(-1, int(self.width() / (hex_size * 3)) + 2):
                x = col * hex_size * 3 + (hex_size * 1.5 if row % 2 else 0)
                y = row * row_height
                draw_hexagon(x, y, hex_size - 2)

        # 添加玻璃态模糊层（半透明渐变覆盖）
        overlay = QLinearGradient(0, 0, self.width(), self.height())
        overlay.setColorAt(0, QColor(10, 15, 28, 100))
        overlay.setColorAt(0.5, QColor(10, 15, 28, 0))
        overlay.setColorAt(1, QColor(10, 15, 28, 100))
        painter.fillRect(self.rect(), overlay)

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
        layout.setContentsMargins(16, 8, 16, 12)
        layout.setSpacing(8)

        # 玻璃态输入容器
        input_container = QWidget()
        input_container.setStyleSheet(f"""
            QWidget {{
                background: rgba(16, 24, 45, 0.60);
                border: 1px solid rgba(0, 245, 255, 0.20);
                border-radius: 12px;
            }}
        """)
        container_layout = QHBoxLayout(input_container)
        container_layout.setContentsMargins(12, 8, 12, 8)
        container_layout.setSpacing(8)

        # 提示符
        prompt_label = QLabel(">")
        prompt_label.setStyleSheet(f"""
            color: {THEME['accent_cyan']};
            font-weight: bold;
            font-size: 16px;
            background: transparent;
        """)
        prompt_label.setFixedWidth(20)

        # 输入框 - 玻璃态风格
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("输入消息或命令...")
        self.input_field.returnPressed.connect(self._on_send)
        self.input_field.installEventFilter(self)
        self.input_field.setStyleSheet(f"""
            QLineEdit {{
                background: transparent;
                color: {THEME['text_primary']};
                border: none;
                font-family: "{FONT_FAMILY}";
                font-size: {FONT_SIZE['normal']}px;
                padding: 4px;
            }}
            QLineEdit::placeholder {{
                color: {THEME['text_muted']};
            }}
        """)

        # 发送按钮 - 霓虹风格
        self.send_button = QPushButton("发送")
        self.send_button.setFixedSize(60, 32)
        self.send_button.setStyleSheet(f"""
            QPushButton {{
                background: rgba(0, 245, 255, 0.15);
                color: {THEME['accent_cyan']};
                border: 1px solid rgba(0, 245, 255, 0.40);
                border-radius: 8px;
                font-family: "{FONT_FAMILY}";
                font-size: 12px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background: rgba(0, 245, 255, 0.30);
                border: 1px solid rgba(0, 245, 255, 0.80);
            }}
            QPushButton:pressed {{
                background: rgba(0, 245, 255, 0.50);
                color: #0A0F1C;
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
        banner.setFixedHeight(52)
        # 玻璃态效果：半透明 + 模糊 + 边框发光
        banner.setStyleSheet(f"""
            QWidget {{
                background: qlineargradient(
                    x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 rgba(16, 24, 45, 0.85),
                    stop: 0.5 rgba(16, 24, 45, 0.70),
                    stop: 1 rgba(16, 24, 45, 0.60)
                );
                border-bottom: 1px solid rgba(0, 245, 255, 0.25);
            }}
        """)

        banner_layout = QHBoxLayout(banner)
        banner_layout.setContentsMargins(16, 6, 16, 6)
        banner_layout.setSpacing(12)

        # 左侧：Logo + 标题
        logo_widget = QWidget()
        logo_layout = QHBoxLayout(logo_widget)
        logo_layout.setContentsMargins(0, 0, 0, 0)
        logo_layout.setSpacing(10)

        # Logo 图标（齿轮样式）
        logo_icon = QLabel("⚙")
        logo_icon_font = QFont("Segoe UI Emoji", 18)
        logo_icon.setFont(logo_icon_font)
        logo_icon.setStyleSheet("""
            color: #00F5FF;
            background: transparent;
        """)
        logo_icon.setFixedSize(28, 28)
        logo_icon.setAlignment(Qt.AlignCenter)

        # 标题文字
        title_label = QLabel("MechForge AI")
        title_font = QFont(FONT_FAMILY, 14, QFont.Bold)
        title_label.setFont(title_font)
        title_label.setStyleSheet("""
            color: #FFFFFF;
            background: transparent;
            font-weight: bold;
        """)

        logo_layout.addWidget(logo_icon)
        logo_layout.addWidget(title_label)

        # 右侧：工具栏按钮
        toolbar_widget = QWidget()
        toolbar_layout = QHBoxLayout(toolbar_widget)
        toolbar_layout.setContentsMargins(0, 0, 0, 0)
        toolbar_layout.setSpacing(8)
        toolbar_layout.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

        # 创建胶囊按钮 - 使用文字+简单符号
        self._create_pill_button(toolbar_layout, "+ 新建", "新建会话", self._new_session)
        self._create_pill_button(toolbar_layout, "C 清空", "清空对话", self._clear_conversation)
        self._create_pill_button(toolbar_layout, "RAG", "RAG开关", self._toggle_rag)
        self._create_pill_button(toolbar_layout, "? 帮助", "帮助", self._show_help)
        self._create_pill_button(toolbar_layout, "X 退出", "退出", self.close, is_danger=True)

        banner_layout.addWidget(logo_widget, stretch=1)
        banner_layout.addWidget(toolbar_widget)

        parent_layout.addWidget(banner)

    def _create_pill_button(self, layout, text, tooltip, callback, is_danger=False):
        """创建胶囊按钮 - 霓虹青辉光效果"""
        btn = QPushButton(text)
        btn.setCursor(Qt.PointingHandCursor)
        btn.setToolTip(tooltip)
        btn.setFixedHeight(28)

        # 根据文字长度调整宽度
        btn.setMinimumWidth(60)

        # 颜色配置
        if is_danger:
            normal_color = "rgba(255, 68, 68, 0.1)"
            border_color = "rgba(255, 68, 68, 0.4)"
            hover_color = "rgba(255, 68, 68, 0.25)"
            text_color = "#FF6666"
        else:
            normal_color = "rgba(0, 245, 255, 0.08)"
            border_color = "rgba(0, 245, 255, 0.3)"
            hover_color = "rgba(0, 245, 255, 0.2)"
            text_color = "#00F5FF"

        # 基础样式 - 使用 Consolas 字体避免 Unicode 问题
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {normal_color};
                color: {text_color};
                border: 1px solid {border_color};
                border-radius: 14px;
                font-size: 11px;
                font-family: "{FONT_FAMILY}";
                font-weight: bold;
                padding: 0 12px;
            }}
            QPushButton:hover {{
                background-color: {hover_color};
                border: 1px solid {text_color};
            }}
            QPushButton:pressed {{
                background-color: {text_color};
                color: #0F1320;
            }}
        """)

        btn.clicked.connect(callback)
        layout.addWidget(btn)

    def _setup_statusbar(self):
        """设置状态栏 - Dark Glassmorphism 风格"""
        self.statusbar = QStatusBar()
        self.statusbar.setFixedHeight(28)
        self.statusbar.setStyleSheet(f"""
            QStatusBar {{
                background: rgba(10, 15, 28, 0.80);
                color: {THEME['text_secondary']};
                border-top: 1px solid rgba(0, 245, 255, 0.15);
                font-size: {FONT_SIZE['small']}px;
                font-family: "{FONT_FAMILY}";
            }}
            QStatusBar::item {{
                border: none;
            }}
        """)
        self.setStatusBar(self.statusbar)

        # API 状态 - 带指示点
        self.api_indicator = QLabel("●")
        self.api_indicator.setStyleSheet("color: #555; font-size: 8px;")
        self.api_label = QLabel("API: --")
        self.api_label.setStyleSheet(f"color: {THEME['text_secondary']};")

        # 模型状态
        self.model_indicator = QLabel("●")
        self.model_indicator.setStyleSheet("color: #555; font-size: 8px;")
        self.model_label = QLabel("模型: --")
        self.model_label.setStyleSheet(f"color: {THEME['text_secondary']};")

        # RAG 状态
        self.rag_indicator = QLabel("●")
        self.rag_indicator.setStyleSheet("color: #555; font-size: 8px;")
        self.rag_label = QLabel("RAG: OFF")
        self.rag_label.setStyleSheet(f"color: {THEME['text_muted']};")

        # 消息计数
        self.msg_label = QLabel("消息: 0")
        self.msg_label.setStyleSheet(f"color: {THEME['text_secondary']};")

        # 分隔符
        separator = QLabel("│")
        separator.setStyleSheet(f"color: rgba(0, 245, 255, 0.3); padding: 0 8px;")

        # 添加状态项
        self.statusbar.addWidget(self.api_indicator)
        self.statusbar.addWidget(self.api_label)
        self.statusbar.addWidget(QLabel("  "))
        self.statusbar.addWidget(self.model_indicator)
        self.statusbar.addWidget(self.model_label)
        self.statusbar.addWidget(QLabel("  "))
        self.statusbar.addWidget(self.rag_indicator)
        self.statusbar.addWidget(self.rag_label)
        self.statusbar.addWidget(QLabel("  "))
        self.statusbar.addWidget(self.msg_label)
    
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
            self.model_label.setText(f"模型: {model_name}")
        
        rag_color = THEME['accent_green'] if self.rag_enabled else THEME['accent_red']
        self.rag_label.setText(f"RAG: {'ON' if self.rag_enabled else 'OFF'}")
        self.rag_label.setStyleSheet(f"color: {rag_color};")
        
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
        """切换 RAG"""
        if not self.rag_engine or not self.rag_engine.is_available:
            self.chat_area.add_message("system", "✗ 未找到知识库")
            return
        
        self.rag_enabled = not self.rag_enabled
        status = "启用" if self.rag_enabled else "禁用"
        self.chat_area.add_message("system", f"✓ RAG 已{status}")
        self._update_status()
    
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
        from mechforge_gui.dialogs import ModelConfigDialog
        
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