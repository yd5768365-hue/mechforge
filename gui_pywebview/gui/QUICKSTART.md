# MechForge AI GUI 快速启动指南

## 🚀 快速开始

### 1. 安装依赖

```bash
# 进入项目目录
cd D:\mechforge_ai

# 安装 MechForge AI
pip install -e .

# 安装 GUI 依赖
pip install fastapi uvicorn pywebview
```

### 2. 启动应用

#### Windows (推荐)

```bash
cd gui
start.bat
```

#### Linux/Mac

```bash
cd gui
chmod +x start.sh
./start.sh
```

#### 手动启动

```bash
# 终端 1: 启动后端服务器
cd gui
python server.py

# 终端 2: 启动桌面应用
cd gui
python desktop_app.py
```

## 📋 系统要求

- **Python**: 3.10+
- **内存**: 4GB+ (推荐 8GB+)
- **磁盘**: 2GB 可用空间
- **Ollama**: 已安装并运行 (可选，用于本地模型)

## 🔧 配置

### 环境变量

在项目根目录创建 `.env` 文件：

```bash
# Ollama 配置
OLLAMA_URL=http://localhost:11434
OLLAMA_MODEL=qwen2.5:3b

# 或使用 OpenAI
OPENAI_API_KEY=your-api-key
OPENAI_BASE_URL=https://api.openai.com/v1

# RAG 配置
MECHFORGE_RAG=true
MECHFORGE_KNOWLEDGE_PATH=./knowledge
```

### 知识库

```bash
# 创建知识库目录
mkdir knowledge

# 添加文档（支持 .txt, .md）
echo "这是测试文档" > knowledge/test.txt
```

## 🎯 功能说明

### AI 聊天

- **流式响应**: 实时显示 AI 回复
- **对话历史**: 自动保存和加载
- **RAG 集成**: 智能知识库检索

### 知识库检索

- **多路召回**: 向量 + BM25 检索
- **结果重排序**: 提高检索质量
- **文档支持**: .txt, .md, .pdf

### CAE 工作台

- **界面**: 已实现
- **后端**: 集成进行中

## 🐛 故障排查

### 1. 后端无法启动

```bash
# 检查端口占用
netstat -ano | findstr :5000

# 更换端口
python server.py --port 5001
```

### 2. AI 无响应

- 检查 Ollama 是否运行: `ollama list`
- 检查环境变量配置
- 查看后端日志

### 3. 导入错误

```bash
# 重新安装依赖
pip install -e ".[dev]"
```

## 📚 API 文档

访问 `http://localhost:5000/docs` 查看完整的 API 文档。

## 🎨 界面说明

- **左侧边栏**: 切换功能模块
- **聊天面板**: 输入问题并查看回复
- **状态栏**: 显示当前配置和状态
- **齿轮图标**: 机械鲸鱼吉祥物切换

## 🔗 相关链接

- [项目主页](https://github.com/yd5768365-hue/mechforge)
- [完整文档](./README.md)
- [MechForge Core](../README.md)

## 💡 提示

- 首次启动会自动创建配置文件
- 对话历史保存在 `~/.mechforge/conversation.json`
- 后端日志输出到控制台

## 📝 更新日志

### v0.5.0 (2026-03-08)

- ✅ GUI 后端服务器实现
- ✅ AI 聊天流式响应
- ✅ RAG 检索集成
- ✅ 配置管理 API
- ✅ 完整的启动脚本

---

**享受 MechForge AI GUI!** 🎉
