# MechForge AI PyWebView 桌面应用

轻量级跨平台桌面应用，使用 PyWebView 替代 PySide6，提供现代化的 AI 对话界面。

[![CI](https://github.com/yd5768365-hue/mechforge/actions/workflows/ci.yml/badge.svg)](https://github.com/yd5768365-hue/mechforge/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

## ✨ 特性

- **🎨 现代化 UI** - 暗色科幻主题，全息投影效果
- **🚀 高性能** - 模块化架构，懒加载，性能监控
- **🤖 多模型支持** - Ollama / GGUF 本地模型切换
- **📚 知识库检索** - RAG 检索增强生成
- **🔧 CAE 工作台** - 网格生成、求解、可视化（占位）
- **📖 经验库** - 机械工程故障案例库
- **🛠️ 开发者友好** - 完整的开发工具链，VS Code 配置

## 📦 快速开始

### 环境要求

- Python 3.10+
- Node.js 18+ (可选，用于代码检查)
- Windows 10+ / macOS 10.15+ / Ubuntu 20.04+

### 安装依赖

```bash
# 克隆仓库
git clone https://github.com/yd5768365-hue/mechforge.git
cd mechforge/gui_pywebview

# 安装 Python 依赖
pip install -r requirements.txt

# 安装开发依赖（可选）
pip install -r requirements-dev.txt

# 安装 Node.js 依赖（可选）
npm install
```

### 运行应用

**Windows:**
```bash
start.bat
# 或
python desktop_app.py
```

**Linux/macOS:**
```bash
bash start.sh
# 或
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
├── build.py                # 优化版打包脚本
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
│   ├── components.css      # UI 组件
│   └── utilities.css       # 工具类
├── core/                   # JavaScript 核心模块
│   ├── event-bus.js        # 事件总线
│   ├── api-client.js       # API 客户端
│   ├── utils.js            # 工具函数
│   ├── logger.js           # 日志工具
│   ├── storage.js          # 存储管理
│   ├── error-handler.js    # 错误处理
│   ├── markdown.js         # Markdown 渲染
│   ├── theme.js            # 主题管理
│   ├── event-manager.js    # 事件管理器
│   ├── module-loader.js    # 模块加载器
│   ├── performance-monitor.js  # 性能监控
│   ├── cache-manager.js    # 缓存管理器
│   ├── debounce-throttle.js    # 防抖节流
│   └── dom-utils.js        # DOM 工具
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
├── .vscode/                # VS Code 配置
│   ├── extensions.json     # 推荐扩展
│   ├── settings.json       # 设置
│   ├── launch.json         # 调试配置
│   └── tasks.json          # 任务配置
├── .github/                # GitHub 配置
│   └── workflows/          # CI/CD 工作流
│       ├── ci.yml          # 持续集成
│       └── release.yml     # 发布
├── dj-whale.png            # 应用图标
├── pyproject.toml          # 项目配置
├── requirements.txt        # Python 依赖
├── requirements-dev.txt    # Python 开发依赖
├── package.json            # Node.js 配置
├── .eslintrc.json          # ESLint 配置
├── .prettierrc             # Prettier 配置
└── README.md               # 项目文档
```

## 🔧 开发

### VS Code 开发环境

推荐使用 VS Code 进行开发，项目已配置好完整的开发环境：

1. 安装推荐的扩展（打开项目时会自动提示）
2. 使用 `Ctrl+Shift+P` → `Tasks: Run Task` 运行常用任务
3. 使用 `F5` 启动调试

### 代码风格

**JavaScript:**
```bash
# 检查代码
npm run lint

# 自动修复
npm run lint:fix

# 格式化
npm run format

# 检查格式
npm run format:check
```

**Python:**
```bash
# 使用 black 格式化
black .

# 使用 ruff 检查
ruff check .

# 类型检查
mypy api/ desktop_app.py server.py
```

### 运行测试

```bash
# 运行所有测试
pytest

# 详细输出
pytest -v

# 跳过慢测试
pytest -m "not slow"

# 生成覆盖率报告
pytest --cov=api --cov-report=html
```

### 构建应用

```bash
# 标准构建
python build.py

# 仅构建（不清理）
python build.py --build

# 清理构建目录
python build.py --clean

# 优化资源后构建（推荐用于发布）
python build.py --optimize

# 开发模式
python build.py --dev

# 运行测试
python build.py --test
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
| 前端技术栈 | HTML/CSS/JS | QML/Qt Widgets |

## 🔌 API 端点

后端服务器提供以下 API：

### 健康检查
| 端点 | 方法 | 描述 |
|------|------|------|
| `/health` | GET | 健康检查 |
| `/api/status` | GET | 系统状态 |

### 聊天
| 端点 | 方法 | 描述 |
|------|------|------|
| `/api/chat` | POST | 非流式聊天 |
| `/api/chat/stream` | POST | 流式聊天 (SSE) |
| `/api/chat/history` | GET | 获取对话历史 |
| `/api/chat/history` | DELETE | 清空对话历史 |

### 模式管理
| 端点 | 方法 | 描述 |
|------|------|------|
| `/api/mode` | GET | 获取当前模式 |
| `/api/mode` | POST | 设置模式 |
| `/api/mode/reset` | POST | 重置为默认模式 |

### RAG
| 端点 | 方法 | 描述 |
|------|------|------|
| `/api/rag/search` | POST | 知识库搜索 |
| `/api/rag/status` | GET | RAG 状态 |
| `/api/rag/toggle` | POST | 切换 RAG 开关 |

### 配置
| 端点 | 方法 | 描述 |
|------|------|------|
| `/api/config` | GET | 获取配置 |
| `/api/config/provider` | POST | 切换 AI provider |
| `/api/models` | GET | 获取模型列表 |

### GGUF
| 端点 | 方法 | 描述 |
|------|------|------|
| `/api/gguf/load` | POST | 加载 GGUF 模型 |
| `/api/gguf/info` | GET | GGUF 模型信息 |

## 🛠️ 技术栈

- **前端**: HTML5 / CSS3 / JavaScript (ES6+)
- **后端**: FastAPI + Uvicorn
- **桌面框架**: PyWebView
- **渲染引擎**: 系统 WebView (Edge WebView2 / WebKit)
- **构建工具**: PyInstaller
- **代码质量**: Black / Ruff / MyPy / ESLint / Prettier

## 📊 性能优化

### JavaScript 优化

- **模块化架构**: 使用 ModuleLoader 实现按需加载
- **懒加载**: 非关键模块延迟加载
- **事件委托**: 减少事件监听器数量
- **防抖节流**: 高频操作优化
- **缓存管理**: 多级缓存策略
- **性能监控**: 实时监控 FPS、内存、长任务

### CSS 优化

- **CSS 变量**: 统一设计系统
- **模块化导入**: 按需加载样式
- **工具类**: 快速构建界面
- **硬件加速**: GPU 加速动画

### Python 优化

- **依赖注入**: 懒加载减少启动时间
- **异步处理**: FastAPI 异步路由
- **状态管理**: 全局状态集中管理

## 📝 更新日志

### v0.5.0 (2024-03-10)
- ✅ 重构 JavaScript 为模块化架构
- ✅ 拆分 CSS 为多个模块文件
- ✅ 重构 Python API 为模块化结构
- ✅ 添加统一错误处理
- ✅ 添加 pyproject.toml 配置
- ✅ 添加 ESLint 代码检查
- ✅ 优化构建脚本，支持资源优化
- ✅ 添加性能监控模块
- ✅ 添加缓存管理器
- ✅ 添加防抖节流工具
- ✅ 添加 DOM 工具集
- ✅ 完善 VS Code 开发配置
- ✅ 优化 CI/CD 工作流
- ✅ 添加 CSS 工具类
- ✅ 更新项目文档

### v0.4.0
- 初始版本发布

## 🤝 贡献指南

欢迎提交 Issue 和 Pull Request！

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 创建 Pull Request

## 📄 许可证

MIT License - 详见 [LICENSE](../LICENSE) 文件

## 🙏 致谢

- [PyWebView](https://pywebview.flowrl.com/) - 轻量级桌面框架
- [FastAPI](https://fastapi.tiangolo.com/) - 现代 Web 框架
- [Ollama](https://ollama.ai/) - 本地大模型服务

---

**Made with ❤️ by MechForge Team**
