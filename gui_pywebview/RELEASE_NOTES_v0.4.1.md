# MechForge AI v0.4.1 发行说明

**发布日期**: 2026年3月6日
**版本号**: v0.4.1

---

## 🎯 版本概述

v0.4.1 是 GUI 界面的重大升级版本，引入了科幻控制台风格主题、统一的知识库路径管理，以及完整的 RAG 功能支持。

---

## ✨ 新功能亮点

### 🎨 1. GUI 界面全面升级

**科幻控制台风格主题**:
- 🌌 深空蓝背景 (#070D1A → #0F172A)
- ✨ 动态网格线动画效果
- 🔷 Modern Dark Glassmorphism 设计语言
- 🎆 霓虹青色 (#22D3EE) 强调色

**全新字体系统**:
| 用途 | 字体 | 风格 |
|------|------|------|
| 标题 | Orbitron | 科幻硬朗 |
| 按钮 | Rajdhani | 短小精悍 |
| 终端文字 | Share Tech Mono | 打字机感 |
| 中文 | Noto Sans SC | 思源黑体 |
| 代码 | JetBrains Mono | 等宽代码 |

### 📚 2. 知识库路径统一

**统一路径管理** (`mechforge_core/config.py`):
- 所有模式使用相同的路径解析逻辑
- 支持环境变量覆盖
- 用户可选择自定义知识库文件夹

**路径优先级**:
1. 用户选择的文件夹（GUI）
2. 环境变量 `MECHFORGE_KNOWLEDGE_PATH`
3. 配置文件中的路径
4. 默认路径 `./knowledge`

### 🤖 3. RAG 功能完整支持

**GUI 中的 RAG 按钮**:
- ✅ 检查知识库模块依赖
- ✅ 用户选择知识库文件夹
- ✅ 空文件夹自动创建示例文档
- ✅ 路径保存到配置文件

**支持的模式**:
- AI 对话模式 (`mechforge-ai`)
- 知识库模式 (`mechforge-k`)
- GUI 桌面应用 (`mechforge-gui`)

### 🛠️ 4. MCP 服务器支持

**Chrome DevTools MCP**:
- 浏览器自动化控制
- 网页内容提取
- 与 AI 对话集成

### 💬 5. 界面优化

**欢迎消息**:
- 使用 QTextEdit 替代 QLabel
- 静态显示，不再自动消失
- 支持富文本格式

**系统消息**:
- 从聊天区域完全移除
- 保持界面整洁

---

## 📦 构建产物

| 文件 | 大小 | 说明 |
|------|------|------|
| `MechForge.exe` | ~71 MB | Windows 可执行文件（轻量版） |
| `mechforge_ai-0.4.1-py3-none-any.whl` | ~160 KB | Python Wheel 包 |
| `mechforge_ai-0.4.1.tar.gz` | ~158 KB | 源码压缩包 |

**轻量版说明**:
- ✅ 完整的 GUI 界面功能
- ✅ AI 对话（OpenAI/Anthropic API）
- ✅ 知识库 RAG 检索
- ❌ 本地模型支持（GGUF/Ollama）- 需完整版

---

## 🛠️ 安装方式

### 方式 1: PyPI 安装

```bash
# 升级到新版本
pip install --upgrade mechforge-ai

# 完整功能
pip install mechforge-ai[all]
```

### 方式 2: Windows 可执行文件

下载 `MechForge.exe`，双击运行：
- ✅ 无需 Python 环境
- ✅ 单文件便携
- ✅ 包含 GUI + AI 对话 + 知识库

---

## 🔄 升级指南

### 从 v0.4.0 升级

```bash
# 1. 升级包
pip install --upgrade mechforge-ai

# 2. 验证安装
mechforge --version

# 3. 启动 GUI
mechforge-gui
```

---

## 🐛 修复问题

| 问题 | 状态 |
|------|------|
| RAG 引擎启动延迟 | ✅ 已修复（延迟加载） |
| HuggingFace 警告 | ✅ 已修复（环境变量抑制） |
| 知识库路径不一致 | ✅ 已修复（统一路径管理） |
| GUI 字体显示问题 | ✅ 已修复（QTextEdit） |

---

## 🗺️ 路线图

### v0.5.0 (计划中)
- [ ] 多物理场仿真支持
- [ ] 参数化设计优化
- [ ] 更多 CAD 格式支持

---

## 📄 许可证

MIT License - 详见 [LICENSE](LICENSE)

---

**🚀 立即体验**:
```bash
pip install --upgrade mechforge-ai
mechforge-gui
```

---

*Made with ❤️ by MechForge Team*
