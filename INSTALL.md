# MechForge AI - 安装指南

## 📦 安装包说明

本项目提供两种安装方式：

### 1. 单文件版 (MechForge-AI.exe)
- **适用场景**: 快速体验、临时使用
- **特点**: 单个可执行文件，无需安装
- **大小**: 约 30-50 MB

### 2. 便携版 (MechForge-AI-Portable/)
- **适用场景**: 日常使用、需要自定义配置
- **特点**: 包含配置文件、知识库目录
- **大小**: 约 30-50 MB

---

## 🚀 快速开始

### 方式一：单文件版（最简单）

1. 下载 `MechForge-AI.exe`
2. 双击运行
3. 首次运行会自动创建配置
4. 开始使用！

### 方式二：便携版（推荐）

1. 下载 `MechForge-AI-v0.4.0-Windows.zip`
2. 解压到任意目录（如 `D:\MechForge-AI`）
3. 运行 `启动 MechForge AI.bat` 或直接运行 `MechForge-AI.exe`
4. 开始使用！

---

## 📋 系统要求

| 项目 | 最低要求 | 推荐配置 |
|------|---------|---------|
| 操作系统 | Windows 10/11 64位 | Windows 11 64位 |
| 内存 | 4 GB | 8 GB+ |
| 磁盘空间 | 200 MB | 500 MB+ |
| 网络 | 可选（用于下载模型） | 宽带连接 |

---

## ⚙️ 首次使用配置

### 默认配置（开箱即用）

程序默认使用 **Ollama** 作为 AI 提供商：
- 模型: `qwen2.5:1.5b`（通义千问 1.5B 参数）
- 运行方式: 本地运行，无需联网
- 自动启动: 程序会尝试自动启动 Ollama 服务

### 安装 Ollama（如未安装）

如果系统未安装 Ollama，程序会提示下载：

1. 访问 https://ollama.com/download
2. 下载并安装 Ollama
3. 重启 MechForge AI

或者使用命令行安装：
```powershell
# Windows
winget install Ollama.Ollama
```

### 下载默认模型

首次使用需要下载模型（约 1GB）：

```bash
# 在命令行中执行
ollama pull qwen2.5:1.5b
```

或者在 MechForge AI 中直接开始对话，程序会自动下载。

---

## 🔧 自定义配置

### 编辑配置文件

便携版：编辑 `config/config.yaml`
安装版：编辑 `%LOCALAPPDATA%\mechforge\config.yaml`

### 切换 AI 提供商

#### 使用 OpenAI
```yaml
provider:
  default: "openai"
  openai:
    api_key: "your-api-key-here"
    model: "gpt-4o-mini"
```

#### 使用 Anthropic
```yaml
provider:
  default: "anthropic"
  anthropic:
    api_key: "your-api-key-here"
    model: "claude-3-haiku-20240307"
```

#### 使用其他 Ollama 模型
```yaml
provider:
  default: "ollama"
  ollama:
    url: "http://localhost:11434"
    model: "llama3.2:3b"  # 或其他模型
```

### 切换主题
```yaml
ui:
  theme: "light"  # 或 "dark"
```

---

## 📚 知识库使用

### 添加知识库文件

1. 将 Markdown (.md) 或文本 (.txt) 文件放入 `knowledge/` 目录
2. 重启程序或等待自动加载
3. 在对话中使用 `/rag` 命令启用知识库检索

### 示例知识库文件

创建 `knowledge/机械设计手册.md`:
```markdown
# 机械设计手册

## 材料属性

### Q235 钢
- 屈服强度: 235 MPa
- 抗拉强度: 375-500 MPa
- 弹性模量: 206 GPa

### 45 钢
- 屈服强度: 355 MPa
- 抗拉强度: 600 MPa
- 弹性模量: 206 GPa
```

---

## 🛠️ 故障排除

### 问题：程序无法启动

**解决方案:**
1. 检查系统是否满足最低要求
2. 安装 [Visual C++ Redistributable](https://aka.ms/vs/17/release/vc_redist.x64.exe)
3. 以管理员身份运行

### 问题：Ollama 连接失败

**解决方案:**
1. 检查 Ollama 是否已安装：
   ```bash
   ollama --version
   ```
2. 手动启动 Ollama 服务：
   ```bash
   ollama serve
   ```
3. 检查端口是否被占用（默认 11434）

### 问题：模型下载慢

**解决方案:**
1. 配置镜像源（中国用户）：
   ```bash
   set OLLAMA_HOST=0.0.0.0
   set OLLAMA_MODELS=D:\ollama\models
   ```
2. 使用代理工具

### 问题：界面显示异常

**解决方案:**
1. 更新显卡驱动
2. 尝试切换主题（编辑配置文件）
3. 删除配置目录重新生成：
   ```bash
   rmdir /s %LOCALAPPDATA%\mechforge
   ```

---

## 🔄 更新程序

### 便携版更新
1. 备份 `config/` 和 `knowledge/` 目录
2. 下载新版本并解压
3. 复制备份的配置和知识库到新目录

### 配置迁移
配置文件位于：
- 便携版：`config/config.yaml`
- 安装版：`%LOCALAPPDATA%\mechforge\config.yaml`

---

## 📞 获取帮助

- **GitHub Issues**: https://github.com/yd5768365-hue/mechforge/issues
- **文档**: https://github.com/yd5768365-hue/mechforge#readme
- **邮件**: 通过 GitHub 联系

---

## 📄 许可证

MIT License - 详见 LICENSE 文件

---

**版本**: 0.4.0  
**更新日期**: 2024年  
**作者**: MechForge Team
