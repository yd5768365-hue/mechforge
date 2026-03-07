#!/usr/bin/env python3
"""
MechForge AI - 美化版界面框架
赛博朋克机械风格 + 现代UI设计
"""

import dearpygui.dearpygui as dpg
from datetime import datetime

# ==========================================
# 1. 精致配色方案 (赛博朋克机械风)
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
# 2. 全局主题和样式
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
    global theme_neon_cyan
    with dpg.theme() as theme_neon_cyan:
        with dpg.theme_component(dpg.mvButton):
            dpg.add_theme_color(dpg.mvThemeCol_Button, (0, 30, 35, 200))
            dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, (0, 60, 70, 220))
            dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, (0, 80, 90, 255))
            dpg.add_theme_color(dpg.mvThemeCol_Text, COLOR_CYAN)
            dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 6)
    
    global theme_neon_purple
    with dpg.theme() as theme_neon_purple:
        with dpg.theme_component(dpg.mvButton):
            dpg.add_theme_color(dpg.mvThemeCol_Button, (35, 20, 50, 200))
            dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, (60, 35, 85, 220))
            dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, (80, 45, 110, 255))
            dpg.add_theme_color(dpg.mvThemeCol_Text, COLOR_PURPLE)
            dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 6)
    
    global theme_neon_error
    with dpg.theme() as theme_neon_error:
        with dpg.theme_component(dpg.mvButton):
            dpg.add_theme_color(dpg.mvThemeCol_Button, (50, 20, 20, 200))
            dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, (80, 30, 30, 220))
            dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, (100, 35, 35, 255))
            dpg.add_theme_color(dpg.mvThemeCol_Text, COLOR_ERROR)
            dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 6)
    
    # 玻璃按钮主题
    global theme_glass
    with dpg.theme() as theme_glass:
        with dpg.theme_component(dpg.mvButton):
            dpg.add_theme_color(dpg.mvThemeCol_Button, (255, 255, 255, 15))
            dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, (255, 255, 255, 30))
            dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, (255, 255, 255, 45))
            dpg.add_theme_color(dpg.mvThemeCol_Text, COLOR_TEXT_PRIMARY)
            dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 6)
    
    # 图标按钮主题 - 非激活
    global theme_icon_inactive
    with dpg.theme() as theme_icon_inactive:
        with dpg.theme_component(dpg.mvButton):
            dpg.add_theme_color(dpg.mvThemeCol_Button, (0, 0, 0, 0))
            dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, (255, 255, 255, 15))
            dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, (255, 255, 255, 25))
            dpg.add_theme_color(dpg.mvThemeCol_Text, COLOR_TEXT_SECONDARY)
            dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 8)
            dpg.add_theme_style(dpg.mvStyleVar_FrameBorderSize, 0)
    
    # 图标按钮主题 - 激活
    global theme_icon_active
    with dpg.theme() as theme_icon_active:
        with dpg.theme_component(dpg.mvButton):
            dpg.add_theme_color(dpg.mvThemeCol_Button, (0, 245, 255, 30))
            dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, (0, 245, 255, 45))
            dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, (0, 245, 255, 60))
            dpg.add_theme_color(dpg.mvThemeCol_Text, COLOR_CYAN)
            dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 8)
            dpg.add_theme_style(dpg.mvStyleVar_FrameBorderSize, 1)
    
    # 输入框主题
    global theme_input
    with dpg.theme() as theme_input:
        with dpg.theme_component(dpg.mvInputText):
            dpg.add_theme_color(dpg.mvThemeCol_FrameBg, COLOR_BG_CARD)
            dpg.add_theme_color(dpg.mvThemeCol_FrameBgHovered, COLOR_BG_HOVER)
            dpg.add_theme_color(dpg.mvThemeCol_Text, COLOR_TEXT_PRIMARY)
            dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 6)
            dpg.add_theme_style(dpg.mvStyleVar_FramePadding, 10, 8)

# ==========================================
# 3. 应用状态
# ==========================================
class AppState:
    def __init__(self):
        self.current_mode = "ai"
        self.kb_files = [
            {"name": "悬臂梁受力分析报告.pdf", "size": "2.4 MB", "status": "indexed"},
            {"name": "材料力学公式手册.docx", "size": "5.1 MB", "status": "indexed"},
            {"name": "齿轮设计规范2024.pdf", "size": "8.7 MB", "status": "indexing"},
        ]
        self.calculation_progress = 0.67

app_state = AppState()

# ==========================================
# 4. 回调函数
# ==========================================
def switch_mode(sender, app_data, user_data):
    """切换模式"""
    modes = ["mode_ai", "mode_kb", "mode_tool"]
    
    for mode in modes:
        dpg.configure_item(mode, show=False)
    
    dpg.configure_item(user_data["mode"], show=True)
    
    # 更新按钮样式
    dpg.bind_item_theme("btn_ai", theme_icon_inactive if user_data["mode"] != "mode_ai" else theme_icon_active)
    dpg.bind_item_theme("btn_kb", theme_icon_inactive if user_data["mode"] != "mode_kb" else theme_icon_active)
    dpg.bind_item_theme("btn_tool", theme_icon_inactive if user_data["mode"] != "mode_tool" else theme_icon_active)
    
    app_state.current_mode = user_data["mode"].replace("mode_", "")

def send_message(sender, app_data, user_data):
    """发送消息"""
    message = dpg.get_value("input_message")
    if message.strip():
        timestamp = datetime.now().strftime("%H:%M")
        
        # 用户消息
        with dpg.group(parent="chat_history", horizontal=True):
            dpg.add_text(f"[{timestamp}]", color=COLOR_TEXT_MUTED)
            dpg.add_text(" 你", color=COLOR_GOLD)
        dpg.add_text("  " + message, color=COLOR_TEXT_PRIMARY, parent="chat_history", wrap=500)
        dpg.add_spacer(height=8, parent="chat_history")
        
        dpg.set_value("input_message", "")
        
        # AI回复
        with dpg.group(parent="chat_history", horizontal=True):
            dpg.add_text(f"[{timestamp}]", color=COLOR_TEXT_MUTED)
            dpg.add_text(" MechForge", color=COLOR_CYAN)
        dpg.add_text("  收到您的消息，正在分析...", color=COLOR_TEXT_SECONDARY, parent="chat_history", wrap=500)
        dpg.add_spacer(height=12, parent="chat_history")
        
        dpg.set_y_scroll("chat_history", dpg.get_y_scroll_max("chat_history"))

def add_kb_file(sender, app_data, user_data):
    """添加知识库文件"""
    with dpg.group(parent="kb_file_list"):
        dpg.add_text("📄 新文件.pdf", color=COLOR_CYAN)
        dpg.add_text("   等待索引...", color=COLOR_WARNING)
    dpg.add_separator(parent="kb_file_list")

# ==========================================
# 5. 构建UI
# ==========================================
def build_ui():
    """构建用户界面"""
    
    with dpg.window(tag="main_window", label="", no_title_bar=True, no_resize=True):
        
        # --- 顶部标题栏 ---
        with dpg.group(horizontal=True):
            dpg.add_button(label="◆", width=28, height=28, small=True)
            dpg.bind_item_theme(dpg.last_item(), theme_neon_cyan)
            
            dpg.add_text("  MechForge AI", color=COLOR_CYAN)
            dpg.add_text("  v0.5.0", color=COLOR_TEXT_MUTED)
            
            dpg.add_spacer(width=320)
            
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
                
                dpg.add_spacer(height=150)
                
                # 设置按钮
                btn_settings = dpg.add_button(label="设置", width=55, height=40)
                dpg.bind_item_theme(btn_settings, theme_glass)
            
            # [右侧主内容区]
            with dpg.child_window(width=-1, height=-45, border=False):
                
                # ===== 模式1: AI对话 =====
                with dpg.group(tag="mode_ai", show=True):
                    with dpg.child_window(height=-60, border=True, tag="chat_history"):
                        dpg.add_text("[系统]  " + datetime.now().strftime("%H:%M"), color=COLOR_TEXT_MUTED)
                        welcome = """👋 欢迎使用 MechForge AI

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
                                # 简单3D立方体线框
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
                dpg.add_text("⚡ MechForge  |  ", color=COLOR_CYAN)
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
# 6. 主程序
# ==========================================
def main():
    dpg.create_context()
    
    # 设置主题
    setup_themes()
    
    # 构建UI
    build_ui()
    
    # 创建视口
    dpg.create_viewport(
        title='MechForge AI',
        width=800,
        height=650,
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
