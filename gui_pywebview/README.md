# MechForge AI PyWebView 桌面应用

轻量级跨平台桌面应用，使用 PyWebView 替代 PySide6，提供现代化的 AI 对话界面。

## ✨ 特性

- **🎨 现代化 UI** - 暗色科幻主题，全息投影效果
- **🤖 多模型支持** - Ollama / GGUF 本地模型切换
- **📚 知识库检索** - RAG 检索增强生成
- **🔧 CAE 工作台** - 网格生成、求解、可视化（占位）
- **📖 经验库** - 机械工程故障案例库
- **🚀 轻量高效** - 无 Qt 依赖，安装包更小

## 📦 快速开始

### 安装依赖

```bash
pip install -r requirements.txt
```

### 运行应用

**Windows:**
```bash
start.bat
```

**Linux/macOS:**
```bash
bash start.sh
```

**或直接运行:**
```bash
python desktop_app.py
```

**调试模式:**
```bash
python desktop_app.py --debug
```

## 📁 项目结构

```
gui_pywebview/
├── desktop_app.py          # 主入口文件
├── server.py               # FastAPI 后端服务器入口
├── api/                    # 模块化 API 路由
│   ├── __init__.py         # 模块导出
│   ├── state.py            # 全局状态管理
│   ├── deps.py             # 依赖注入（懒加载）
│   ├── errors.py           # 统一错误处理
│   ├── health.py           # 健康检查 API
│   ├── chat.py             # 聊天 API
│   ├── rag.py              # RAG API
│   ├── config.py           # 配置 API
│   └── gguf.py             # GGUF 模型 API
├── index.html              # 前端页面
├── styles-modular.css      # 模块化样式入口
├── css/                    # CSS 模块
│   ├── variables.css       # CSS 变量、基础重置
│   ├── layout.css          # 布局组件
│   ├── chat.css            # 聊天面板
│   ├── panels.css          # 知识库、CAE 面板
│   ├── effects.css         # 动画效果
│   └── components.css      # UI 组件
├── core/                   # JavaScript 核心模块
│   ├── event-bus.js        # 事件总线
│   ├── api-client.js       # API 客户端
│   ├── utils.js            # 工具函数
│   ├── error-handler.js    # 错误处理
│   └── markdown.js         # Markdown 渲染
├── services/               # JavaScript 服务模块
│   ├── ai-service.js       # AI 服务
│   └── config-service.js   # 配置服务
├── app/                    # JavaScript 应用模块
│   ├── main.js             # 主入口
│   ├── ui/                 # UI 模块
│   │   ├── particles.js    # 粒子效果
│   │   ├── window-control.js
│   │   └── mascot.js       # 吉祥物
│   ├── chat/               # 聊天模块
│   │   ├── chat-ui.js
│   │   ├── chat-handler.js
│   │   └── chat-features.js
│   ├── knowledge/          # 知识库模块
│   ├── cae/                # CAE 工作台
│   └── settings/           # 设置模块
├── tests/                  # 测试
│   ├── conftest.py         # 测试配置
│   ├── fixtures.py         # 测试夹具
│   └── test_api.py         # API 测试
├── dj-whale.png            # 应用图标
├── build.py                # 打包脚本
├── pyproject.toml          # 项目配置
├── requirements.txt        # Python 依赖
├── package.json            # Node.js 配置 (ESLint)
└── .eslintrc.json          # ESLint 配置
```

## 🔧 开发

### 代码风格

**JavaScript:**
```bash
# 安装 ESLint
npm install

# 检查代码
npm run lint

# 自动修复
npm run lint:fix
```

**Python:**
```bash
# 使用 black 格式化
black *.py api/

# 使用 ruff 检查
ruff check .

# 类型检查
mypy api/
```

### 运行测试

```bash
# 运行所有测试
pytest

# 详细输出
pytest -v

# 跳过慢测试
pytest -m "not slow"
```

### 打包为可执行文件

```bash
# 安装 PyInstaller
pip install pyinstaller

# 打包
python build.py

# 或分步执行
python build.py --clean
python build.py --build
```

打包后的可执行文件位于 `dist/` 目录。

## 🆚 与 PySide6 版本对比

| 特性 | PyWebView | PySide6 |
|------|-----------|---------|
| 安装包大小 | ~50MB | ~200MB |
| 依赖复杂度 | 低 | 高 |
| 启动速度 | 快 | 中等 |
| 内存占用 | 低 | 高 |
| GPU 兼容性 | 好 | 需要配置 |
| 跨平台 | 优秀 | 优秀 |
| 开发效率 | 高 | 中等 |

## 🔌 API 端点

后端服务器提供以下 API：

| 端点 | 方法 | 描述 |
|------|------|------|
| `/health` | GET | 健康检查 |
| `/api/status` | GET | 系统状态 |
| `/api/chat` | POST | 非流式聊天 |
| `/api/chat/stream` | POST | 流式聊天 (SSE) |
| `/api/chat/history` | GET | 获取对话历史 |
| `/api/chat/history` | DELETE | 清空对话历史 |
| `/api/rag/search` | POST | 知识库搜索 |
| `/api/rag/status` | GET | RAG 状态 |
| `/api/rag/toggle` | POST | 切换 RAG 开关 |
| `/api/config` | GET | 获取配置 |
| `/api/config/provider` | POST | 切换 AI provider |
| `/api/models` | GET | 获取模型列表 |
| `/api/gguf/load` | POST | 加载 GGUF 模型 |
| `/api/gguf/info` | GET | GGUF 模型信息 |

## 🛠️ 技术栈

- **前端**: HTML5 / CSS3 / JavaScript (ES6+)
- **后端**: FastAPI + Uvicorn
- **桌面框架**: PyWebView
- **渲染引擎**: 系统 WebView (Edge WebView2 / WebKit)

## 📝 更新日志

### v0.5.0
- 重构 JavaScript 为模块化架构
- 拆分 CSS 为多个模块文件
- 重构 Python API 为模块化结构
- 添加统一错误处理
- 添加 pyproject.toml 配置
- 添加 ESLint 代码检查
- 优化构建脚本
- 更新项目文档

## 📄 许可证

MIT License