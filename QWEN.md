# MechForge AI 项目上下文

## 项目概述

**MechForge AI** 是一个面向机械工程师的 AI 垂直助手，提供 AI 对话、知识库检索 (RAG) 和 CAE 工作台三大核心功能。

- **版本**: 0.4.0
- **Python**: 3.10+
- **许可证**: MIT
- **仓库**: https://github.com/yd5768365-hue/mechforge

### 核心功能

| 模式 | 命令 | 功能 |
|------|------|------|
| AI 对话 | `mechforge` | 多模型 AI 对话，支持 OpenAI/Anthropic/Ollama/GGUF |
| 知识库 | `mechforge-k` | RAG 检索，向量 + BM25 + 重排序 |
| CAE 工作台 | `mechforge-work` | Gmsh 网格 + CalculiX 求解 + PyVista 可视化 |
| Web 服务 | `mechforge-web` | FastAPI + WebSocket Web 界面 |
| 模型管理 | `mechforge-model` | Ollama + GGUF 本地模型管理 |

---

## 项目结构

```
mechforge_ai/
├── mechforge_core/          # 核心模块 (配置、缓存、数据库、日志、安全、MCP)
│   ├── config.py            # Pydantic v2 配置管理
│   ├── cache.py             # 多级缓存系统
│   ├── database.py          # SQLite 数据库
│   ├── logger.py            # 结构化日志
│   ├── security.py          # 安全工具
│   ├── mcp/                 # MCP 协议实现
│   ├── gguf_server.py       # GGUF HTTP 服务器
│   └── local_model_manager.py
├── mechforge_ai/            # AI 对话模块
│   ├── terminal.py          # 终端界面入口
│   ├── llm_client.py        # LLM 客户端
│   ├── rag_engine.py        # RAG 引擎
│   ├── command_handler.py   # 命令处理
│   └── model_cli.py         # 模型 CLI
├── mechforge_knowledge/     # 知识库模块
│   ├── cli.py               # 知识库 CLI
│   ├── lookup.py            # 查询引擎
│   └── rag.py               # RAG 实现
├── mechforge_work/          # CAE 工作台模块
│   ├── work_cli.py          # CAE CLI 入口
│   ├── cae_core.py          # CAE 核心引擎
│   ├── mesh_engine.py       # Gmsh 网格引擎
│   ├── solver_engine.py     # CalculiX 求解器
│   └── viz_engine.py        # PyVista 可视化
├── mechforge_web/           # Web 服务模块
│   ├── main.py              # FastAPI 应用入口
│   ├── api.py               # API 路由
│   ├── middleware.py        # 安全中间件
│   └── security_config.py   # 安全配置
├── mechforge_theme/         # 主题组件
│   ├── colors.py            # 颜色定义
│   └── components.py        # UI 组件
├── mechforge_gui_ai/        # GUI 桌面应用 (PySide6)
│   ├── app.py               # 应用入口
│   ├── main_window.py       # 主窗口
│   ├── theme.py             # 终端风格主题
│   ├── dialogs.py           # 配置对话框
│   └── build_gui.py         # 打包脚本
├── tests/                   # 测试
│   ├── unit/                # 单元测试
│   ├── integration/         # 集成测试
│   └── e2e/                 # 端到端测试
├── docs/                    # 文档
├── examples/                # 示例
└── scripts/                 # 构建脚本
```

---

## 构建与运行

### 安装

```bash
# PyPI 安装
pip install mechforge-ai

# 完整安装
pip install mechforge-ai[all]

# 开发模式
pip install -e ".[dev,all]"
```

### 运行命令

```bash
mechforge              # AI 对话模式 (终端)
mechforge-gui          # AI 对话模式 (GUI桌面应用)
mechforge-k            # 知识库模式
mechforge-work         # CAE 工作台
mechforge-work --tui   # CAE TUI 界面
mechforge-web          # Web 服务 (http://localhost:8080)
mechforge-model list   # 查看可用模型
mechforge-model select # 选择默认模型
```

### 测试

```bash
pytest                  # 运行所有测试
pytest tests/unit       # 单元测试
pytest tests/integration # 集成测试
pytest -m "not slow"    # 跳过慢测试
```

### 代码质量

```bash
ruff check .            # Lint 检查
black --check .         # 格式检查
mypy mechforge_*/       # 类型检查
```

### 构建

```bash
python scripts/build_package.py   # 构建包
python scripts/build_docs.py      # 构建文档
```

---

## 开发规范

### 代码风格

- **格式化**: Black (line-length=100)
- **Lint**: Ruff (pycodestyle, Pyflakes, isort, pep8-naming 等)
- **类型**: MyPy (strict mode)
- **文档**: Google style docstrings

### 命名约定

- 模块: `mechforge_<name>` (如 `mechforge_core`, `mechforge_ai`)
- 类: PascalCase (如 `MechForgeConfig`, `CAEEngine`)
- 函数/变量: snake_case (如 `get_config`, `mesh_engine`)
- 常量: UPPER_SNAKE_CASE (如 `DEFAULT_TIMEOUT`)
- 私有方法: `_leading_underscore`

### 配置管理

配置使用 Pydantic v2，支持:
- YAML/JSON 配置文件 (`config.yaml`)
- 环境变量覆盖 (如 `OLLAMA_URL`, `MECHFORGE_RAG`)
- 配置热重载 (`ConfigWatcher`)

配置优先级: 环境变量 > `~/.mechforge/config.yaml` > `./config.yaml`

### 日志规范

```python
from mechforge_core import get_logger

logger = get_logger("module.name")
logger.info("操作完成")
logger.error("错误详情", extra={"context": value})
```

### 测试规范

- 使用 `pytest` + `pytest-asyncio`
- 共享夹具在 `tests/conftest.py`
- 测试文件命名: `test_<module>.py` 或 `*_test.py`
- 使用 `@pytest.mark.slow` 标记慢测试

---

## 依赖分组

| 分组 | 用途 | 安装命令 |
|------|------|----------|
| 基础 | 核心功能 | `pip install mechforge-ai` |
| dev | 开发工具 | `pip install mechforge-ai[dev]` |
| llm | GGUF 推理 | `pip install mechforge-ai[llm]` |
| rag | 知识库 RAG | `pip install mechforge-ai[rag]` |
| work | CAE 工作台 | `pip install mechforge-ai[work]` |
| web | Web 服务 | `pip install mechforge-ai[web]` |
| all | 完整功能 | `pip install mechforge-ai[all]` |

---

## 关键技术栈

### AI/LLM
- **OpenAI API** / **Anthropic API**: 云端模型
- **Ollama**: 本地模型服务
- **llama-cpp-python**: GGUF 本地推理
- **MCP (Model Context Protocol)**: 工具调用协议

### RAG
- **ChromaDB**: 向量数据库
- **Sentence-Transformers**: 文本嵌入
- **Rank-BM25**: 关键词检索

### CAE
- **Gmsh 4.15+**: 几何处理 + 网格生成
- **CalculiX**: FEA 求解器
- **PyVista**: 3D 可视化

### Web
- **FastAPI**: 异步 Web 框架
- **WebSocket**: 实时通信
- **Jinja2**: 模板引擎

### UI
- **Rich**: 终端 UI
- **Textual**: TUI 框架

---

## 环境变量

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `OLLAMA_URL` | `http://localhost:11434` | Ollama 服务地址 |
| `OLLAMA_MODEL` | `qwen2.5:1.5b` | 默认模型 |
| `OPENAI_API_KEY` | - | OpenAI API Key |
| `ANTHROPIC_API_KEY` | - | Anthropic API Key |
| `MECHFORGE_RAG` | `false` | 启用 RAG |
| `MECHFORGE_KNOWLEDGE_PATH` | `./knowledge` | 知识库路径 |
| `MECHFORGE_LOG_LEVEL` | `info` | 日志级别 |
| `MECHFORGE_THEME` | `dark` | UI 主题 |

---

## Docker 部署

```bash
# Docker Compose (推荐)
docker-compose --profile full up -d

# 单独模式
docker-compose --profile ai up -d     # AI 对话
docker-compose --profile rag up -d    # 知识库
docker-compose --profile work up -d   # CAE 工作台
docker-compose --profile web up -d    # Web 服务
```

镜像变体:
- `ghcr.io/yd5768365-hue/mechforge:latest` (完整版 ~800MB)
- `ghcr.io/yd5768365-hue/mechforge-ai:latest` (AI 对话 ~200MB)
- `ghcr.io/yd5768365-hue/mechforge-rag:latest` (RAG ~500MB)
- `ghcr.io/yd5768365-hue/mechforge-work:latest` (CAE ~400MB)
- `ghcr.io/yd5768365-hue/mechforge-web:latest` (Web ~300MB)

---

## 常见问题排查

### 命令未找到
```bash
pip install --upgrade mechforge-ai
# 或重新安装
pip install --force-reinstall mechforge-ai
```

### CAE 功能不可用
```bash
python check_cae_env.py  # 检查环境
pip install mechforge-ai[work]
```

### 模型加载失败
```bash
ollama list              # 检查 Ollama
mechforge-model list     # 检查 GGUF 模型
```

### Web 端口被占用
```bash
mechforge-web --port 8081
```

---

## 相关文档

- `README.md` - 项目介绍和快速开始
- `CHANGELOG.md` - 版本更新日志
- `docs/DOCKER.md` - Docker 部署指南
- `config.yaml` - 配置文件示例
- `.env.example` - 环境变量模板
- `开发日志/DEV_LOG.md` - 开发日志（Qwen 记录）
- `.qwen/mcp_config.json` - MCP 服务器配置


## Qwen Added Memories
- 每次完成任务后记录 MechForge AI 开发日志到 DEV_LOG.md。格式示例：
## 2026年3月4日

### 问题1：RAG引擎启动延迟与HuggingFace警告
- **发现者**：小夏
- **问题描述**：启动 `mechforge-ai` 时，RAG引擎随主程序一起启动，导致加载嵌入模型产生延迟，同时出现 HuggingFace 警告信息
- **解决方法**：
  1. 将 RAG 引擎改为延迟加载（使用 `@property` 属性）
  2. 添加环境变量抑制 HF 警告
- **解决效果**：启动速度提升，不再显示警告信息

