# 🚀 MechForge AI GUI - 快速开始

## 📦 安装

### 1. 安装依赖

```bash
# 进入项目目录
cd D:\mechforge_ai

# 安装 MechForge AI
pip install -e .

# 安装 GUI 依赖
pip install fastapi uvicorn pywebview
```

### 2. 配置环境变量（可选）

在项目根目录创建 `.env` 文件：

```bash
# Ollama 配置
OLLAMA_URL=http://localhost:11434
OLLAMA_MODEL=qwen2.5:3b

# 或使用 OpenAI
OPENAI_API_KEY=your-api-key

# RAG 配置
MECHFORGE_RAG=true
MECHFORGE_KNOWLEDGE_PATH=./knowledge
```

### 3. 准备知识库（可选）

```bash
# 创建知识库目录
mkdir knowledge

# 添加文档
echo "这是测试文档" > knowledge/test.txt
```

## 🎯 启动应用

### Windows（推荐）

```bash
cd gui
start.bat
```

### Linux/Mac

```bash
cd gui
chmod +x start.sh
./start.sh
```

### 手动启动

```bash
# 终端 1: 启动后端服务器
cd gui
python server.py

# 终端 2: 启动桌面应用
cd gui
python desktop_app.py
```

## 💬 使用 AI 聊天

1. **启动应用**后，等待启动动画完成
2. **在输入框**输入你的问题
3. **点击发送**或按 Enter 键
4. **查看流式响应** - AI 会逐字符回复
5. **对话历史**自动保存

### 示例对话

```
用户: 你好，介绍一下你自己
AI: 你好！我是 MechForge AI，一个面向机械工程师的 AI 垂直助手...

用户: 什么是有限元分析？
AI: 有限元分析（FEA）是一种数值计算方法...
```

## 🔍 使用 RAG 检索

1. **切换到 Knowledge 标签**
2. **输入搜索关键词**
3. **点击搜索**或按 Enter 键
4. **查看检索结果**

### 示例搜索

```
查询: 螺栓连接设计规范
结果: 
  1. 《螺栓连接设计手册》- 相关度 0.95
  2. 《机械设计标准》- 相关度 0.87
  3. 《GB/T 连接件规范》- 相关度 0.82
```

## ⚙️ 配置管理

### 查看当前配置

访问 `http://localhost:5000/docs`（Swagger UI）

### 修改配置

编辑 `gui/server_config.yaml`：

```yaml
[server]
host = "127.0.0.1"
port = 5000

[features]
enable_rag = true
enable_streaming = true
```

## 🐛 故障排查

### 1. 后端无法启动

```bash
# 检查端口占用
netstat -ano | findstr :5000

# 更换端口
python server.py --port 5001
```

### 2. AI 无响应

- 检查 Ollama 是否运行：`ollama list`
- 检查环境变量配置
- 查看后端日志（控制台输出）

### 3. 导入错误

```bash
# 重新安装依赖
pip install -e ".[dev]"
```

### 4. RAG 检索失败

- 确认知识库目录存在
- 检查文档格式（支持 .txt, .md, .pdf）
- 查看 RAG 状态：`GET http://localhost:5000/api/rag/status`

## 📚 API 文档

完整的 API 文档请访问：`http://localhost:5000/docs`

### 常用端点

| 端点 | 方法 | 说明 |
|------|------|------|
| `/health` | GET | 健康检查 |
| `/status` | GET | 系统状态 |
| `/api/chat` | POST | 非流式聊天 |
| `/api/chat/stream` | POST | 流式聊天 |
| `/api/rag/search` | POST | 搜索知识库 |
| `/api/models` | GET | 可用模型列表 |

## 🎨 界面说明

- **左侧边栏**: 切换功能模块（AI / RAG / CAE）
- **聊天面板**: 输入问题并查看回复
- **状态栏**: 显示当前配置和状态
- **齿轮图标**: 机械鲸鱼吉祥物切换

## 📖 更多文档

- [完整文档](./README.md) - 详细功能说明
- [实现总结](./IMPLEMENTATION.md) - 技术实现细节
- [开发日志](../开发日志/2026-03-08_GUI_AI_实现总结.md) - 开发记录

## 💡 提示

- ✅ 首次启动会自动创建配置文件
- ✅ 对话历史保存在 `~/.mechforge/conversation.json`
- ✅ 后端日志输出到控制台
- ✅ 支持流式响应，体验更流畅
- ✅ RAG 检索与 CLI 版本保持一致

## 🎉 享受 MechForge AI GUI！

---

**有任何问题？** 查看 [故障排查](#故障排查) 或创建 Issue。
