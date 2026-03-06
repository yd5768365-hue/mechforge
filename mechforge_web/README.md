# MechForge Web - Web UI

基于 FastAPI + WebSocket 的现代化 Web 界面。

## 特性

- 🎨 **现代化界面**：响应式设计，支持深色/浅色主题
- ⚡ **实时通信**：WebSocket 实现流式 AI 对话
- 🔧 **三模式集成**：AI 对话、知识库、CAE 工作台
- 📱 **移动端支持**：自适应布局，支持手机/平板
- 🚀 **高性能**：异步处理，支持多并发连接

## 快速开始

### 安装

```bash
pip install mechforge-ai[web]

# 或完整版（包含所有功能）
pip install mechforge-ai[web-full]
```

### 启动

```bash
# 命令行启动
mechforge-web

# 或指定参数
mechforge-web --host 0.0.0.0 --port 8080 --reload

# Python 启动
python -m mechforge_web.main
```

访问 http://localhost:8080

## API 文档

启动后自动生成的文档：

- **Swagger UI**: http://localhost:8080/docs
- **ReDoc**: http://localhost:8080/redoc
- **OpenAPI Schema**: http://localhost:8080/openapi.json

## WebSocket API

连接 WebSocket：

```javascript
const ws = new WebSocket('ws://localhost:8080/ws/chat');

ws.onopen = () => {
    ws.send(JSON.stringify({
        message: '你好',
        rag: true,
        model: 'ollama'
    }));
};

ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    console.log(data);
};
```

消息格式：

```typescript
// 发送
interface ChatRequest {
    message: string;
    model?: string;      // 'ollama' | 'openai' | 'anthropic'
    rag?: boolean;       // 是否启用知识库
}

// 接收
interface ChatResponse {
    type: 'ack' | 'stream_start' | 'stream' | 'stream_end' | 'error';
    messageId?: string;
    content?: string;
    message?: string;
}
```

## REST API

### 聊天

```bash
# 非流式聊天
POST /api/chat
Content-Type: application/json

{
    "message": "计算悬臂梁挠度",
    "model": "ollama",
    "rag": true
}

# 获取对话历史
GET /api/chat/history?limit=50

# 清空历史
DELETE /api/chat/history
```

### 知识库

```bash
# 搜索知识库
POST /api/knowledge/search
Content-Type: application/json

{
    "query": "螺栓 GB/T 5782",
    "top_k": 5
}

# 获取状态
GET /api/knowledge/status
```

### CAE

```bash
# 运行示例
POST /api/cae/demo

# 生成网格
POST /api/cae/mesh
Content-Type: application/json

{
    "size": 2.0,
    "mesh_type": "tet"
}

# 执行求解
POST /api/cae/solve
Content-Type: application/json

{
    "analysis_type": "static",
    "material": "steel"
}

# 获取结果
GET /api/cae/results
```

### 系统

```bash
# 健康检查
GET /api/health

# 获取配置
GET /api/config

# 系统状态
GET /api/system/status
```

## 架构

```
mechforge_web/
├── main.py           # FastAPI 应用入口
├── api.py            # API 路由
├── templates/        # Jinja2 模板
│   └── index.html    # 主页面
└── static/           # 静态资源
    ├── css/
    │   └── style.css
    └── js/
        └── app.js
```

## 开发

```bash
# 安装开发依赖
pip install -e ".[web,dev]"

# 启动开发服务器（热重载）
mechforge-web --reload

# 或
uvicorn mechforge_web.main:app --reload --port 8080
```

## 配置

环境变量：

```bash
# 服务器配置
export MEGHFORGE_WEB_HOST=0.0.0.0
export MEGHFORGE_WEB_PORT=8080

# 其他配置与 CLI 模式相同
export OLLAMA_URL=http://localhost:11434
export MECHFORGE_KNOWLEDGE_PATH=./knowledge
```

## Docker

```bash
# 构建镜像
docker build -t mechforge-web --target web .

# 运行
docker run -p 8080:8080 \
    -v $(pwd)/knowledge:/app/knowledge \
    mechforge-web

# 或使用 docker-compose
docker-compose up mechforge-web
```

## 技术栈

- **后端**: FastAPI, WebSocket, Uvicorn
- **前端**: 原生 JavaScript, Marked (Markdown), Highlight.js
- **样式**: 纯 CSS (无框架，轻量级)
- **图标**: Font Awesome

## 许可证

MIT License
