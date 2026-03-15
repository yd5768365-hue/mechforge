# MechForge AI GUI

现代化的桌面应用程序，提供 AI 聊天、知识库检索和 CAE 仿真功能。

## 功能特性

### 1. AI 助手 (Chat)
- ✅ 流式对话响应
- ✅ 对话历史记录
- ✅ RAG 知识库集成
- ✅ 多模型支持 (Ollama/OpenAI/Anthropic/GGUF)

### 2. 知识库检索 (RAG)
- ✅ 向量检索 + BM25 关键词检索
- ✅ 智能文档切分
- ✅ 结果重排序
- ✅ 多格式文档支持

### 3. CAE 工作台
- ⚠️ 界面已实现，后端集成进行中
- ✅ 模型加载
- ✅ 网格生成
- ✅ 求解计算
- ✅ 结果可视化

## 技术栈

### 前端
- **HTML5/CSS3** - 现代化界面
- **JavaScript (ES6+)** - 业务逻辑
- **PyWebView** - 桌面应用封装

### 后端
- **FastAPI** - Web 框架
- **MechForge Core** - 核心功能
- **LLM Client** - AI 模型客户端
- **RAG Engine** - 知识库引擎

### 核心功能
- **AI 对话** - 支持流式和非流式
- **RAG 检索** - 多路召回 + 重排序
- **配置管理** - 动态配置加载

## 安装

### 1. 安装依赖

```bash
# 进入项目根目录
cd D:\mechforge_ai

# 安装 MechForge AI
pip install -e .

# 安装 GUI 依赖
pip install pywebview fastapi uvicorn
```

### 2. 配置环境

确保已配置好以下环境变量：

```bash
# Ollama 服务地址
OLLAMA_URL=http://localhost:11434
OLLAMA_MODEL=qwen2.5:3b

# 或者使用 OpenAI
OPENAI_API_KEY=your-api-key
```

### 3. 准备知识库（可选）

```bash
# 创建知识库目录
mkdir knowledge

# 添加文档（支持 .txt, .md, .pdf）
# 文档将自动被索引
```

## 运行

### Windows

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

## API 端点

### 健康检查
- `GET /health` - 健康检查
- `GET /status` - 系统状态

### AI 聊天
- `POST /api/chat` - 非流式聊天
- `POST /api/chat/stream` - 流式聊天
- `GET /api/chat/history` - 获取历史
- `DELETE /api/chat/history` - 清空历史

### RAG 检索
- `POST /api/rag/search` - 搜索知识库
- `GET /api/rag/status` - RAG 状态
- `POST /api/rag/toggle` - 切换 RAG

### 配置管理
- `GET /api/config` - 获取配置
- `POST /api/config` - 更新配置
- `GET /api/models` - 可用模型列表

## 项目结构

```
gui/
├── server.py              # 后端服务器
├── desktop_app.py         # 桌面应用入口
├── app.js                 # 前端主逻辑
├── index.html             # 主页面
├── styles.css             # 样式表
├── core/                  # 核心模块
│   ├── api-client.js      # API 客户端
│   ├── event-bus.js       # 事件总线
│   └── ...
├── services/              # 业务服务
│   ├── ai-service.js      # AI 服务
│   ├── config-service.js  # 配置服务
│   └── ...
├── start.bat              # Windows 启动脚本
├── start.sh               # Linux/Mac 启动脚本
└── server_config.yaml     # 服务器配置
```

## 使用说明

### 1. 启动应用

运行 `start.bat` (Windows) 或 `start.sh` (Linux/Mac) 启动应用。

### 2. AI 聊天

- 在聊天面板输入问题
- 支持流式响应
- 对话历史自动保存

### 3. 知识库检索

- 切换到 Knowledge 标签
- 输入搜索关键词
- 查看检索结果

### 4. 配置管理

- 修改 `server_config.yaml` 配置服务器
- 通过环境变量配置 AI 模型
- 支持动态切换模型

## 故障排查

### 1. 后端服务器无法启动

```bash
# 检查端口是否被占用
netstat -ano | findstr :5000

# 更换端口
python server.py --port 5001
```

### 2. AI 聊天无响应

- 检查 Ollama/OpenAI 服务是否运行
- 检查环境变量配置
- 查看后端日志：`http://localhost:5000/docs`

### 3. RAG 检索失败

- 确认知识库目录存在
- 检查文档格式是否支持
- 查看 RAG 状态：`GET /api/rag/status`

## 开发指南

### 添加新功能

1. 在 `services/` 目录创建新服务
2. 在 `app.js` 中注册事件监听
3. 更新 UI 界面

### 调试

```bash
# 启用调试模式
python server.py --reload

# 查看日志
# 后端日志输出到控制台
# 前端日志在浏览器开发者工具中
```

### 构建发布

```bash
# 使用 PyInstaller 打包
pip install pyinstaller
pyinstaller build_gui.py
```

## 许可证

MIT License

## 贡献

欢迎提交 Issue 和 Pull Request！

## 联系方式

- 项目地址: https://github.com/yd5768365-hue/mechforge
- 问题反馈: 创建 GitHub Issue
