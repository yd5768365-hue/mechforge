# MechForge AI 开发日志

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