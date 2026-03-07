import dearpygui.dearpygui as dpg

dpg.create_context()

# ==========================================
# 1. 核心色彩与主题定义 (赛博机械霓虹风格)
# ==========================================
NAVY_BG = (12, 16, 26, 255)        # 极深海军蓝
PANEL_BG = (18, 24, 38, 255)       # 面板背景色
CYAN_NEON = (0, 255, 230, 255)     # 青色霓虹
CYAN_DIM = (0, 255, 230, 80)       # 黯淡青色 (用于边框/非活跃)
PURPLE_GLOW = (150, 50, 255, 200)  # 紫色渐变替代色 (用于活跃/强调)
TEXT_COLD = (200, 230, 240, 255)   # 冷白带青字体

with dpg.theme() as global_theme:
    with dpg.theme_component(dpg.mvAll):
        # 窗口与背景
        dpg.add_theme_color(dpg.mvThemeCol_WindowBg, NAVY_BG)
        dpg.add_theme_color(dpg.mvThemeCol_ChildBg, PANEL_BG)
        dpg.add_theme_color(dpg.mvThemeCol_Border, CYAN_DIM)
        dpg.add_theme_style(dpg.mvStyleVar_WindowBorderSize, 1)
        dpg.add_theme_style(dpg.mvStyleVar_ChildBorderSize, 1)
        dpg.add_theme_style(dpg.mvStyleVar_WindowRounding, 4)
        dpg.add_theme_style(dpg.mvStyleVar_ChildRounding, 4)
        
        # 文本
        dpg.add_theme_color(dpg.mvThemeCol_Text, TEXT_COLD)
        
        # 按钮状态 (模拟通电与发光)
        dpg.add_theme_color(dpg.mvThemeCol_Button, (25, 35, 55, 255))
        dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, CYAN_DIM)
        dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, PURPLE_GLOW)
        dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 3)
        dpg.add_theme_style(dpg.mvStyleVar_ItemSpacing, 4, 8)

dpg.bind_theme(global_theme)

# ==========================================
# 2. 交互逻辑：左侧导航切换
# ==========================================
def switch_mode(sender, app_data, user_data):
    modes = ["mode_ai", "mode_kb", "mode_tool"]
    for mode in modes:
        dpg.configure_item(mode, show=False)
    dpg.configure_item(user_data, show=True)

# ==========================================
# 3. 界面构建
# ==========================================
with dpg.window(tag="main_window"):
    
    # --- 顶部：伪标题栏 (极简) ---
    with dpg.group(horizontal=True):
        dpg.add_text("MechForge AI", color=CYAN_NEON)
        # 实际使用中，右上角三按钮通常由OS接管，或者需要无边框窗口配合自定义拖拽
        
    dpg.add_spacer(height=2)
    dpg.add_separator()
    dpg.add_spacer(height=2)

    # --- 中部：左侧导航 + 主内容区 ---
    with dpg.group(horizontal=True):
        
        # [左侧窄导航] - 70px 宽
        with dpg.child_window(width=70, height=450, border=True):
            # 使用文字模拟图标，实际可加载图片纹理代替
            dpg.add_button(label="[ AI ]", width=55, height=55, callback=switch_mode, user_data="mode_ai")
            dpg.add_button(label="[ KB ]", width=55, height=55, callback=switch_mode, user_data="mode_kb")
            dpg.add_button(label="[TOOL]", width=55, height=55, callback=switch_mode, user_data="mode_tool")
            dpg.add_spacer(height=200)
            dpg.add_button(label="[SET]", width=55, height=55) # 设置占位
            
        # [中央主内容区]
        with dpg.child_window(width=-1, height=450, border=False):
            
            # 模式1: AI 模式 (默认显示)
            with dpg.group(tag="mode_ai", show=True):
                with dpg.child_window(height=-40, border=True):
                    dpg.add_text("输入工程问题开始对话", color=(100, 120, 140, 255))
                    # 这里是聊天气泡的占位
                    dpg.add_text("> 机械臂小头像: \n您好，今日需要进行哪种材料的应力分析？", color=CYAN_NEON)
                    dpg.add_text("深紫玻璃泡: \n帮我调出昨天的悬臂梁模型。", color=PURPLE_GLOW, indent=50)
                
                with dpg.group(horizontal=True):
                    dpg.add_input_text(width=-60, hint="Send a message...")
                    dpg.add_button(label="Send", width=50)

            # 模式2: 知识库模式 (默认隐藏)
            with dpg.group(tag="mode_kb", show=False):
                with dpg.group(horizontal=True):
                    dpg.add_input_text(width=-100, hint="Search documents...")
                    dpg.add_button(label="+ 添加", width=80)
                dpg.add_spacer(height=5)
                # 模拟索引进度
                dpg.add_progress_bar(default_value=0.67, overlay="索引中... 17M/s", width=-1)
                dpg.add_spacer(height=5)
                # 模拟列表卡片
                with dpg.child_window(height=-30, border=True):
                    for i in range(3):
                        dpg.add_text(f"悬臂梁受力分析报告_v{i}.pdf", color=CYAN_NEON)
                        dpg.add_text("...最大挠度集中在末端，符合杨氏模量预期...", color=(150, 160, 170, 255))
                        dpg.add_progress_bar(default_value=0.9-i*0.2, overlay="相关度", width=100)
                        dpg.add_separator()
                dpg.add_text("已索引 42 文件 · 1.8 GB · 最后更新 3 分钟前", color=(100, 120, 140, 255))

            # 模式3: 工具台模式 (默认隐藏)
            with dpg.group(tag="mode_tool", show=False):
                with dpg.group(horizontal=True):
                    dpg.add_button(label="新建计算")
                    dpg.add_button(label="导入几何")
                    dpg.add_button(label="网格划分")
                    dpg.add_button(label="求解 & 可视化")
                dpg.add_spacer(height=10)
                # 大进度条
                dpg.add_progress_bar(default_value=0.67, overlay="Gmsh 网格生成中... 67% (剩余 12s)", width=-1)
                dpg.add_spacer(height=10)
                
                with dpg.group(horizontal=True):
                    # 左侧输出区
                    with dpg.child_window(width=250, border=True):
                        dpg.add_text("计算日志:\n[INFO] Reading step file...\n[INFO] Meshing surface...\n[WARN] High aspect ratio detected.", color=TEXT_COLD)
                    # 右侧 PyVista 预览区 (占位)
                    with dpg.child_window(width=-1, border=True):
                        # 在DPG中嵌入PyVista需要将PyVista渲染为图像并作为Texture加载
                        dpg.add_text("[ 3D 渲染视图占位 ]\n(此处接入 PyVista 图像流)", color=CYAN_DIM)

    # --- 底部状态栏 --- (45px)
    dpg.add_spacer(height=5)
    with dpg.child_window(height=40, border=True):
        with dpg.group(horizontal=True):
            dpg.add_text("[MechForge] >", color=CYAN_NEON)
            dpg.add_text("API: Ollama | 模型: qwen2.5:3b | RAG: ON | KB: 42 文件 | v0.5.0", color=(150, 170, 190, 255))
            # 靠右对齐的模拟
            dpg.add_spacer(width=80)
            dpg.add_button(label="Log")
            dpg.add_button(label="Pause")

# ==========================================
# 4. 视口与渲染配置
# ==========================================
dpg.create_viewport(title='MechForge AI', width=720, height=580, resizable=False)
dpg.setup_dearpygui()
dpg.show_viewport()
dpg.set_primary_window("main_window", True)
dpg.start_dearpygui()
dpg.destroy_context()