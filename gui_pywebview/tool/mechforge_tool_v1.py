#!/usr/bin/env python3
"""
MechForge AI Tool - 集成AI聊天的工具界面
基于DearPyGUI的赛博朋克风格界面
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
    print(f"警告: 无法导入MechForge模块: {e}")
    MECHFORGE_AVAILABLE = False

# ==========================================
# 配色方案
# ==========================================
COLOR_BG_DARK = (8, 12, 20, 255)
COLOR_BG_PANEL = (15, 20, 32, 255)
COLOR_BG_CARD = (22, 28, 42, 255)
COLOR_BG_HOVER = (30, 38, 56, 255)

COLOR_CYAN = (0, 245, 255, 255)
COLOR_CYAN_GLOW = (0, 245, 255, 180)
COLOR_CYAN_DIM = (0, 180, 200, 100)
COLOR_PURPLE = (180, 100, 255, 255)
COLOR_PURPLE_GLOW = (180, 100, 255, 150)
COLOR_GOLD = (255, 200, 80, 255)

COLOR_TEXT_PRIMARY = (230, 240, 255, 255)
COLOR_TEXT_SECONDARY = (150, 170, 200, 255)
COLOR_TEXT_MUTED = (100, 120, 150, 255)

COLOR_SUCCESS = (80, 220, 120, 255)
COLOR_WARNING = (255, 180, 60, 255)
COLOR_ERROR = (255, 90, 90, 255)
COLOR_INFO = (80, 160, 255, 255)

COLOR_BORDER = (40, 55, 80, 255)
COLOR_SEPARATOR = (50, 65, 95, 255)

# ==========================================
# AI聊天管理器
# ==========================================
class AIChatManager:
    """AI聊天管理器"""
    
    def __init__(self):
        self.llm = None
        self.messages = []
        self.is_ready = False
        self.response_queue = queue.Queue()
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
        
        # 添加用户消息到历史
        self.messages.append({"role": "user", "content": message})
        
        try:
            # 使用流式输出
            response_text = ""
            self.streaming = True
            
            for chunk in self.llm.chat_stream(message, history=self.messages[:-1]):
                if chunk:
                    response_text += chunk
                    if callback:
                        callback(chunk, is_streaming=True)
            
            self.streaming = False
            
            # 添加AI回复到历史
            self.messages.append({"role": "assistant", "content": response_text})
            
            # 限制历史长度
            if len(self.messages) > 20:
                self.messages = self.messages[-20:]
            
            return response_text
            
        except Exception as e:
            self.streaming = False
            error_msg = f"[错误] AI响应失败: {str(e)}"
            print(error_msg)
            return error_msg
    
    def clear_history(self):
        """清空对话历史"""
        self.messages = []
        print("[AI] 对话历史已清空")
    
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
# 全局状态
# ==========================================
class AppState:
    def __init__(self):
        self.current_mode = "ai"
        self.ai_manager = AIChatManager()
        self.kb_files = [
            {"name": "悬臂梁受力分析报告.pdf", "size": "2.4 MB", "status": "indexed"},
            {"name": "材料力学公式手册.docx", "size": "5.1 MB", "status": "indexed"},
            {"name": "齿轮设计规范2024.pdf", "size": "8.7 MB", "status": "indexing"},
        ]
        self.calculation_progress = 0.67
        self.current_response = ""

app_state = AppState()

# ==========================================
# 主题设置
# ==========================================
def setup_themes():
    """设置所有主题"""
    
    # 全局主题
    with dpg.theme() as global_theme:
        with dpg.theme_component(dpg.mvAll):
            dpg.add_theme_color(dpg.mvThemeCol_WindowBg, COLOR_BG_DARK)
            dpg.add_theme_color(dpg.mvThemeCol_ChildBg, COLOR_BG_PANEL)
            dpg.add_theme_color(dpg.mvThemeCol_Border, COLOR_BORDER)
            dpg.add_theme_style(dpg.mvStyleVar_WindowRounding, 8)
            dpg.add_theme_style(dpg.mvStyleVar_ChildRounding, 6)
            dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 4)
            dpg.add_theme_style(dpg.mvStyleVar_WindowBorderSize, 1)
            dpg.add_theme_style(dpg.mvStyleVar_ChildBorderSize, 1)
            dpg.add_theme_style(dpg.mvStyleVar_ItemSpacing, 8, 8)
            dpg.add_theme_style(dpg.mvStyleVar_WindowPadding, 12, 12)
            dpg.add_theme_style(dpg.mvStyleVar_FramePadding, 8, 6)
            dpg.add_theme_color(dpg.mvThemeCol_Text, COLOR_TEXT_PRIMARY)
            dpg.add_theme_color(dpg.mvThemeCol_Button, COLOR_BG_CARD)
            dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, (0, 200, 220, 80))
            dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, COLOR_CYAN_GLOW)
            dpg.add_theme_color(dpg.mvThemeCol_FrameBg, COLOR_BG_CARD)
            dpg.add_theme_color(dpg.mvThemeCol_FrameBgHovered, COLOR_BG_HOVER)
            dpg.add_theme_color(dpg.mvThemeCol_ScrollbarGrab, COLOR_BORDER)
            dpg.add_theme_color(dpg.mvThemeCol_ScrollbarGrabHovered, COLOR_CYAN)
            dpg.add_theme_color(dpg.mvThemeCol_PlotHistogram, COLOR_CYAN)
    
    dpg.bind_theme(global_theme)
    
    # 霓虹按钮主题
    global theme_neon_cyan, theme_neon_purple, theme_neon_error, theme_glass
    global theme_icon_active, theme_icon_inactive, theme_input
    
    with dpg.theme() as theme_neon_cyan:
        with dpg.theme_component(dpg.mvButton):
            dpg.add_theme_color(dpg.mvThemeCol_Button, (0, 30, 35, 200))
            dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, (0, 60, 70, 220))
            dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, (0, 80, 90, 255))
            dpg.add_theme_color(dpg.mvThemeCol_Text, COLOR_CYAN)
            dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 6)
    
    with dpg.theme() as theme_neon_purple:
        with dpg.theme_component(dpg.mvButton):
            dpg.add_theme_color(dpg.mvThemeCol_Button, (35, 20, 50, 200))
            dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, (60, 35, 85, 220))
            dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, (80, 45, 110, 255))
            dpg.add_theme_color(dpg.mvThemeCol_Text, COLOR_PURPLE)
            dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 6)
    
    with dpg.theme() as theme_neon_error:
        with dpg.theme_component(dpg.mvButton):
            dpg.add_theme_color(dpg.mvThemeCol_Button, (50, 20, 20, 200))
            dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, (80, 30, 30, 220))
            dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, (100, 35, 35, 255))
            dpg.add_theme_color(dpg.mvThemeCol_Text, COLOR_ERROR)
            dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 6)
    
    with dpg.theme() as theme_glass:
        with dpg.theme_component(dpg.mvButton):
            dpg.add_theme_color(dpg.mvThemeCol_Button, (255, 255, 255, 15))
            dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, (255, 255, 255, 30))
            dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, (255, 255, 255, 45))
            dpg.add_theme_color(dpg.mvThemeCol_Text, COLOR_TEXT_PRIMARY)
            dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 6)
    
    with dpg.theme() as theme_icon_inactive:
        with dpg.theme_component(dpg.mvButton):
            dpg.add_theme_color(dpg.mvThemeCol_Button, (0, 0, 0, 0))
            dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, (255, 255, 255, 15))
            dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, (255, 255, 255, 25))
            dpg.add_theme_color(dpg.mvThemeCol_Text, COLOR_TEXT_SECONDARY)
            dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 8)
            dpg.add_theme_style(dpg.mvStyleVar_FrameBorderSize, 0)
    
    with dpg.theme() as theme_icon_active:
        with dpg.theme_component(dpg.mvButton):
            dpg.add_theme_color(dpg.mvThemeCol_Button, (0, 245, 255, 30))
            dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, (0, 245, 255, 45))
            dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, (0, 245, 255, 60))
            dpg.add_theme_color(dpg.mvThemeCol_Text, COLOR_CYAN)
            dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 8)
            dpg.add_theme_style(dpg.mvStyleVar_FrameBorderSize, 1)
    
    with dpg.theme() as theme_input:
        with dpg.theme_component(dpg.mvInputText):
            dpg.add_theme_color(dpg.mvThemeCol_FrameBg, COLOR_BG_CARD)
            dpg.add_theme_color(dpg.mvThemeCol_FrameBgHovered, COLOR_BG_HOVER)
            dpg.add_theme_color(dpg.mvThemeCol_Text, COLOR_TEXT_PRIMARY)
            dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 6)
            dpg.add_theme_style(dpg.mvStyleVar_FramePadding, 10, 8)

# ==========================================
# 回调函数
# ==========================================
def switch_mode(sender, app_data, user_data):
    """切换模式"""
    modes = ["mode_ai", "mode_kb", "mode_tool"]
    
    for mode in modes:
        dpg.configure_item(mode, show=False)
    
    dpg.configure_item(user_data["mode"], show=True)
    
    dpg.bind_item_theme("btn_ai", theme_icon_active if user_data["mode"] == "mode_ai" else theme_icon_inactive)
    dpg.bind_item_theme("btn_kb", theme_icon_active if user_data["mode"] == "mode_kb" else theme_icon_inactive)
    dpg.bind_item_theme("btn_tool", theme_icon_active if user_data["mode"] == "mode_tool" else theme_icon_inactive)
    
    app_state.current_mode = user_data["mode"].replace("mode_", "")

def update_ai_response(chunk, is_streaming=False):
    """更新AI流式响应"""
    if is_streaming:
        app_state.current_response += chunk
        # 更新最后一条AI消息
        dpg.set_value("last_ai_response", app_state.current_response)

def send_message_async():
    """异步发送消息"""
    message = dpg.get_value("input_message")
    if not message.strip():
        return
    
    timestamp = datetime.now().strftime("%H:%M")
    
    # 添加用户消息到UI
    with dpg.group(parent="chat_history"):
        dpg.add_text(f"[{timestamp}]  你", color=COLOR_GOLD)
        dpg.add_text("  " + message, color=COLOR_TEXT_PRIMARY, wrap=520)
    dpg.add_spacer(height=8, parent="chat_history")
    
    # 清空输入框
    dpg.set_value("input_message", "")
    
    # 添加AI消息占位
    with dpg.group(parent="chat_history"):
        dpg.add_text(f"[{timestamp}]  MechForge", color=COLOR_CYAN)
        app_state.current_response = "思考中..."
        dpg.add_text(app_state.current_response, color=COLOR_TEXT_SECONDARY, 
                    wrap=520, tag="last_ai_response")
    dpg.add_spacer(height=12, parent="chat_history")
    
    # 滚动到底部
    dpg.set_y_scroll("chat_history", dpg.get_y_scroll_max("chat_history"))
    
    # 在后台线程中调用AI
    def ai_thread():
        response = app_state.ai_manager.send_message(message, callback=update_ai_response)
        # 更新最终响应
        dpg.set_value("last_ai_response", response)
    
    thread = threading.Thread(target=ai_thread, daemon=True)
    thread.start()

def send_message(sender, app_data, user_data):
    """发送消息"""
    send_message_async()

def clear_chat(sender, app_data, user_data):
    """清空聊天"""
    # 删除所有子元素
    for child in dpg.get_item_children("chat_history")[1]:
        dpg.delete_item(child)
    
    # 清空AI历史
    app_state.ai_manager.clear_history()
    
    # 添加欢迎消息
    welcome = """👋 欢迎使用 MechForge AI

我是您的机械工程AI助手，可以帮助您：
• 解答机械设计问题
• 分析CAE仿真结果  
• 检索知识库文档
• 执行工程计算

请输入您的问题开始对话..."""
    dpg.add_text(welcome, color=COLOR_TEXT_SECONDARY, wrap=520, parent="chat_history")
    dpg.add_separator(parent="chat_history")

def add_kb_file(sender, app_data, user_data):
    """添加知识库文件"""
    with dpg.group(parent="kb_file_list"):
        dpg.add_text("📄 新文件.pdf", color=COLOR_CYAN)
        dpg.add_text("   等待索引...", color=COLOR_WARNING)
    dpg.add_separator(parent="kb_file_list")

# ==========================================
# 构建UI
# ==========================================
def build_ui():
    """构建用户界面"""
    
    with dpg.window(tag="main_window", label="", no_title_bar=True, no_resize=True):
        
        # --- 顶部标题栏 ---
        with dpg.group(horizontal=True):
            dpg.add_button(label="◆", width=28, height=28, small=True)
            dpg.bind_item_theme(dpg.last_item(), theme_neon_cyan)
            
            dpg.add_text("  MechForge AI Tool", color=COLOR_CYAN)
            dpg.add_text("  v0.5.0", color=COLOR_TEXT_MUTED)
            
            dpg.add_spacer(width=280)
            
            # AI状态指示
            ai_status = app_state.ai_manager.get_status()
            status_color = COLOR_SUCCESS if ai_status == "就绪" else COLOR_WARNING if ai_status == "生成中..." else COLOR_ERROR
            dpg.add_text(f"AI: {ai_status}", color=status_color)
            
            dpg.add_spacer(width=20)
            
            dpg.add_button(label="─", width=32, height=28, small=True, callback=lambda: dpg.minimize_viewport())
            dpg.bind_item_theme(dpg.last_item(), theme_glass)
            
            dpg.add_button(label="□", width=32, height=28, small=True)
            dpg.bind_item_theme(dpg.last_item(), theme_glass)
            
            dpg.add_button(label="×", width=32, height=28, small=True, callback=lambda: dpg.stop_dearpygui())
            dpg.bind_item_theme(dpg.last_item(), theme_neon_error)
        
        dpg.add_separator()
        
        # --- 主内容区 ---
        with dpg.group(horizontal=True):
            
            # [左侧导航栏]
            with dpg.child_window(width=70, height=-45, border=False):
                dpg.add_spacer(height=10)
                
                # AI模式按钮
                btn_ai = dpg.add_button(label="AI\n对话", width=55, height=55, callback=switch_mode,
                                       user_data={"mode": "mode_ai"})
                dpg.bind_item_theme(btn_ai, theme_icon_active)
                dpg.set_item_alias(btn_ai, "btn_ai")
                dpg.add_spacer(height=8)
                
                # 知识库按钮
                btn_kb = dpg.add_button(label="知识\n库", width=55, height=55, callback=switch_mode,
                                       user_data={"mode": "mode_kb"})
                dpg.bind_item_theme(btn_kb, theme_icon_inactive)
                dpg.set_item_alias(btn_kb, "btn_kb")
                dpg.add_spacer(height=8)
                
                # 工具台按钮
                btn_tool = dpg.add_button(label="工具\n台", width=55, height=55, callback=switch_mode,
                                         user_data={"mode": "mode_tool"})
                dpg.bind_item_theme(btn_tool, theme_icon_inactive)
                dpg.set_item_alias(btn_tool, "btn_tool")
                
                dpg.add_spacer(height=120)
                
                # 清空聊天按钮
                dpg.add_button(label="清空", width=55, height=40, callback=clear_chat)
                dpg.bind_item_theme(dpg.last_item(), theme_glass)
                
                dpg.add_spacer(height=8)
                
                # 设置按钮
                dpg.add_button(label="设置", width=55, height=40)
                dpg.bind_item_theme(dpg.last_item(), theme_glass)
            
            # [右侧主内容区]
            with dpg.child_window(width=-1, height=-45, border=False):
                
                # ===== 模式1: AI对话 =====
                with dpg.group(tag="mode_ai", show=True):
                    with dpg.child_window(height=-60, border=True, tag="chat_history"):
                        dpg.add_text("[系统]  " + datetime.now().strftime("%H:%M"), color=COLOR_TEXT_MUTED)
                        welcome = """👋 欢迎使用 MechForge AI Tool

我是您的机械工程AI助手，可以帮助您：
• 解答机械设计问题
• 分析CAE仿真结果  
• 检索知识库文档
• 执行工程计算

请输入您的问题开始对话..."""
                        dpg.add_text(welcome, color=COLOR_TEXT_SECONDARY, wrap=520)
                        dpg.add_separator()
                    
                    dpg.add_spacer(height=8)
                    
                    with dpg.group(horizontal=True):
                        dpg.add_input_text(tag="input_message", width=-90, hint="输入消息...", 
                                         on_enter=True, callback=send_message)
                        dpg.bind_item_theme(dpg.last_item(), theme_input)
                        
                        dpg.add_button(label="发送", width=80, callback=send_message)
                        dpg.bind_item_theme(dpg.last_item(), theme_neon_cyan)
                
                # ===== 模式2: 知识库 =====
                with dpg.group(tag="mode_kb", show=False):
                    with dpg.group(horizontal=True):
                        dpg.add_input_text(width=-120, hint="搜索文档...")
                        dpg.bind_item_theme(dpg.last_item(), theme_input)
                        
                        dpg.add_button(label="+ 添加文件", width=100, callback=add_kb_file)
                        dpg.bind_item_theme(dpg.last_item(), theme_neon_purple)
                    
                    dpg.add_spacer(height=10)
                    
                    with dpg.group(horizontal=True):
                        dpg.add_text("索引状态:", color=COLOR_TEXT_SECONDARY)
                        dpg.add_button(label="", width=8, height=8, small=True)
                        dpg.bind_item_theme(dpg.last_item(), theme_icon_active)
                        dpg.add_text("运行中  |  42 文件  |  1.8 GB", color=COLOR_TEXT_PRIMARY)
                    
                    dpg.add_spacer(height=8)
                    
                    with dpg.child_window(height=-1, border=True, tag="kb_file_list"):
                        for file in app_state.kb_files:
                            dpg.add_text(f"📄 {file['name']}", color=COLOR_CYAN)
                            dpg.add_text(f"   {file['size']}", color=COLOR_TEXT_MUTED)
                            if file["status"] == "indexed":
                                dpg.add_text("   ✓ 已索引", color=COLOR_SUCCESS)
                            else:
                                dpg.add_text("   ⏳ 索引中...", color=COLOR_WARNING)
                                dpg.add_progress_bar(default_value=0.45, width=100)
                            dpg.add_separator()
                
                # ===== 模式3: 工具台 =====
                with dpg.group(tag="mode_tool", show=False):
                    with dpg.group(horizontal=True):
                        dpg.add_button(label="➕ 新建计算")
                        dpg.bind_item_theme(dpg.last_item(), theme_neon_cyan)
                        
                        dpg.add_button(label="📂 导入几何")
                        dpg.bind_item_theme(dpg.last_item(), theme_glass)
                        
                        dpg.add_button(label="🔲 网格划分")
                        dpg.bind_item_theme(dpg.last_item(), theme_glass)
                        
                        dpg.add_button(label="▶ 求解")
                        dpg.bind_item_theme(dpg.last_item(), theme_neon_purple)
                    
                    dpg.add_spacer(height=12)
                    
                    with dpg.child_window(height=60, border=True):
                        dpg.add_text("Gmsh 网格生成中...", color=COLOR_TEXT_PRIMARY)
                        dpg.add_progress_bar(default_value=app_state.calculation_progress, 
                                           width=-1, overlay=f"{int(app_state.calculation_progress*100)}%")
                    
                    dpg.add_spacer(height=12)
                    
                    with dpg.group(horizontal=True):
                        with dpg.child_window(width=280, height=-1, border=True):
                            dpg.add_text("📋 计算日志", color=COLOR_CYAN)
                            dpg.add_separator()
                            logs = [
                                "[INFO] Reading STEP file...",
                                "[INFO] Surface meshing completed",
                                "[INFO] Volume meshing: 67%",
                                "[WARN] High aspect ratio detected",
                                "[INFO] Optimizing mesh quality...",
                            ]
                            for log in logs:
                                if "WARN" in log:
                                    dpg.add_text(log, color=COLOR_WARNING)
                                else:
                                    dpg.add_text(log, color=COLOR_TEXT_SECONDARY)
                        
                        with dpg.child_window(width=-1, height=-1, border=True):
                            dpg.add_text("🔮 3D 预览", color=COLOR_CYAN)
                            dpg.add_separator()
                            dpg.add_text("网格节点: 45,230", color=COLOR_TEXT_SECONDARY)
                            dpg.add_text("单元数量: 182,456", color=COLOR_TEXT_SECONDARY)
                            dpg.add_text("质量评分: 8.4/10", color=COLOR_SUCCESS)
                            
                            with dpg.drawlist(width=-1, height=180):
                                cx, cy = 150, 90
                                size = 50
                                pts = [
                                    (cx-size, cy-size//2), (cx+size, cy-size//2),
                                    (cx+size+25, cy-size//2-25), (cx-size+25, cy-size//2-25)
                                ]
                                for i in range(4):
                                    dpg.draw_line(pts[i], pts[(i+1)%4], color=COLOR_CYAN, thickness=2)
                                    dpg.draw_line((pts[i][0], pts[i][1]+size), 
                                                (pts[(i+1)%4][0], pts[(i+1)%4][1]+size), 
                                                color=COLOR_CYAN, thickness=2)
                                    dpg.draw_line(pts[i], (pts[i][0], pts[i][1]+size), 
                                                color=COLOR_CYAN_DIM, thickness=1)
        
        # --- 底部状态栏 ---
        dpg.add_separator()
        with dpg.child_window(height=35, border=False):
            with dpg.group(horizontal=True):
                dpg.add_text("⚡ MechForge Tool  |  ", color=COLOR_CYAN)
                dpg.add_text("API: Ollama  |  ", color=COLOR_TEXT_SECONDARY)
                dpg.add_text("模型: qwen2.5:3b  |  ", color=COLOR_TEXT_PRIMARY)
                dpg.add_text("RAG: ON  |  ", color=COLOR_SUCCESS)
                dpg.add_text("KB: 42 文件", color=COLOR_TEXT_PRIMARY)
                
                dpg.add_spacer(width=100)
                
                dpg.add_button(label="日志", width=50, height=22, small=True)
                dpg.bind_item_theme(dpg.last_item(), theme_glass)
                dpg.add_button(label="暂停", width=50, height=22, small=True)
                dpg.bind_item_theme(dpg.last_item(), theme_glass)

# ==========================================
# 主程序
# ==========================================
def main():
    dpg.create_context()
    
    # ==========================================
    # 字体注册与加载（支持中文）
    # ==========================================
    with dpg.font_registry():
        # Windows系统使用微软雅黑
        font_path = "C:/Windows/Fonts/msyh.ttc"
        
        # 检查字体文件是否存在
        if os.path.exists(font_path):
            # 参数16是字体大小（像素）
            with dpg.font(font_path, 16) as default_font:
                # 加载常用中文字符集
                dpg.add_font_range_hint(dpg.mvFontRangeHint_Chinese_Simplified_Common)
                # 额外加载默认字符集（英文、数字、符号）
                dpg.add_font_range_hint(dpg.mvFontRangeHint_Default)
            
            # 将加载的字体绑定为全局默认字体
            dpg.bind_font(default_font)
            print(f"[字体] 成功加载: {font_path}")
        else:
            print(f"[警告] 找不到字体文件: {font_path}")
            # 尝试备用字体
            backup_fonts = [
                "C:/Windows/Fonts/simhei.ttf",  # 黑体
                "C:/Windows/Fonts/simsun.ttc",  # 宋体
                "C:/Windows/Fonts/segoeui.ttf", # Segoe UI
            ]
            for backup in backup_fonts:
                if os.path.exists(backup):
                    with dpg.font(backup, 16) as default_font:
                        dpg.add_font_range_hint(dpg.mvFontRangeHint_Chinese_Simplified_Common)
                        dpg.add_font_range_hint(dpg.mvFontRangeHint_Default)
                    dpg.bind_font(default_font)
                    print(f"[字体] 使用备用字体: {backup}")
                    break
    
    # 设置主题
    setup_themes()
    
    # 构建UI
    build_ui()
    
    # 创建视口
    dpg.create_viewport(
        title='MechForge AI Tool',
        width=850,
        height=700,
        resizable=True,
        min_width=700,
        min_height=500,
        vsync=True,
        clear_color=COLOR_BG_DARK
    )
    
    dpg.setup_dearpygui()
    dpg.show_viewport()
    dpg.set_primary_window("main_window", True)
    
    # 主循环
    while dpg.is_dearpygui_running():
        dpg.render_dearpygui_frame()
    
    dpg.destroy_context()

if __name__ == "__main__":
    main()
