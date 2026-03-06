# MechForge AI

真正懂机械、敢说真话、能真算

<p align="center">
  <a href="https://github.com/yd5768365-hue/mechforge/releases">
    <img src="https://img.shields.io/badge/version-0.4.0-blue.svg" alt="Version"/>
  </a>
  <a href="https://github.com/yd5768365-hue/mechforge/blob/main/LICENSE">
    <img src="https://img.shields.io/badge/license-MIT-green.svg" alt="License"/>
  </a>
  <a href="https://python.org">
    <img src="https://img.shields.io/badge/python-3.10+-blue.svg" alt="Python"/>
  </a>
  <a href="https://github.com/yd5768365-hue/mechforge/actions/workflows/ci.yml">
    <img src="https://github.com/yd5768365-hue/mechforge/actions/workflows/ci.yml/badge.svg" alt="CI"/>
  </a>
  <a href="https://github.com/yd5768365-hue/mechforge/pkgs/container/mechforge">
    <img src="https://img.shields.io/badge/ghcr.io-mechforge-blue.svg" alt="Docker GHCR"/>
  </a>
  <a href="https://github.com/yd5768365-hue/mechforge/stargazers">
    <img src="https://img.shields.io/github/stars/yd5768365-hue/mechforge?style=social" alt="Stars"/>
  </a>
</p>

---

## 📑 目录

- [✨ 核心特性](#-核心特性)
- [🚀 快速开始](#-快速开始)
  - [📦 Docker 部署](#-docker-部署)
- [📖 使用指南](#-使用指南)
- [🏗️ 技术架构](#-技术架构)
- [📦 依赖分组](#-依赖分组)
- [🛠️ 开发](#-开发)
- [📂 项目结构](#-项目结构)
- [📝 更新日志](#-更新日志)
- [📄 许可证](#-许可证)

---

## ✨ 核心特性

### 🤖 AI 对话模式
- **多模型支持**: OpenAI, Anthropic, Ollama, 本地 GGUF
- **流式响应**: 实时打字机效果
- **工具调用**: MCP 协议，内置工程计算工具
- **对话历史**: 持久化存储

### 📚 知识库检索
- **多后端支持**: 本地引擎 / RAGFlow API
- **RAG 引擎**: 向量检索 + BM25 + 重排序
- **多格式支持**: Markdown, PDF, TXT, Word, 图片
- **高级解析**: OCR 文字识别、表格提取、版面分析（RAGFlow）
- **原文呈现**: 杜绝 AI 幻觉
- **智能切分**: 自动文档分块

### 🔧 CAE 工作台
- **几何处理**: STEP, IGES, STL, OBJ, BREP 导入
- **网格划分**: Gmsh 4.15+ 集成，支持四面体/六面体网格
- **FEA 求解**: CalculiX 本地求解 + API 远程求解
- **可视化**: PyVista 3D 云图 + ASCII 后备显示
- **材料库**: 钢材、铝合金、铜、钛合金

### 🌐 Web 界面
- **FastAPI**: 高性能异步后端
- **WebSocket**: 实时双向通信
- **安全中间件**: 速率限制、IP 过滤、输入验证、安全头

### 🔌 MCP 协议
- **内置工具**: 悬臂梁计算、材料查询、弹簧设计
- **可扩展**: 自定义工具注册
- **外部连接**: 文件系统、数据库、GitHub
- **标准化**: Model Context Protocol

### 🦙 本地模型管理
- **统一管理**: Ollama + GGUF
- **HTTP 服务**: GGUF 提供 Ollama 兼容 API
- **自动启动**: 按需启动模型服务
- **交互选择**: 可视化模型选择器

---

## 🚀 快速开始

### 💻 系统要求

- **Python**: 3.10 或更高版本
- **操作系统**: Windows 10/11, macOS 10.15+, Ubuntu 20.04+
- **内存**: 最低 4GB，推荐 8GB+
- **磁盘空间**: 500MB（不含模型文件）

### 安装

```bash
# 从 PyPI 安装 (推荐)
pip install mechforge-ai

# 完整安装（所有功能）
pip install mechforge-ai[all]

# 从源码安装
git clone https://github.com/yd5768365-hue/mechforge.git
cd mechforge
pip install -e ".[all]"
```

### 配置本地模型

**方式 A: Ollama (推荐)**
```bash
# 安装 Ollama
curl -fsSL https://ollama.com/install.sh | sh

# 下载模型
ollama pull qwen2.5:1.5b
```

**方式 B: GGUF 模型**
```bash
# 下载 GGUF 文件
wget https://huggingface.co/Qwen/Qwen2.5-1.5B-Instruct-GGUF/resolve/main/qwen2.5-1.5b-instruct-q4_k_m.gguf \
  -O ./models/qwen2.5-1.5b.gguf

# 启动 GGUF 服务器
mechforge-model serve -m qwen2.5-1.5b.gguf
```

### 启动使用

```bash
# 查看可用模型
mechforge-model list

# 选择默认模型
mechforge-model select

# 启动 AI 对话
mechforge

# 启动知识库
mechforge-k

# 启动 CAE 工作台
mechforge-work

# 启动 CAE TUI 界面
mechforge-work --tui

# 启动 Web 界面
mechforge-web
```

### 📋 命令速查表

| 命令 | 说明 | 示例 |
|------|------|------|
| `mechforge` | 启动 AI 对话 | 直接运行进入交互模式 |
| `mechforge-k` | 启动知识库 | `mechforge-k search "关键词"` |
| `mechforge-work` | 启动 CAE 工作台 | `mechforge-work demo` |
| `mechforge-work --tui` | 启动 CAE TUI 界面 | 交互式终端界面 |
| `mechforge-web` | 启动 Web 界面 | 访问 http://localhost:8080 |
| `mechforge-model` | 模型管理 | `mechforge-model list` |

---

## 📦 Docker 部署

提供多种镜像变体，支持 `linux/amd64` 和 `linux/arm64` 平台。

### 快速启动

```bash
# 方式一：使用启动脚本
./docker-start.sh start           # Linux/macOS
docker-start.bat start            # Windows

# 方式二：Docker Compose (推荐)
git clone https://github.com/yd5768365-hue/mechforge.git
cd mechforge
cp .env.example .env
docker-compose --profile full up -d

# 方式三：直接拉取镜像运行
docker pull ghcr.io/yd5768365-hue/mechforge:latest
docker run -it --rm ghcr.io/yd5768365-hue/mechforge:latest
```

### 镜像变体

| 镜像 | 大小 | 描述 |
|------|------|------|
| `ghcr.io/yd5768365-hue/mechforge:latest` | ~800MB | 完整版（推荐） |
| `ghcr.io/yd5768365-hue/mechforge-ai:latest` | ~200MB | AI 对话模式 |
| `ghcr.io/yd5768365-hue/mechforge-rag:latest` | ~500MB | 知识库 RAG 模式 |
| `ghcr.io/yd5768365-hue/mechforge-work:latest` | ~400MB | CAE 工作台模式 |
| `ghcr.io/yd5768365-hue/mechforge-web:latest` | ~300MB | Web 服务模式 |

### Docker Compose 启动模式

```bash
docker-compose --profile ai up -d      # AI 对话
docker-compose --profile rag up -d     # 知识库
docker-compose --profile work up -d    # CAE 工作台
docker-compose --profile web up -d     # Web 服务
docker-compose --profile full up -d    # 完整版 (推荐)
```

### 环境变量

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `OLLAMA_URL` | `http://ollama:11434` | Ollama 服务地址 |
| `OLLAMA_MODEL` | `qwen2.5:1.5b` | 默认使用的模型 |
| `LOG_LEVEL` | `INFO` | 日志级别 |
| `WEB_PORT` | `8080` | Web 服务端口 |

📖 详细文档请参阅 [Docker 部署指南](docs/DOCKER.md)

---

## 📖 使用指南

### AI 对话示例

```
$ mechforge

[MechForge] > 计算一个长100mm的悬臂梁挠度，截面10x10mm，受力1000N

AI: 我来为您计算这个悬臂梁的挠度...

使用工具: calculate_cantilever_deflection
参数: {"length": 100, "force": 1000, "width": 10, "height": 10}

结果: 最大挠度为 0.0254 mm

计算公式: δ = FL³ / (3EI)
其中:
- F = 1000 N
- L = 100 mm
- E = 210000 MPa (钢材)
- I = 833.33 mm⁴
```

---

## 📚 知识库高级配置

### 后端选择

MechForge AI 支持两种知识库后端：

| 后端 | 特点 | 适用场景 |
|------|------|----------|
| `local` | 轻量级，无需外部服务 | Markdown/TXT 文档，快速部署 |
| `ragflow` | 高级文档解析能力 | PDF/图片/表格，OCR 需求 |

### 配置方式

编辑 `config.yaml`：

```yaml
knowledge:
  # 选择后端: local | ragflow
  backend: "local"

  # 本地后端配置
  path: "./knowledge"

  # RAGFlow 后端配置（当 backend: ragflow 时生效）
  ragflow:
    url: "http://localhost:9380"
    api_key: "your-api-key"
    kb_id: "your-kb-id"
```

---

### 🔧 RAGFlow 集成指南

RAGFlow 是一个开源的 RAG 引擎，提供高级文档解析能力：

- **OCR 文字识别**: 支持扫描件、图片 PDF
- **表格提取**: 自动识别表格结构
- **版面分析**: 智能识别标题、段落、图片
- **多格式支持**: PDF、Word、PPT、Excel、图片

#### Step 1: 部署 RAGFlow

```bash
# 克隆 RAGFlow 仓库
git clone https://github.com/infiniflow/ragflow.git
cd ragflow/docker

# 修改 .env（可选，使用稳定版本）
echo "RAGFLOW_IMAGE=infiniflow/ragflow:v0.15.0" > .env

# 启动服务（CPU 版本）
docker compose -f docker-compose.yml up -d

# 或使用 GPU 版本
# docker compose -f docker-compose-gpu.yml up -d
```

启动后访问 http://localhost:9380，默认账号 `ragflow` / `infiniflow`。

#### Step 2: 创建知识库

1. 登录 RAGFlow 界面
2. 点击 **Knowledge Base** → **Create Knowledge Base**
3. 输入知识库名称（如 `mechanical`）
4. 选择解析方法：
   - **General**: 通用文档
   - **Manual**: 手册类文档
   - **Law**: 法律法规
   - **Paper**: 学术论文
   - **Book**: 书籍
   - **Table**: 表格类文档
5. 上传文档并等待解析完成

#### Step 3: 获取 API 凭证

1. 点击右上角 **Settings** → **API Keys**
2. 创建新的 API Key
3. 记录 **API Key** 和 **Knowledge Base ID**

#### Step 4: 配置 MechForge AI

编辑 `config.yaml`：

```yaml
knowledge:
  backend: "ragflow"
  ragflow:
    url: "http://localhost:9380"
    api_key: "ragflow-xxxxxxxxxxxx"
    kb_id: "kb_xxxxxxxxxxxx"
```

#### Step 5: 使用知识库

```python
from mechforge_knowledge import get_backend_from_config

# 获取配置的后端
backend = get_backend_from_config()

# 检查健康状态
is_healthy = await backend.health_check()

# 检索知识库
results = await backend.search("轴承选型方法", top_k=5)
for result in results:
    print(f"来源: {result.source}")
    print(f"内容: {result.content}")
    print(f"相关度: {result.score}")
```

#### RAGFlow 常见问题

**Q: RAGFlow 启动失败**
```bash
# 检查端口占用
netstat -tlnp | grep 9380

# 查看日志
docker logs ragflow-server

# 重启服务
docker compose restart
```

**Q: 文档解析慢**
- 使用 GPU 版本可加速 OCR
- 减少并发解析任务数
- 选择合适的解析方法

**Q: 检索结果不准确**
- 调整 `top_k` 参数
- 尝试不同的解析方法
- 检查文档分块是否合理

---

### CAE 分析示例

```bash
$ mechforge-work

[MechBot] > /demo
✓ 悬臂梁示例已加载

[MechBot] > /mesh --size=2.0
✓ 网格生成完成: 12345 节点, 6789 单元

[MechBot] > /solve
✓ 求解完成
  最大位移: 0.025396 mm
  最大应力: 125.60 MPa

[MechBot] > /show vonmises
[显示应力云图...]
```

### 使用 CalculiX API 远程求解

```bash
# 设置 API 端点
[MechBot] > /api https://your-calculix-api.com

# 使用 API 求解
[MechBot] > /solve --api
```

### Web 界面

访问 http://localhost:8080 使用 Web 界面：

- **AI 对话**: 实时流式聊天，支持 Markdown
- **知识库**: 可视化搜索和浏览
- **CAE**: 3D 模型查看，结果可视化

---

## 🏗️ 技术架构

```
┌─────────────────────────────────────────────────────────────┐
│                      MechForge AI v0.4.0                    │
├──────────────┬──────────────┬──────────────┬────────────────┤
│  AI 对话     │  知识库      │  CAE 工作台  │  Web 界面      │
├──────────────┼──────────────┼──────────────┼────────────────┤
│ LLM Client   │ RAG Engine   │ Gmsh 4.15+   │ FastAPI        │
│ MCP Tools    │ BM25/Rerank  │ CalculiX     │ WebSocket      │
│ Streaming    │ ChromaDB     │ PyVista      │ Security       │
├──────────────┴──────────────┴──────────────┴────────────────┤
│              Core (Config / MCP / Local Model Manager)       │
├─────────────────────────────────────────────────────────────┤
│  🦙 Ollama  │  📦 GGUF HTTP  │  🔧 MCP Servers               │
└─────────────────────────────────────────────────────────────┘
```

---

## 📦 依赖分组

```bash
# 基础功能 (AI Chat)
pip install mechforge-ai

# CAE 功能 (+Gmsh +CalculiX +PyVista)
pip install mechforge-ai[work]

# RAG 功能 (+ChromaDB +Sentence-Transformers)
pip install mechforge-ai[rag]

# Web 界面 (+FastAPI +WebSocket)
pip install mechforge-ai[web]

# 完整功能 (所有依赖)
pip install mechforge-ai[all]
```

---

## 🔧 故障排除

### 常见问题

**Q: 启动时提示 "命令未找到"**
```bash
# 确保安装成功并添加到 PATH
pip install --upgrade mechforge-ai
# 或重新安装
pip install --force-reinstall mechforge-ai
```

**Q: CAE 功能无法使用**
```bash
# 检查 CAE 环境
python check_cae_env.py

# 安装 CAE 依赖
pip install mechforge-ai[work]
```

**Q: 模型加载失败**
```bash
# 检查 Ollama 是否运行
ollama list

# 或检查 GGUF 文件路径
mechforge-model list
```

**Q: Web 界面无法访问**
```bash
# 检查端口是否被占用
mechforge-web --port 8081

# 或使用不同的主机
mechforge-web --host 0.0.0.0
```

---

## 🛠️ 开发

```bash
# 安装开发依赖
pip install -e ".[dev]"

# 运行测试
pytest

# 代码检查
ruff check .
black --check .
mypy mechforge_*/

# 构建文档
python scripts/build_docs.py

# 构建包
python scripts/build_package.py
```

---

## 📂 项目结构

```
mechforge_ai/
├── mechforge_core/            # 核心模块
│   ├── config.py              # Pydantic 配置
│   ├── cache.py               # 多级缓存系统
│   ├── database.py            # SQLite 数据库
│   ├── logger.py               # 结构化日志
│   ├── security.py             # 安全工具
│   ├── mcp/                    # MCP 协议实现
│   ├── gguf_server.py          # GGUF HTTP 服务器
│   └── local_model_manager.py  # 本地模型管理
├── mechforge_ai/              # AI 对话
│   ├── llm_client.py          # LLM 客户端
│   ├── terminal.py            # 终端界面
│   ├── rag_engine.py          # RAG 引擎
│   └── model_cli.py           # 模型 CLI
├── mechforge_knowledge/       # 知识库
│   ├── cli.py                 # 知识库 CLI
│   ├── lookup.py              # 查询引擎
│   └── rag.py                 # RAG 实现
├── mechforge_work/            # CAE 工作台
│   ├── work_cli.py            # CAE CLI
│   ├── mesh_engine.py         # Gmsh 网格引擎
│   ├── solver_engine.py       # CalculiX 求解器
│   ├── viz_engine.py          # PyVista 可视化
│   └── cae_core.py            # CAE 核心
├── mechforge_web/             # Web 界面
│   ├── api.py                 # API 路由
│   ├── main.py                # FastAPI 应用
│   ├── middleware.py          # 安全中间件
│   └── security_config.py     # 安全配置
├── mechforge_theme/           # 主题组件
│   ├── colors.py              # 颜色定义
│   └── components.py          # UI 组件
├── docs/                      # 文档
├── tests/                     # 测试
├── examples/                  # 示例
└── scripts/                   # 脚本
```

---

## 🤝 贡献

欢迎贡献代码！请遵循以下步骤：

1. Fork 仓库
2. 创建特性分支 (`git checkout -b feature/amazing`)
3. 提交更改 (`git commit -m 'Add amazing feature'`)
4. 推送分支 (`git push origin feature/amazing`)
5. 创建 Pull Request

---

## 📄 许可证

本项目采用 [MIT License](LICENSE) 开源。

---

## 🙏 致谢

感谢以下开源项目：
- [Gmsh](https://gmsh.info/) - 网格生成
- [CalculiX](http://www.calculix.de/) - FEA 求解器
- [Ollama](https://ollama.com/) - 本地 LLM
- [LlamaCPP](https://github.com/ggerganov/llama.cpp) - GGUF 推理
- [FastAPI](https://fastapi.tiangolo.com/) - Web 框架
- [PyVista](https://pyvista.org/) - 3D 可视化
- [Rich](https://github.com/Textualize/rich) - 终端 UI

---

## 📞 联系我们

- **GitHub**: https://github.com/yd5768365-hue/mechforge (主仓库)
- **GitCode**: https://gitcode.com/2501_94457157/mechforge (镜像仓库)
- **Issues**: [报告问题](https://github.com/yd5768365-hue/mechforge/issues)
- **Discussions**: [讨论区](https://github.com/yd5768365-hue/mechforge/discussions)

---

## 📝 更新日志

### v0.4.0 (2026-03-05)

#### ✨ 新特性
- **Docker 支持**
  - 多阶段构建 Dockerfile，支持 5 种镜像变体
  - Docker Compose 配置，一键部署完整服务
  - 自动镜像构建推送到 Docker Hub 和 GHCR
  - 快速启动脚本 (Linux/macOS/Windows)
- **CAE 工作台完整实现**
  - Gmsh 4.15+ 集成，支持 STEP/IGES/STL/OBJ/BREP 格式
  - CalculiX 本地求解 + API 远程求解
  - PyVista 3D 可视化 + ASCII 后备显示
  - 内置材料库（钢材、铝合金、铜、钛合金）
- **知识库后端架构**
  - 统一的 `KnowledgeBackend` 抽象接口
  - `LocalBackend`: 本地 ChromaDB + BM25 实现
  - `RAGFlowBackend`: RAGFlow API 集成，支持 OCR、表格提取
  - 配置文件支持后端切换
- **Textual TUI 界面**
  - 交互式文件选择
  - 进度显示
  - 结果展示
- **三种主模式**
  - `mechforge` - AI 对话模式
  - `mechforge-k` - 知识库查询模式
  - `mechforge-work` - CAE 工作台模式
- **核心模块增强**
  - 多级缓存系统 (Memory + Disk)
  - SQLite 数据库支持
  - 结构化日志系统
  - 安全中间件栈

#### 🔧 改进
- 优化包结构和导入
- 统一本地模型管理 (Ollama + GGUF)
- 改进 CAE 工作台错误处理
- 增强 MCP 工具支持
- GitHub Actions 自动同步到 GitCode
- 修复 AI 模式提示符颜色渲染问题
- 优化启动界面分隔线

#### 🐛 修复
- 修复 `rich.box` 导入错误
- 修复 Pylance 导入解析问题
- 修复打包配置路径问题
- 修复 Pylance 导入解析问题

### v0.3.0 (2025-12-15)

- 知识库查询模式
- RAG 支持
- 多 AI 提供商支持
- 配置管理

### v0.2.0 (2025-11-01)

- AI 聊天模式
- 本地 Ollama 模型支持
- 基础命令处理

### v0.1.0 (2025-10-01)

- 初始项目结构
- 基础 CLI 框架
- 配置系统

---

## 🚀 后续开发目标

### v0.5.0 (计划中)

- **知识库增强**
  - 持续积累机械工程专业知识
  - 集成更多专业文档和标准规范
  - 优化检索精度和响应速度
- **CAE 功能扩展**
  - 更多求解器支持
  - 参数化建模
  - 结果后处理增强
- **用户体验优化**
  - Web 界面重构
  - 移动端适配
  - 多语言支持

### v0.6.0 (敬请期待)

> 🎯 **知识驱动，智能进化**

v0.6.0 将是一个重要里程碑，核心目标是构建一个**持续学习、不断进化**的机械工程知识库系统。

**核心特性**：
- 📚 **知识库持续扩充**: 每日更新机械设计、制造工艺、材料科学等领域知识
- 🧠 **智能问答升级**: 基于知识库的精准问答，拒绝 AI 幻觉
- 🔧 **专业工具集成**: 更多工程计算工具，覆盖设计全流程
- 📊 **案例库建设**: 真实工程案例，助力设计决策

**知识库建设计划**：
- 机械设计手册（轴承、齿轮、紧固件等）
- 材料性能数据库
- 公差配合查询
- 标准件选型指南
- 常见问题解决方案

---

<p align="center">
  Made with ❤️ for Mechanical Engineers
</p>

<p align="center">
  <b>v0.6.0 敬请期待</b> 🚀
</p>