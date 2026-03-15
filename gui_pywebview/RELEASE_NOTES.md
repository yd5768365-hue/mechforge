# MechForge AI v0.4.0 发行说明

**发布日期**: 2026年3月6日  
**版本号**: v0.4.0  
**代号**: "ForgeMaster"  

---

## 🎯 版本概述

MechForge AI v0.4.0 是一个里程碑版本，标志着我们从 AI 对话工具向**完整机械工程 AI 工作台**的转型。本版本引入了三大核心模式、完整的 CAE 工作流支持、以及现代化的 GUI 界面。

---

## ✨ 新功能亮点

### 🤖 1. AI 对话模式 (`mechforge-ai`)

**多模型 AI 对话系统**，支持云端和本地模型：

| 提供商 | 模型示例 | 特点 |
|--------|----------|------|
| **OpenAI** | GPT-4, GPT-3.5 | 云端最强性能 |
| **Anthropic** | Claude 3.5 Sonnet | 超长上下文 |
| **Ollama** | Qwen2.5, Llama3 | 本地隐私保护 |
| **本地 GGUF** | 自定义量化模型 | 离线运行 |

**特性**:
- 💬 流式响应，实时打字机效果
- 🛠️ MCP 工具调用（悬臂梁计算、材料查询、弹簧设计）
- 💾 对话历史持久化
- 🎨 终端风格 UI（Rich + PySide6 GUI）

---

### 📚 2. 知识库模式 (`mechforge-k`)

**RAG 检索增强生成**，让 AI 真正读懂你的文档：

- **双后端架构**:
  - 🏠 **本地引擎**: ChromaDB + Sentence-Transformers
  - ☁️ **RAGFlow API**: 企业级 RAG 服务

- **多格式支持**:
  - 📄 Markdown, PDF, TXT, Word
  - 🖼️ 图片 OCR 文字识别
  - 📊 表格提取、版面分析

- **混合检索**:
  - 🔍 向量语义检索
  - 🔤 BM25 关键词检索
  - 🎯 重排序优化

---

### 🔧 3. CAE 工作台模式 (`mechforge-work`)

**真正的工程计算能力**，不只是聊天：

#### 几何处理
- 📐 支持 STEP, IGES, STL, OBJ, BREP 格式
- 🎨 内置演示模型（支架、圆柱、轴承等）

#### 网格划分 (Gmsh 4.15+)
```bash
# 生成分支支架网格
mechforge-work
> /mesh
# 选择 test_models/test_bracket.step
# 自动优化网格质量
```

#### FEA 求解 (CalculiX)
- 🖥️ **本地求解**: 集成 CalculiX 求解器
- 🌐 **API 远程求解**: 支持远程高性能计算
- 📚 **材料库**: 钢材、铝合金、铜、钛合金

#### 可视化
- 🎮 **PyVista 3D**: 交互式应力云图
- 📊 **ASCII 后备**: 终端内显示结果

#### TUI 界面
```bash
mechforge-work --tui
```
- 文件选择对话框
- 进度指示器
- 结果展示面板

---

### 🖥️ 4. GUI 桌面应用 (`mechforge-gui`)

**PySide6 构建的现代化界面**：

- 🎨 终端风格主题（Monokai 配色）
- 💬 多标签对话界面
- ⚙️ 可视化配置管理
- 🚀 一键打包为单文件 EXE (277MB)

---

### 🌐 5. Web 服务 (`mechforge-web`)

**FastAPI + WebSocket 实时通信**：

```bash
mechforge-web --port 8080
# 访问 http://localhost:8080
```

- ⚡ 异步高性能
- 🔒 安全中间件（速率限制、IP过滤）
- 🔄 WebSocket 实时推送

---

## 📦 安装方式

### 方式 1: PyPI 安装（推荐）

```bash
# 基础版（AI 对话）
pip install mechforge-ai

# 完整版（所有功能）
pip install mechforge-ai[all]

# 特定功能
pip install mechforge-ai[rag]    # 知识库
pip install mechforge-ai[work]   # CAE 工作台
pip install mechforge-ai[web]    # Web 服务
```

### 方式 2: Docker 部署

```bash
# 完整版
docker-compose --profile full up -d

# 单独模式
docker-compose --profile ai up -d
docker-compose --profile rag up -d
docker-compose --profile work up -d
docker-compose --profile web up -d
```

**镜像地址**:
- `ghcr.io/yd5768365-hue/mechforge:latest` (完整版 ~800MB)
- `ghcr.io/yd5768365-hue/mechforge-ai:latest` (AI 对话 ~200MB)
- `ghcr.io/yd5768365-hue/mechforge-rag:latest` (RAG ~500MB)
- `ghcr.io/yd5768365-hue/mechforge-work:latest` (CAE ~400MB)
- `ghcr.io/yd5768365-hue/mechforge-web:latest` (Web ~300MB)

### 方式 3: Windows 可执行文件

下载 `MechForge.exe` (277MB)，双击运行：
- ✅ 无需 Python 环境
- ✅ 单文件便携
- ✅ 包含 AI 对话 + 知识库 + GUI

---

## 🛠️ 技术栈

| 领域 | 技术 |
|------|------|
| **AI/LLM** | OpenAI API, Anthropic API, Ollama, llama-cpp-python |
| **RAG** | ChromaDB, Sentence-Transformers, Rank-BM25 |
| **CAE** | Gmsh 4.15+, CalculiX, PyVista |
| **Web** | FastAPI, WebSocket, Jinja2 |
| **GUI** | PySide6, Rich, Textual |
| **配置** | Pydantic v2, YAML |
| **构建** | PyInstaller, Docker |

---

## 🔄 升级指南

### 从 v0.3.x 升级

```bash
# 1. 备份配置
cp ~/.mechforge/config.yaml ~/.mechforge/config.yaml.backup

# 2. 升级包
pip install --upgrade mechforge-ai[all]

# 3. 验证安装
mechforge --version

# 4. 测试 CAE 功能
mechforge-work --tui
```

### 破坏性变更

- 无破坏性变更，完全向后兼容

---

## 🐛 已知问题

| 问题 | 状态 | 解决方案 |
|------|------|----------|
| RAG 引擎首次启动较慢 | 🟡 已知 | 已改为延迟加载 |
| HuggingFace 警告信息 | 🟡 已知 | 已添加环境变量抑制 |
| CAE 功能需要 Gmsh/CalculiX | 🟡 文档 | 详见 [CAE 环境检查](docs/DOCKER.md) |

---

## 🗺️ 路线图

### v0.5.0 (计划中)
- [ ] 多物理场仿真支持（热、流体）
- [ ] 参数化设计优化
- [ ] 更多 CAD 格式支持（CATIA, SolidWorks）
- [ ] 云端 CAE 求解集群

### v1.0.0 (目标)
- [ ] 完整的机械设计工作流
- [ ] AI 辅助生成 CAD 模型
- [ ] 智能设计审查
- [ ] 企业级权限管理

---

## 🤝 贡献者

感谢所有为本版本做出贡献的开发者！

---

## 📄 许可证

MIT License - 详见 [LICENSE](LICENSE)

---

## 📞 支持

- 🐛 **Bug 报告**: [GitHub Issues](https://github.com/yd5768365-hue/mechforge/issues)
- 💬 **讨论**: [GitHub Discussions](https://github.com/yd5768365-hue/mechforge/discussions)
- 📧 **联系**: yd5768365@163.com

---

## 🎉 致谢

感谢以下开源项目：
- [Gmsh](https://gmsh.info/) - 网格生成
- [CalculiX](http://www.calculix.de/) - FEA 求解器
- [PyVista](https://pyvista.org/) - 3D 可视化
- [Ollama](https://ollama.com/) - 本地 LLM
- [RAGFlow](https://ragflow.io/) - RAG 引擎

---

**🚀 立即体验**: 
```bash
pip install mechforge-ai[all]
mechforge-ai
```

**🐳 Docker 一键启动**:
```bash
docker run -it --rm ghcr.io/yd5768365-hue/mechforge:latest
```

---

*Made with ❤️ by MechForge Team*
