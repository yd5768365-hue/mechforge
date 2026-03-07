# MechForge AI 开发日志

## 2026年3月7日

### 改进：统一Python环境配置
- **实现者**：Qwen Code
- **问题描述**：项目缺乏统一的Python环境配置，不同开发者可能使用不同Python版本和依赖，导致兼容性问题
- **解决方法**：
  1. **指定Python版本** (`.python-version`): 指定Python 3.12为推荐版本
  2. **创建环境设置脚本**: `setup_env.bat` (Windows) / `setup_env.sh` (Linux/Mac)
  3. **创建快速激活脚本**: `activate.bat` / `activate.sh`
  4. **生成requirements.txt**: 锁定所有依赖版本
  5. **创建Makefile**: 简化常用开发任务
  6. **创建环境检查脚本** (`check_env.py`): 全面检查环境配置
- **新增文件**: `.python-version`, `setup_env.bat`, `setup_env.sh`, `activate.bat`, `activate.sh`, `requirements.txt`, `Makefile`, `check_env.py`
- **使用方法**: `setup_env.bat` (首次设置) / `activate.bat` (快速激活) / `make install-all` / `python check_env.py`
- **解决效果**: 统一Python 3.12环境，自动化环境配置，简化开发流程，支持多平台

---

### 新增功能：AI自我反思与提升技能 (Self-Reflection Skill)
- **实现者**：Qwen Code
- **功能描述**：为AI设计了一个完整的自我反思与提升系统，让AI能够从交互中学习、记录经验、持续优化自身表现
- **核心组件**：
  1. **交互日志记录器 (ReflectionLogger)**：
     - 记录每次AI交互的完整信息（输入、输出、结果、反馈）
     - 按日期自动组织存储在 `~/.mechforge/reflections/interactions/`
     - 支持用户反馈和结果标记
  
  2. **反思分析引擎 (ReflectionEngine)**：
     - 自动分析任务成功/失败原因
     - 识别5种错误类型：理解错误、知识缺失、逻辑错误、格式问题、上下文限制
     - 生成改进策略和成功经验
     - 从反思中提取可复用的经验教训
  
  3. **经验库管理 (ExperienceDB)**：
     - 存储和管理提取的经验教训
     - 支持关键词搜索和相关性检索
     - 跟踪经验应用次数和成功率
     - 自动合并相似经验
  
  4. **报告生成器 (ReflectionReporter)**：
     - 生成日报、周报、月报
     - 分析错误类型分布和改进趋势
     - 提供系统级优化建议
  
  5. **集成工具 (Integration)**：
     - `@with_reflection` 装饰器自动记录函数调用
     - `ReflectionMixin` 类为现有类添加反思能力
     - `ReflectionAwareLLM` 包装器自动增强提示词

- **文件结构**：
  ```
  mechforge_core/reflection/
  ├── __init__.py          # 模块导出
  ├── models.py            # 数据模型（Pydantic）
  ├── logger.py            # 交互日志记录
  ├── engine.py            # 反思分析引擎
  ├── experience_db.py     # 经验库管理
  ├── reporter.py          # 报告生成
  ├── cli.py               # 命令行接口
  └── integration.py       # 集成工具
  ```

- **Skill配置**：
  - 路径：`.qwen/skills/self-reflection/SKILL.md`
  - 触发条件：完成复杂任务后、用户提及"反思"或"总结"、遇到重复错误、会话结束时

- **使用示例**：
  ```python
  # 基础用法
  from mechforge_core.reflection import ReflectionLogger, ReflectionEngine
  logger = ReflectionLogger()
  log_id = logger.log_interaction(task_description="...", user_input="...", ai_output="...", result="success")
  engine = ReflectionEngine()
  reflection = engine.reflect_on_task(log)
  
  # 装饰器自动记录
  @with_reflection(task_type="coding")
  def generate_code(prompt):
      return ai.generate(prompt)
  
  # CLI命令
  python -m mechforge_core.reflection log --task "..." --input "..." --output "..."
  python -m mechforge_core.reflection review --limit 20
  python -m mechforge_core.reflection report --period weekly
  ```

- **实现效果**：
  - AI能够记录自己的错误并从中学到改进方法
  - 形成可复用的经验库，提升后续任务成功率
  - 生成周期性报告，展示改进趋势
  - 与MechForge现有模块（RAG、CAE、AI对话）可无缝集成

---

## 2026年3月10日（补充）

### 问题6：打包 GUI-AI 版本
- **发现者**：小夏
- **问题描述**：需要将 GUI 版本打包为独立的 Windows 可执行文件（.exe），方便用户直接使用
- **解决方法**：
  1. **创建轻量版打包脚本** (`build_gui_light.py`)：
     - 使用 PyInstaller 打包为单文件 exe
     - 排除大型依赖（torch、transformers、sklearn、pandas 等）
     - 仅包含核心功能：PySide6、Rich、Pydantic、Requests
  2. **打包配置**：
     - `--onefile`：单文件输出
     - `--windowed`：无控制台窗口
     - `--exclude-module`：排除不需要的模块
     - `--hidden-import`：添加隐藏导入
  3. **输出文件**：
     - 路径：`D:\mechforge_ai\dist\MechForge.exe`
     - 大小：约 71 MB（轻量版）
- **功能说明**：
  - ✅ 完整的 GUI 界面功能
  - ✅ AI 对话（OpenAI/Anthropic API）
  - ✅ 知识库 RAG 检索（需单独安装知识库模块）
  - ❌ 本地模型支持（GGUF/Ollama）- 需完整版
- **解决效果**：
  - 用户可直接运行 MechForge.exe，无需安装 Python
  - 文件大小适中（71 MB），便于分发
  - 启动速度快，资源占用低

---

### 问题5：GUI 字体升级 - 科幻控制台风格
- **发现者**：小夏
- **问题描述**：界面字体需要更符合科幻控制台风格，提升视觉体验
- **解决方法**：
  1. **更新字体配置** (`theme.py`)：
     - `FONT_FAMILY_TITLE` = "Orbitron" - 标题字体（科幻硬朗）
     - `FONT_FAMILY_UI` = "Rajdhani" - UI 按钮字体（短小精悍）
     - `FONT_FAMILY_TERMINAL` = "Share Tech Mono" - 终端提示文字（打字机感）
     - `FONT_FAMILY_CN` = "Noto Sans SC" - 中文字体（思源黑体）
     - `FONT_FAMILY` = "JetBrains Mono" - 代码/消息字体
  2. **应用新字体** (`main_window.py`)：
     - 标题 "MechForge AI" → Orbitron
     - 按钮文字（新建、清空、RAG、帮助）→ Rajdhani
     - 欢迎词内容 → Share Tech Mono
     - 中文副标题 → Noto Sans SC
     - 消息气泡、输入框、状态栏 → JetBrains Mono
- **字体搭配效果**：
  - 标题：硬朗科幻感，品牌识别度高
  - 按钮：紧凑干练，不占空间
  - 终端文字：打字机感，命令行氛围
  - 中文：与英文科技字体协调，不突兀
- **解决效果**：
  - 界面整体呈现科幻控制台风格
  - 字体层次分明，视觉体验提升
  - 中英文搭配协调，阅读舒适

---

## 2026年3月10日（补充）

### 问题4：RAG 功能支持用户选择知识库文件夹
- **发现者**：小夏
- **问题描述**：用户希望自由选择知识库文件夹位置，而不是限制在固定路径
- **解决方法**：
  1. 添加 `_select_knowledge_folder()` 方法，使用 `QFileDialog` 让用户选择文件夹
  2. 添加 `_has_documents()` 方法检查文件夹是否包含文档
  3. 添加 `_create_sample_document()` 方法创建示例文档
  4. 添加 `_save_knowledge_path()` 方法保存用户选择到配置
  5. 修改 `_toggle_rag()` 逻辑：
     - 如果没有找到知识库，自动弹出选择对话框
     - 用户选择后保存路径并重新初始化 RAG 引擎
     - 空文件夹可创建示例文档
- **用户体验流程**：
  1. 点击 RAG 按钮
  2. 如果未找到知识库，提示选择文件夹
  3. 打开系统文件夹选择对话框
  4. 选择后检查是否有文档
  5. 空文件夹可选择创建示例文档
  6. 路径保存到配置，下次自动使用
- **解决效果**：
  - 用户可自由选择知识库位置
  - 配置持久化，下次启动自动加载
  - 提供示例文档，降低使用门槛

---

### 问题3：修复欢迎词显示不清和 RAG 按钮无反应
- **发现者**：小夏
- **问题描述**：
  1. 欢迎词在内容较多时显示不清楚（使用 QLabel 导致）
  2. 点击 RAG 按钮后没有任何反应
- **原因分析**：
  1. QLabel 对多行长文本支持不好，文字容易重叠或截断
  2. RAG 按钮逻辑复杂，依赖 rag_engine 初始化，容易静默失败
- **解决方法**：
  1. **欢迎词**：改用 QTextEdit 显示内容，支持滚动，文字更清晰
  2. **RAG 按钮**：
     - 简化逻辑，直接使用 `find_knowledge_path()` 检查路径
     - 添加多个检查点：模块安装 → 路径存在 → 有文档文件
     - 每个检查点失败都弹出明确的 QMessageBox 提示
     - RAG 状态切换改为在状态栏显示（不添加系统消息）
- **解决效果**：
  - 欢迎词长文本清晰可读，支持滚动
  - RAG 按钮点击有明确反馈，用户知道问题所在

---

### 问题2：GUI RAG 按钮添加知识库模块检查
- **发现者**：小夏
- **问题描述**：用户点击 GUI 中的 RAG 按钮时，如果未安装知识库模块（mechforge-knowledge），会静默失败或显示不友好的错误信息
- **解决方法**：
  1. 在 `_toggle_rag()` 方法中添加模块检查逻辑
  2. 创建 `_check_knowledge_module()` 方法检查 `mechforge_knowledge` 是否可导入
  3. 如果未安装，弹出 QMessageBox 提示对话框，显示：
     - 问题说明：知识库模块未安装
     - 安装命令：`pip install mechforge-ai[rag]` 或 `pip install mechforge-ai[all]`
  4. 对话框样式匹配 GUI 主题（深空蓝背景、星光青按钮）
  5. 只有安装模块后才允许启用 RAG 功能
- **解决效果**：
  - 用户点击 RAG 按钮时，未安装会收到清晰的安装指引
  - 提供具体的 pip 安装命令，降低用户使用门槛
  - 界面风格统一，体验更友好

---

### 问题1：统一 AI 模式和知识库模式的知识库来源
- **发现者**：小夏
- **问题描述**：AI 模式（mechforge-ai）和知识库模式（mechforge-k）使用不同的逻辑查找知识库路径，导致两个模式可能使用不同的知识库来源
- **原因分析**：
  - 知识库模式有 `_find_knowledge_path()` 函数，按优先级搜索多个路径
  - AI 模式的 RAG 引擎直接从配置文件获取路径，没有搜索逻辑
  - 两个模式的路径查找逻辑不一致
- **解决方法**：
  1. 在 `mechforge_core.config` 中创建统一的 `find_knowledge_path()` 函数
  2. 更新知识库模式 (`mechforge_knowledge/cli.py`) 使用统一函数
  3. 更新 AI 模式的 RAG 引擎 (`mechforge_ai/rag_engine.py`) 使用统一函数
  4. 更新终端模式 (`mechforge_ai/terminal.py`) 使用统一函数
  5. GUI 模式通过 RAGEngine 自动使用统一函数
- **统一路径搜索优先级**：
  1. 配置文件中的 `knowledge.path`
  2. 项目根目录的 `knowledge` 文件夹
  3. 项目根目录的 `data/knowledge` 文件夹
  4. 用户配置目录的 `.mechforge/knowledge` 文件夹
  5. 当前工作目录的 `knowledge` 文件夹
- **解决效果**：
  - AI 模式和知识库模式使用完全一致的知识库来源
  - 代码复用性提升，维护更简单
  - 用户体验一致，无论在哪个模式都能访问相同的知识库

---

## 2026年3月9日（补充）

### 问题3：修复欢迎词无法正常显示（简化版）
- **发现者**：小夏
- **问题描述**：欢迎词的打字机动画无法正常显示内容，用户看不到欢迎信息
- **原因分析**：
  - `QTextEdit.setHtml()` 在打字过程中频繁调用会导致内容重置和闪烁
  - 复杂的动画逻辑容易出错
- **解决方法**：
  1. **彻底简化**：移除所有打字机动画相关代码
  2. 使用简单的 `QLabel` 直接显示静态文本
  3. 移除发光效果等复杂图形效果
  4. 保留用户发送第一条消息后自动移除的逻辑
- **解决效果**：
  - 欢迎词立即显示，稳定可靠
  - 代码简洁，维护性提升
  - 用户发送第一条消息后自动移除

---

### 问题2：GUI 界面精致重构 - Modern Dark Glassmorphism
- **发现者**：小夏
- **问题描述**：基于用户提供的精致设计规范，全面重构 GUI 界面，提升视觉品质和用户体验
- **解决方法**：
  1. **主题系统升级** (`theme.py`)：
     - 新配色：深空蓝渐变 (#070D1A → #0F172A)
     - 星光青强调色 (#22D3EE) 替代电光青，更精致柔和
     - 添加 UI 字体变量 `FONT_FAMILY_UI` (Segoe UI)
     - 新增圆角半径配置 `RADIUS`
     - 全面更新样式表，更现代的控件风格
  2. **主窗口重构** (`main_window.py`)：
     - **Banner 标题栏**：精致玻璃态渐变 + 胶囊按钮工具栏
     - **消息气泡**：更克制的配色、圆角优化、最大宽度限制
     - **头像设计**：AI/ME/SYS 文字头像替代符号，更专业
     - **输入区域**：玻璃态容器 + 渐变发送按钮 + `>_` 提示符
     - **状态栏**：Chip 指示器风格，精致状态点
     - **欢迎卡片**：更淡的发光效果、更舒适的间距
     - **背景网格**：降低不透明度至 14，更克制优雅
  3. **对话框更新** (`dialogs.py`)：
     - 保持与新主题一致
- **解决效果**：
  - 界面整体更精致、现代、专业
  - 视觉层次更清晰，交互元素更突出
  - 配色更柔和舒适，长时间使用不易疲劳
  - 代码结构更清晰，维护性提升

---

### 问题1：GUI 背景视觉升级 - 深空蓝 + 动态网格线
- **发现者**：小夏
- **问题描述**：原有六边形蜂窝网格背景显得杂乱，有锯齿感，需要替换为更简洁优雅的深空蓝背景 + 动态网格线
- **解决方法**：
  1. **深空蓝渐变背景**：
     - 使用三层渐变：深黑蓝 (#020617) → 深空蓝 (#0a0f1c) → 午夜蓝 (#0f172a)
     - 添加径向渐变中心光晕，营造深邃空间感
  2. **动态网格线效果**：
     - 网格间距 40px，线条透明度根据距离中心位置动态变化
     - 垂直/水平线使用渐变透明度（两端透明，中间可见）
     - 网格交叉点添加发光圆点，中心区域更亮
  3. **科技感细节**：
     - 添加微妙的扫描线效果（极淡的横向光带）
     - 更新主题配色 `theme.py`，统一深空蓝色调
  4. **修复技术问题**：
     - QPen 不支持直接使用 QLinearGradient，需使用 QBrush 包装
- **解决效果**：
  - 背景从杂乱六边形变为优雅深空蓝渐变
  - 动态网格线营造数字化、科技感氛围
  - 整体视觉更加简洁、专业、有深度

---

## 2026年3月6日（补充）

### 问题1：Chrome DevTools MCP 服务器验证与配置
- **发现者**：小夏
- **问题描述**：需要验证 Chrome DevTools MCP 服务器是否正常工作，并配置到 MechForge 项目中
- **解决方法**：
  1. 创建测试脚本 `test_mcp_chrome.py` 验证 MCP 服务器连接
  2. 验证成功：服务器版本 0.19.0，3 个工具可用（navigate/evaluate/screenshot）
  3. 修复 `mechforge_core/mcp/client.py` Windows 兼容性（添加 `shell=True`）
  4. 创建 MCP 配置文件 `.qwen/mcp_config.json`
  5. 创建使用示例 `examples/mcp_chrome_example.py`
- **解决效果**：
  - Chrome DevTools MCP 服务器验证通过
  - 可在 MechForge 中调用浏览器自动化工具
  - 支持网页截图、JavaScript 执行、页面导航等功能

---

## 2026年3月8日

### 问题1：GUI 视觉细节优化
- **发现者**：小夏
- **问题描述**：需要进一步优化 GUI 的视觉细节，增强品牌识别度和启动界面的视觉冲击力
- **解决方法**：
  1. **标题栏文字优化**：确认使用白色粗体 "MechForge AI"，提升品牌辨识度
  2. **欢迎词发光边框**：使用 QGraphicsDropShadowEffect 实现青色霓虹外发光效果
     - 模糊半径 30px，营造柔和光晕
     - 颜色 rgba(0, 245, 255, 100)，半透明电光青
     - 偏移量 (0, 0)，中心对称发光
  3. **欢迎词卡片优化**：
     - 背景改为 rgba(16, 24, 45, 0.70)，更深的玻璃态
     - 边框颜色 rgba(0, 245, 255, 0.40)，更明显的青色边框
     - 圆角 16px，更大的圆角更现代
     - 内边距 20px 24px，更舒适的阅读空间
- **解决效果**：
  - 标题栏品牌文字清晰醒目
  - 欢迎词卡片呈现霓虹灯般的悬浮发光效果
  - 启动界面视觉冲击力显著提升
  - 整体风格更加统一协调

---

## 2026年3月7日

### 问题1：GUI 界面升级为 Dark Glassmorphism 赛博朋克风格
- **发现者**：小夏
- **问题描述**：需要为 mechforge-gui 升级视觉设计，采用 Dark Glassmorphism 风格，增强科技感和未来主义氛围
- **解决方法**：
  1. **配色升级**：深海军蓝渐变背景 (#0A0F1C → #121A2E)，电光青霓虹强调色 (#00F5FF)
  2. **六边形蜂窝网格**：使用 QPainter 实时绘制六边形网格纹理，象征机械结构的精密与互联
  3. **玻璃态效果**：半透明背景 + 模糊 + 发光边框，营造深邃的层次感
  4. **标题栏改造**：玻璃态渐变背景 + 霓虹按钮 + 发光悬停效果
  5. **输入栏升级**：玻璃态容器 + 无边框输入框 + 霓虹发送按钮
  6. **状态栏优化**：深色半透明背景 + 状态指示点 + 青色分隔线
  7. **垂直分层布局**：标题栏 → 聊天区 → 输入栏 → 状态栏，焦点集中在交互核心
- **解决效果**：
  - 界面呈现深邃的赛博朋克科技感
  - 六边形蜂窝网格增强机械工程主题
  - 玻璃态效果营造未来主义氛围
  - 整体视觉层次清晰，交互焦点突出

---

## 2026年3月6日

### 问题1：创建 PySide6 GUI 桌面应用
- **发现者**：小夏
- **问题描述**：需要为 `mechforge-ai` 创建桌面 GUI 版本，功能与终端版本一致，但界面更友好
- **解决方法**：
  1. 创建 `mechforge_gui_ai/` 模块，使用 PySide6 框架
  2. 设计终端风格深色主题（深蓝黑背景 + 青色/绿色强调）
  3. 实现主窗口：横幅区域、聊天区域、输入区域、状态栏
  4. 集成 LLMClient 和 RAGEngine，支持多 Provider（OpenAI/Anthropic/Ollama/GGUF）
  5. 实现命令支持：/help, /status, /rag, /clear, /model 等
  6. 添加工具栏按钮：新建、清空、模型、RAG、帮助、退出
  7. 创建打包脚本 `build_gui.py`，支持 PyInstaller 打包为单文件 exe
  8. 更新 `pyproject.toml` 添加 `mechforge-gui` 命令入口和 `[gui]` 依赖分组
- **解决效果**：
  - GUI 应用成功运行，界面风格与终端一致
  - 支持直接运行 `python mechforge_gui_ai/app.py` 或 `mechforge-gui` 命令
  - 可打包为独立 exe 文件分发

---

## 2026年3月5日

### 问题1：AI模式提示符颜色标签未渲染
- **发现者**：小夏
- **问题描述**：启动 `mechforge` AI 对话模式时，底部提示符显示为原始文本 `[spring_green3][MechForge] >[/spring_green3]`，颜色标签没有被正确渲染
- **解决方法**：
  1. 定位问题：`terminal.py` 中 `_input_with_history()` 方法使用 Python 内置 `input()` 函数，该函数不支持 Rich 颜色标签解析
  2. 修改方案：将 `input()` 替换为 `console.input()`，使用 Rich 的 Console 类来正确渲染颜色标签
- **解决效果**：提示符正确显示为绿色 `[MechForge] >`

---

### 问题2：启动动画与横幅之间缺少分隔
- **发现者**：小夏
- **问题描述**：`系统启动中... ✓` 提示与 ASCII 横幅之间没有分隔，视觉上不够美观
- **解决方法**：在 `gear_spin()` 方法末尾添加 `console.print(Rule(style="dim cyan"))` 水平分隔线
- **解决效果**：启动动画与横幅之间有清晰的分隔线，界面更美观

---

### 问题3：v0.4.0 先行版本打包发布
- **发现者**：小夏
- **问题描述**：项目基本框架已完成，需要打包发布先行版本到 PyPI
- **解决方法**：
  1. 修复 `pyproject.toml` 配置：将 `where = ["packages"]` 改为 `where = ["."]`，解决包路径问题
  2. 更新 license 配置为 SPDX 格式 `license = "MIT"`
  3. 添加 keywords 字段
  4. 运行 `python -m build` 构建 sdist 和 wheel
- **解决效果**：成功构建发布包
  - `mechforge_ai-0.4.0-py3-none-any.whl` (126 KB)
  - `mechforge_ai-0.4.0.tar.gz` (156 KB)

---

### 问题4：集成 RAGFlow 高级文档解析能力
- **发现者**：小夏
- **问题描述**：现有知识库功能仅支持基础的 Markdown/TXT/PDF 文档处理，缺乏 OCR、表格提取、版面分析等高级能力
- **解决方法**：
  1. 设计统一的知识库后端接口 `KnowledgeBackend`，支持多种后端实现
  2. 实现 `LocalBackend`：封装现有的 ChromaDB + BM25 本地实现
  3. 实现 `RAGFlowBackend`：通过 API 调用 RAGFlow 服务，获得高级文档解析能力
  4. 更新配置文件支持后端切换（`backend: local | ragflow`）
  5. 添加 `get_backend()` 和 `get_backend_from_config()` 工厂方法
- **解决效果**：
  - 知识库模块支持后端切换，便于后期扩展
  - RAGFlow 集成代码独立存放在 `mechforge_knowledge/backends/` 目录，便于删除
  - 配置文件新增 `knowledge.backend` 和 `knowledge.ragflow` 配置项

---

## 2026年3月4日

### 问题1：RAG引擎启动延迟与HuggingFace警告
- **发现者**：小夏
- **问题描述**：启动 `mechforge-ai` 时，RAG引擎随主程序一起启动，导致加载嵌入模型产生延迟，同时出现 HuggingFace 警告信息（HF_TOKEN、BertModel LOAD REPORT 等）
- **解决方法**：
  1. 将 RAG 引擎改为延迟加载（使用 `@property` 属性），仅在需要时初始化
  2. 在 `rag_engine.py` 添加环境变量抑制 HF 警告：
     - `TOKENIZERS_PARALLELISM=false`
     - `HF_HUB_DISABLE_TELEMETRY=1`
     - `TRANSFORMERS_VERBOSITY=error`
  3. 使用 `warnings.catch_warnings()` 抑制 sentence-transformers 加载警告
- **解决效果**：RAG 默认关闭时不加载嵌入模型，启动速度提升，不再显示 HuggingFace 警告信息

---

### 问题2：终端界面机器人图标删除
- **发现者**：小夏
- **问题描述**：各模式界面显示的机器人 ASCII 图标占用空间，希望删除
- **解决方法**：
  1. 删除 `mechforge_theme/components.py` 中的机器人 Panel
  2. 删除 `mechforge_knowledge/cli.py` 中的机器人 Panel
  3. 删除 `mechforge_work/work_cli.py` 中的机器人 Panel
  4. 将提示符从 `[MechBot]` 改为 `[MechForge]`
- **解决效果**：界面更简洁，统一使用 `[MechForge]` 作为提示符

---

### 问题3：terminal.py 文件损坏
- **发现者**：小夏
- **问题描述**：启动时报错 `SyntaxError: source code string cannot contain null bytes`，文件内容全部为空字节
- **解决方法**：使用 `git checkout HEAD -- mechforge_ai/terminal.py` 从 git 恢复文件
- **解决效果**：文件恢复正常，程序可正常启动
