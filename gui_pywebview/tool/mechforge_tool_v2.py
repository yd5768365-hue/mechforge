#!/usr/bin/env python3
"""
MechForge AI Tool v2 - 美化升级版
基于DearPyGUI的赛博朋克风格界面 + AI聊天集成
特性：Unicode图标、聊天气泡、HUD装饰线、无缝布局
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import dearpygui.dearpygui as dpg
from datetime import datetime
import threading
import queue

# 导入MechForge AI模块
try:
    from mechforge_ai.llm_client import LLMClient
    from mechforge_core.config import get_config
    MECHFORGE_AVAILABLE = True
except ImportError as e:
    print(f"[警告] 无法导入MechForge模块: {e}")
    MECHFORGE_AVAILABLE = False

# ==========================================
# 1. 核心色彩与主题 (赛博机械霓虹)
# ==========================================
NAVY_BG = (10, 14, 24, 255)        # 极深海军蓝 (底色)
PANEL_BG = (15, 20, 33, 255)       # 面板背景色 (略亮一点点)
CYAN_NEON = (0, 255, 230, 255)     # 青色霓虹主色
CYAN_DIM = (0, 255, 230, 60)       # 黯淡青色 (用于边框/非活跃状态)
PURPLE_GLOW = (130, 60, 255, 255)  # 紫色能量渐变 (强调色)
PURPLE_DIM = (130, 60, 255, 50)    # 紫色暗背景 (用于用户气泡)
TEXT_COLD = (200, 230, 240, 255)   # 冷白带青字体

COLOR_SUCCESS = (80, 220, 120, 255)
COLOR_WARNING = (255, 180, 60, 255)
COLOR_ERROR = (255, 90, 90, 255)

# ==========================================
# 2. AI聊天管理器
# ==========================================
class AIChatManager:
    """AI聊天管理器"""
    
    def __init__(self):
        self.llm = None
        self.messages = []
        self.is_ready = False
        self.streaming = False
        
        if MECHFORGE_AVAILABLE:
            try:
                self.llm = LLMClient()
                self.is_ready = True
                print("[AI] LLM客户端初始化成功")
            except Exception as e:
                print(f"[AI] LLM初始化失败: {e}")
    
    def send_message(self, message, callback=None):
        """发送消息到AI"""
        if not self.is_ready:
            return "[错误] AI未初始化，请检查配置"
        
        self.messages.append({"role": "user", "content": message})
        
        try:
            response_text = ""
            self.streaming = True
            
            for chunk in self.llm.chat_stream(message, history=self.messages[:-1]):
                if chunk:
                    response_text += chunk
                    if callback:
                        callback(chunk, is_streaming=True)
            
            self.streaming = False
            self.messages.append({"role": "assistant", "content": response_text})
            
            if len(self.messages) > 20:
                self.messages = self.messages[-20:]
            
            return response_text
            
        except Exception as e:
            self.streaming = False
            return f"[错误] AI响应失败: {str(e)}"
    
    def clear_history(self):
        """清空对话历史"""
        self.messages = []
    
    def get_status(self):
        """获取AI状态"""
        if not MECHFORGE_AVAILABLE:
            return "未安装"
        if not self.is_ready:
            return "初始化失败"
        if self.streaming:
            return "生成中..."
        return "就绪"

# ==========================================
# 3. 全局状态
# ==========================================
class AppState:
    def __init__(self):
        self.current_mode = "ai"
        self.ai_manager = AIChatManager()
        self.current_response = ""
        self.bubble_count = 0

app_state = AppState()

# ==========================================
# 4. 自定义组件：聊天气泡主题
# ==========================================
def create_bubble_theme(bg_color, border_color):
    """创建聊天气泡主题"""
    with dpg.theme() as theme_id:
        with dpg.theme_component(dpg.mvChildWindow):
            dpg.add_theme_color(dpg.mvThemeCol_ChildBg, bg_color)
            dpg.add_theme_color(dpg.mvThemeCol_Border, border_color)
            dpg.add_theme_style(dpg.mvStyleVar_ChildBorderSize, 1)
            dpg.add_theme_style(dpg.mvStyleVar_ChildRounding, 6)
            dpg.add_theme_style(dpg.mvStyleVar_WindowPadding, 10, 8)
    return theme_id

# ==========================================
# 5. 交互逻辑
# ==========================================
def switch_mode(sender, app_data, user_data):
    """切换模式"""
    for mode in ["mode_ai", "mode_kb", "mode_tool"]:
        dpg.configure_item(mode, show=False)
    dpg.configure_item(user_data, show=True)
    app_state.current_mode = user_data.replace("mode_", "")

def update_ai_response(chunk, is_streaming=False):
    """更新AI流式响应"""
    if is_streaming:
        app_state.current_response += chunk
        dpg.set_value("last_ai_response", app_state.current_response)

def send_message_async():
    """异步发送消息"""
    message = dpg.get_value("input_message")
    if not message.strip():
        return
    
    timestamp = datetime.now().strftime("%H:%M")
    app_state.bubble_count += 1
    
    # 用户气泡 (靠右缩进模拟)
    with dpg.group(parent="chat_history"):
        dpg.add_spacer(height=5)
        with dpg.group(horizontal=True):
            dpg.add_spacer(width=200)
            with dpg.child_window(width=450, height=0, tag=f"user_bubble_{app_state.bubble_count}"):
                dpg.add_text(f"🧑 你 [{timestamp}]", color=PURPLE_GLOW)
                dpg.add_text(message, color=TEXT_COLD, wrap=430)
        dpg.bind_item_theme(f"user_bubble_{app_state.bubble_count}", theme_user_bubble)
    
    dpg.set_value("input_message", "")
    dpg.set_y_scroll("chat_history", dpg.get_y_scroll_max("chat_history"))
    
    # AI气泡占位
    app_state.bubble_count += 1
    with dpg.group(parent="chat_history"):
        dpg.add_spacer(height=5)
        with dpg.child_window(width=450, height=0, tag=f"ai_bubble_{app_state.bubble_count}"):
            dpg.add_text(f"🤖 MechForge [{timestamp}]", color=CYAN_NEON)
            app_state.current_response = "思考中..."
            dpg.add_text(app_state.current_response, color=TEXT_COLD, wrap=430, tag="last_ai_response")
        dpg.bind_item_theme(f"ai_bubble_{app_state.bubble_count}", theme_ai_bubble)
    
    dpg.set_y_scroll("chat_history", dpg.get_y_scroll_max("chat_history"))
    
    # 后台线程调用AI
    def ai_thread():
        response = app_state.ai_manager.send_message(message, callback=update_ai_response)
        dpg.set_value("last_ai_response", response)
    
    thread = threading.Thread(target=ai_thread, daemon=True)
    thread.start()

def clear_chat(sender, app_data, user_data):
    """清空聊天"""
    for child in dpg.get_item_children("chat_history")[1]:
        dpg.delete_item(child)
    app_state.ai_manager.clear_history()
    app_state.bubble_count = 0
    
    # 添加欢迎消息
    with dpg.group(parent="chat_history"):
        dpg.add_spacer(height=5)
        with dpg.child_window(width=450, height=0):
            dpg.add_text("🤖 MechForge [系统]", color=CYAN_NEON)
            welcome = """👋 欢迎使用 MechForge AI

我是您的机械工程AI助手，可以帮助您：
• 解答机械设计问题
• 分析CAE仿真结果
• 检索知识库文档
• 执行工程计算

请输入您的问题开始对话..."""
            dpg.add_text(welcome, color=TEXT_COLD, wrap=430)
        dpg.bind_item_theme(dpg.last_item(), theme_ai_bubble)

# ==========================================
# 6. 主程序
# ==========================================
def main():
    dpg.create_context()
    
    # ==========================================
    # 字体注册 (修复中文与引入符号)
    # ==========================================
    with dpg.font_registry():
        font_path = "C:/Windows/Fonts/msyh.ttc"
        if os.path.exists(font_path):
            with dpg.font(font_path, 16) as default_font:
                dpg.add_font_range_hint(dpg.mvFontRangeHint_Chinese_Simplified_Common)
                dpg.add_font_range_hint(dpg.mvFontRangeHint_Default)
            dpg.bind_font(default_font)
            print(f"[字体] 成功加载: {font_path}")
        else:
            print(f"[警告] 找不到字体文件: {font_path}")
    
    # ==========================================
    # 全局主题
    # ==========================================
    with dpg.theme() as global_theme:
        with dpg.theme_component(dpg.mvAll):
            dpg.add_theme_color(dpg.mvThemeCol_WindowBg, NAVY_BG)
            dpg.add_theme_color(dpg.mvThemeCol_ChildBg, PANEL_BG)
            dpg.add_theme_color(dpg.mvThemeCol_Border, CYAN_DIM)
            dpg.add_theme_color(dpg.mvThemeCol_Text, TEXT_COLD)
            
            # 隐藏原生边框，依靠发光线来界定区域
            dpg.add_theme_style(dpg.mvStyleVar_WindowBorderSize, 0)
            dpg.add_theme_style(dpg.mvStyleVar_ChildBorderSize, 0)
            dpg.add_theme_style(dpg.mvStyleVar_WindowPadding, 0, 0)
            dpg.add_theme_style(dpg.mvStyleVar_ItemSpacing, 8, 8)
            
            # 按钮样式
            dpg.add_theme_color(dpg.mvThemeCol_Button, (25, 35, 55, 0))
            dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, CYAN_DIM)
            dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, PURPLE_DIM)
            dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 4)
    
    dpg.bind_theme(global_theme)
    
    # 创建气泡主题
    global theme_ai_bubble, theme_user_bubble
    theme_ai_bubble = create_bubble_theme((0, 40, 40, 100), CYAN_DIM)
    theme_user_bubble = create_bubble_theme(PURPLE_DIM, (130, 60, 255, 100))
    
    # ==========================================
    # 界面构建
    # ==========================================
    with dpg.window(tag="main_window"):
        
        # --- 顶部：伪标题栏 (极简发光线) ---
        with dpg.child_window(height=35):
            dpg.add_spacer(height=8)
            with dpg.group(horizontal=True):
                dpg.add_spacer(width=10)
                dpg.add_text("⚡ MechForge AI Tool", color=CYAN_NEON)
                ai_status = app_state.ai_manager.get_status()
                status_color = CYAN_NEON if ai_status == "就绪" else COLOR_WARNING if ai_status == "生成中..." else COLOR_ERROR
                dpg.add_text(f"  [AI: {ai_status}]", color=status_color)
            
            # HUD 发光装饰线
            with dpg.drawlist(width=850, height=5):
                dpg.draw_line((0, 0), (850, 0), color=CYAN_DIM, thickness=1)
                dpg.draw_line((10, 0), (150, 0), color=CYAN_NEON, thickness=2)
        
        # --- 中部：左侧导航 + 主内容区 ---
        with dpg.group(horizontal=True):
            
            # [左侧窄导航] - 60px 宽，Unicode图标
            with dpg.child_window(width=60, height=520):
                dpg.add_spacer(height=10)
                dpg.add_button(label=" 🤖\n AI", width=50, height=50, callback=switch_mode, user_data="mode_ai")
                dpg.add_button(label=" 📚\n KB", width=50, height=50, callback=switch_mode, user_data="mode_kb")
                dpg.add_button(label=" 🛠️\n CAE", width=50, height=50, callback=switch_mode, user_data="mode_tool")
                dpg.add_spacer(height=250)
                dpg.add_button(label=" 🗑️\n CLR", width=50, height=50, callback=clear_chat)
                dpg.add_spacer(height=5)
                dpg.add_button(label=" ⚙️\n SET", width=50, height=50)
                
                # 右侧垂直分割线
                with dpg.drawlist(width=2, height=520, pos=(58, 0)):
                    dpg.draw_line((0, 0), (0, 520), color=CYAN_DIM, thickness=1)
            
            # [中央主内容区]
            with dpg.child_window(width=-1, height=520):
                dpg.add_spacer(height=10)
                
                # --- 模式1: AI 模式 ---
                with dpg.group(tag="mode_ai", show=True):
                    with dpg.child_window(height=-55, tag="chat_history"):
                        # 欢迎气泡
                        with dpg.child_window(width=450, height=0):
                            dpg.add_text("🤖 MechForge [系统]", color=CYAN_NEON)
                            welcome = """👋 欢迎使用 MechForge AI Tool

我是您的机械工程AI助手，可以帮助您：
• 解答机械设计问题
• 分析CAE仿真结果
• 检索知识库文档
• 执行工程计算

请输入您的问题开始对话..."""
                            dpg.add_text(welcome, color=TEXT_COLD, wrap=430)
                        dpg.bind_item_theme(dpg.last_item(), theme_ai_bubble)
                    
                    # 底部输入框区域
                    with dpg.group(horizontal=True):
                        dpg.add_spacer(width=5)
                        dpg.add_input_text(tag="input_message", width=-85, hint="[ 输入工程指令 / 查询参数 ] ...", on_enter=True, callback=send_message_async)
                        
                        # 发送按钮特殊样式
                        with dpg.theme() as btn_theme:
                            with dpg.theme_component(dpg.mvButton):
                                dpg.add_theme_color(dpg.mvThemeCol_Button, PURPLE_DIM)
                                dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, (130, 60, 255, 100))
                                dpg.add_theme_color(dpg.mvThemeCol_Text, CYAN_NEON)
                        btn = dpg.add_button(label="📤 SEND", width=80, callback=send_message_async)
                        dpg.bind_item_theme(btn, btn_theme)
                
                # --- 模式2: 知识库模式 (KB) ---
                with dpg.group(tag="mode_kb", show=False):
                    with dpg.group(horizontal=True):
                        dpg.add_spacer(width=5)
                        dpg.add_input_text(width=-100, hint="🔍 检索技术文档、标准规范...")
                        dpg.add_button(label="➕ 添加", width=80)
                    dpg.add_spacer(height=15)
                    
                    dpg.add_text("  ⚡ 索引中 [████████░░] 82%  |  速度: 17MB/s", color=CYAN_NEON)
                    dpg.add_spacer(height=10)
                    
                    # 列表卡片
                    with dpg.child_window(height=-10):
                        files = [
                            ("GB/T 228.1-2021 金属材料拉伸试验.pdf", "匹配段落：屈服强度测定...", 90),
                            ("悬臂梁受力分析报告_v2.pdf", "匹配段落：最大挠度计算...", 85),
                            ("齿轮设计规范2024.docx", "匹配段落：模数选择标准...", 75),
                        ]
                        for name, desc, score in files:
                            with dpg.child_window(height=80):
                                dpg.add_text(f"📄 {name}", color=CYAN_NEON)
                                dpg.add_text(f"   {desc}", color=(150, 160, 170, 255))
                                dpg.add_progress_bar(default_value=score/100, overlay=f"相关度 {score}%", width=150)
                            dpg.bind_item_theme(dpg.last_item(), theme_ai_bubble)
                
                # --- 模式3: 工具台模式 (CAE) ---
                with dpg.group(tag="mode_tool", show=False):
                    with dpg.group(horizontal=True):
                        dpg.add_spacer(width=5)
                        dpg.add_button(label="➕ 新建")
                        dpg.add_button(label="📂 导入")
                        dpg.add_button(label="🔲 网格")
                        dpg.add_button(label="▶ 求解")
                    dpg.add_spacer(height=15)
                    
                    with dpg.group(horizontal=True):
                        dpg.add_spacer(width=5)
                        dpg.add_progress_bar(default_value=0.67, overlay="Gmsh 网格生成中... 67% (预计剩余 12s)", width=-10)
                    
                    dpg.add_spacer(height=15)
                    
                    with dpg.group(horizontal=True):
                        dpg.add_spacer(width=5)
                        # 控制台日志区
                        with dpg.child_window(width=300, height=-10, tag="console_win"):
                            dpg.add_text(">> SYSTEM LOG", color=CYAN_NEON)
                            logs = [
                                ("[INFO]", "Reading STEP file...", COLOR_SUCCESS),
                                ("[INFO]", "Initializing Gmsh API...", COLOR_SUCCESS),
                                ("[WARN]", "High aspect ratio detected", COLOR_WARNING),
                                ("[INFO]", "Remeshing surface...", COLOR_SUCCESS),
                            ]
                            for level, msg, color in logs:
                                dpg.add_text(f"{level} {msg}", color=color)
                        dpg.bind_item_theme("console_win", theme_ai_bubble)
                        
                        # 可视化占位区
                        with dpg.child_window(width=-10, height=-10, tag="viewer_win"):
                            dpg.add_spacer(height=100)
                            with dpg.group(horizontal=True):
                                dpg.add_spacer(width=100)
                                dpg.add_text("[ 3D Render View ]\n\nWaiting for VTK/PyVista Stream...", color=CYAN_DIM)
                            
                            # 3D线框示意
                            with dpg.drawlist(width=-1, height=150):
                                cx, cy = 200, 75
                                size = 40
                                pts = [
                                    (cx-size, cy-size//2), (cx+size, cy-size//2),
                                    (cx+size+20, cy-size//2-20), (cx-size+20, cy-size//2-20)
                                ]
                                for i in range(4):
                                    dpg.draw_line(pts[i], pts[(i+1)%4], color=CYAN_NEON, thickness=2)
                                    dpg.draw_line((pts[i][0], pts[i][1]+size), 
                                                (pts[(i+1)%4][0], pts[(i+1)%4][1]+size), 
                                                color=CYAN_NEON, thickness=2)
                                    dpg.draw_line(pts[i], (pts[i][0], pts[i][1]+size), 
                                                color=CYAN_DIM, thickness=1)
                        dpg.bind_item_theme("viewer_win", theme_user_bubble)
        
        # --- 底部状态栏 ---
        with dpg.drawlist(width=850, height=2):
            dpg.draw_line((0, 0), (850, 0), color=CYAN_DIM, thickness=1)
        
        with dpg.child_window(height=40):
            dpg.add_spacer(height=5)
            with dpg.group(horizontal=True):
                dpg.add_spacer(width=10)
                dpg.add_text("●", color=CYAN_NEON)
                dpg.add_text("Ollama RAG", color=TEXT_COLD)
                dpg.add_text("|", color=CYAN_DIM)
                dpg.add_text("Model: qwen2.5:3b", color=TEXT_COLD)
                dpg.add_text("|", color=CYAN_DIM)
                dpg.add_text("MEM: 1.2GB", color=TEXT_COLD)
                
                dpg.add_spacer(width=200)
                dpg.add_text("CPU: 12%  GPU: 45%", color=PURPLE_GLOW)
    
    # ==========================================
    # 视口与渲染
    # ==========================================
    dpg.create_viewport(
        title='MechForge AI Tool v2',
        width=850,
        height=620,
        resizable=False,
        vsync=True,
        clear_color=NAVY_BG
    )
    
    dpg.setup_dearpygui()
    dpg.show_viewport()
    dpg.set_primary_window("main_window", True)
    
    while dpg.is_dearpygui_running():
        dpg.render_dearpygui_frame()
    
    dpg.destroy_context()

if __name__ == "__main__":
    main()
