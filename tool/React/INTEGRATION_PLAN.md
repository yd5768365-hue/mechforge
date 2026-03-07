# MechForge React 版本集成规划

## 📋 项目概述

将现有的 Python 后端功能完整集成到 React 前端，实现前后端分离架构。

## 🏗️ 系统架构

```
┌─────────────────────────────────────────────────────────────┐
│                      React Frontend                         │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐ │
│  │  AI Chat    │  │ Knowledge   │  │    CAE Workbench    │ │
│  │   Mode      │  │   Base      │  │       Mode          │ │
│  └─────────────┘  └─────────────┘  └─────────────────────┘ │
│  ┌─────────────────────────────────────────────────────────┐│
│  │              Context API / Redux Store                  ││
│  └─────────────────────────────────────────────────────────┘│
└──────────────────────────┬──────────────────────────────────┘
                           │ HTTP / WebSocket
┌──────────────────────────▼──────────────────────────────────┐
│                   Python Backend                            │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐ │
│  │  mechforge  │  │ mechforge-k │  │   mechforge-work    │ │
│  │    -ai      │  │             │  │                     │ │
│  └─────────────┘  └─────────────┘  └─────────────────────┘ │
│  ┌─────────────────────────────────────────────────────────┐│
│  │              FastAPI Web Server                         ││
│  └─────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────┘
```

## 📁 文件结构规划

```
React/
├── public/
│   └── index.html
├── src/
│   ├── components/           # 通用组件
│   │   ├── Layout/          # 布局组件
│   │   │   ├── Sidebar.jsx      # 侧边栏
│   │   │   ├── TitleBar.jsx     # 标题栏
│   │   │   ├── StatusBar.jsx    # 状态栏
│   │   │   └── index.js
│   │   ├── Common/          # 通用UI组件
│   │   │   ├── GlassCard.jsx    # 玻璃态卡片
│   │   │   ├── NeonButton.jsx   # 霓虹按钮
│   │   │   ├── ProgressBar.jsx  # 进度条
│   │   │   └── index.js
│   │   └── Icons/           # 图标组件
│   │       └── index.jsx
│   │
│   ├── modes/               # 三种模式页面
│   │   ├── AIAssistant/     # AI助手模式
│   │   │   ├── ChatPanel.jsx    # 聊天面板
│   │   │   ├── MessageBubble.jsx # 消息气泡
│   │   │   ├── InputArea.jsx    # 输入区域
│   │   │   ├── hooks/
│   │   │   │   └── useChat.js   # 聊天逻辑Hook
│   │   │   └── index.jsx
│   │   │
│   │   ├── KnowledgeBase/   # 知识库模式
│   │   │   ├── SearchPanel.jsx  # 搜索面板
│   │   │   ├── DocumentList.jsx # 文档列表
│   │   │   ├── IndexProgress.jsx # 索引进度
│   │   │   ├── hooks/
│   │   │   │   └── useKnowledge.js
│   │   │   └── index.jsx
│   │   │
│   │   └── Workbench/       # 工具台模式
│   │       ├── ToolPanel.jsx    # 工具面板
│   │       ├── Console.jsx      # 控制台
│   │       ├── Viewer3D.jsx     # 3D预览
│   │       ├── ProgressPanel.jsx # 进度面板
│   │       ├── hooks/
│   │       │   └── useWorkbench.js
│   │       └── index.jsx
│   │
│   ├── services/            # API服务层
│   │   ├── api.js           # Axios实例配置
│   │   ├── aiService.js     # AI对话API
│   │   ├── knowledgeService.js # 知识库API
│   │   ├── workbenchService.js # 工具台API
│   │   └── websocket.js     # WebSocket连接
│   │
│   ├── store/               # 状态管理
│   │   ├── index.js         # Store配置
│   │   ├── slices/
│   │   │   ├── appSlice.js      # 应用状态
│   │   │   ├── chatSlice.js     # 聊天状态
│   │   │   ├── knowledgeSlice.js # 知识库状态
│   │   │   └── workbenchSlice.js # 工具台状态
│   │   └── hooks/
│   │       └── useStore.js
│   │
│   ├── hooks/               # 全局Hooks
│   │   ├── useWebSocket.js
│   │   ├── useStreaming.js
│   │   └── useTheme.js
│   │
│   ├── utils/               # 工具函数
│   │   ├── constants.js     # 常量定义
│   │   ├── helpers.js       # 辅助函数
│   │   └── formatters.js    # 格式化函数
│   │
│   ├── styles/              # 样式文件
│   │   ├── global.css       # 全局样式
│   │   ├── theme.js         # 主题配置
│   │   └── animations.css   # 动画样式
│   │
│   ├── App.jsx              # 主应用组件
│   ├── main.jsx             # 入口文件
│   └── index.js             # 导出
│
├── package.json
├── vite.config.js           # Vite配置
└── INTEGRATION_PLAN.md      # 本文件
```

## 🔌 API 接口设计

### 1. AI 对话接口

```javascript
// services/aiService.js

// 发送消息（流式）
export const sendMessageStream = async (message, history, onChunk) => {
  const response = await fetch('/api/chat/stream', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message, history }),
  });
  
  const reader = response.body.getReader();
  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    onChunk(new TextDecoder().decode(value));
  }
};

// 获取模型列表
export const getModels = () => api.get('/api/models');

// 切换模型
export const switchModel = (modelId) => api.post('/api/models/switch', { modelId });
```

**后端对应**: `mechforge_ai/llm_client.py`

### 2. 知识库接口

```javascript
// services/knowledgeService.js

// 搜索文档
export const searchDocuments = (query, topK = 5) => 
  api.post('/api/knowledge/search', { query, top_k: topK });

// 获取文档列表
export const getDocuments = () => api.get('/api/knowledge/documents');

// 添加文档
export const addDocument = (file) => {
  const formData = new FormData();
  formData.append('file', file);
  return api.post('/api/knowledge/documents', formData);
};

// 删除文档
export const deleteDocument = (docId) => 
  api.delete(`/api/knowledge/documents/${docId}`);

// 获取索引状态
export const getIndexStatus = () => api.get('/api/knowledge/index-status');
```

**后端对应**: `mechforge_knowledge/backends/local_backend.py`

### 3. 工具台接口

```javascript
// services/workbenchService.js

// 导入几何文件
export const importGeometry = (file) => {
  const formData = new FormData();
  formData.append('file', file);
  return api.post('/api/cae/import', formData);
};

// 生成网格
export const generateMesh = (params) => 
  api.post('/api/cae/mesh', params);

// 运行求解
export const runSolver = (config) => 
  api.post('/api/cae/solve', config);

// 获取计算进度（WebSocket）
export const connectProgressWS = (onProgress) => {
  const ws = new WebSocket('ws://localhost:8000/ws/cae/progress');
  ws.onmessage = (e) => onProgress(JSON.parse(e.data));
  return ws;
};

// 获取结果
export const getResults = (jobId) => 
  api.get(`/api/cae/results/${jobId}`);
```

**后端对应**: `mechforge_work/cae_core.py`

## 🎯 组件集成方案

### 1. AI助手模式集成

```jsx
// modes/AIAssistant/index.jsx
import { useChat } from './hooks/useChat';
import { ChatPanel } from './ChatPanel';
import { InputArea } from './InputArea';

export const AIAssistantMode = () => {
  const { messages, sendMessage, isStreaming } = useChat();
  
  return (
    <div className="ai-mode">
      <ChatPanel messages={messages} />
      <InputArea 
        onSend={sendMessage} 
        disabled={isStreaming}
        placeholder="输入工程问题..."
      />
    </div>
  );
};
```

**集成要点**:
- 使用 WebSocket 实现流式响应
- 消息历史存储在 Redux 中
- 支持 Markdown 渲染
- 代码高亮显示

### 2. 知识库模式集成

```jsx
// modes/KnowledgeBase/index.jsx
import { useKnowledge } from './hooks/useKnowledge';
import { SearchPanel } from './SearchPanel';
import { DocumentList } from './DocumentList';
import { IndexProgress } from './IndexProgress';

export const KnowledgeBaseMode = () => {
  const { 
    documents, 
    searchResults, 
    indexProgress,
    search, 
    addDocument,
    deleteDocument 
  } = useKnowledge();
  
  return (
    <div className="knowledge-mode">
      <SearchPanel onSearch={search} />
      <IndexProgress progress={indexProgress} />
      <DocumentList 
        documents={searchResults || documents}
        onDelete={deleteDocument}
        onAdd={addDocument}
      />
    </div>
  );
};
```

**集成要点**:
- 文件上传使用 FormData
- 索引进度轮询或 WebSocket
- 搜索结果高亮显示
- 支持文件拖拽上传

### 3. 工具台模式集成

```jsx
// modes/Workbench/index.jsx
import { useWorkbench } from './hooks/useWorkbench';
import { ToolPanel } from './ToolPanel';
import { Console } from './Console';
import { Viewer3D } from './Viewer3D';

export const WorkbenchMode = () => {
  const {
    logs,
    progress,
    meshData,
    runCalculation,
    importGeometry
  } = useWorkbench();
  
  return (
    <div className="workbench-mode">
      <ToolPanel 
        onImport={importGeometry}
        onRun={runCalculation}
      />
      <div className="workbench-content">
        <Console logs={logs} />
        <Viewer3D meshData={meshData} />
      </div>
      <ProgressPanel progress={progress} />
    </div>
  );
};
```

**集成要点**:
- 3D可视化使用 Three.js
- 日志实时推送 WebSocket
- 进度条动画效果
- 支持结果导出

## 📡 WebSocket 设计

```javascript
// services/websocket.js

class WebSocketManager {
  constructor() {
    this.connections = new Map();
  }
  
  connect(endpoint, onMessage) {
    const ws = new WebSocket(`ws://localhost:8000${endpoint}`);
    ws.onmessage = (e) => onMessage(JSON.parse(e.data));
    ws.onerror = (e) => console.error('WebSocket error:', e);
    this.connections.set(endpoint, ws);
    return ws;
  }
  
  disconnect(endpoint) {
    const ws = this.connections.get(endpoint);
    if (ws) {
      ws.close();
      this.connections.delete(endpoint);
    }
  }
  
  // AI 流式响应
  connectChatStream(onChunk) {
    return this.connect('/ws/chat', onChunk);
  }
  
  // CAE 进度推送
  connectCAEProgress(onProgress) {
    return this.connect('/ws/cae/progress', onProgress);
  }
  
  // 知识库索引进度
  connectIndexProgress(onProgress) {
    return this.connect('/ws/knowledge/index', onProgress);
  }
}

export const wsManager = new WebSocketManager();
```

## 🎨 主题与样式

```javascript
// styles/theme.js
export const theme = {
  colors: {
    // 背景色
    bgDark: '#0a0e14',
    bgPanel: '#0d1117',
    bgCard: 'rgba(17, 24, 32, 0.7)',
    
    // 霓虹色
    cyan: '#00e5ff',
    cyanDim: 'rgba(0, 229, 255, 0.6)',
    purple: '#8237ff',
    purpleDim: 'rgba(130, 55, 255, 0.5)',
    
    // 文字色
    textPrimary: '#c8d8e0',
    textSecondary: '#5a7a8a',
    
    // 状态色
    success: '#4caf50',
    warning: '#ffca28',
    error: '#ff5252',
  },
  
  glass: {
    background: 'rgba(17, 24, 32, 0.7)',
    border: '1px solid rgba(0, 229, 255, 0.25)',
    boxShadow: '0 0 20px rgba(0, 229, 255, 0.08)',
    backdropFilter: 'blur(10px)',
  },
  
  neon: {
    boxShadow: '0 0 16px rgba(0, 229, 255, 0.4)',
    textShadow: '0 0 8px rgba(0, 229, 255, 0.6)',
  },
};
```

## 🚀 实施步骤

### Phase 1: 基础架构 (1-2天)
1. 创建 React + Vite 项目
2. 配置 Redux Toolkit
3. 设置 Axios 和 WebSocket
4. 创建主题配置

### Phase 2: 核心组件 (2-3天)
1. 实现 Layout 组件（侧边栏、标题栏、状态栏）
2. 创建通用 UI 组件（玻璃卡片、霓虹按钮）
3. 实现三种模式的基础结构

### Phase 3: API集成 (3-4天)
1. 集成 AI 对话 API（流式响应）
2. 集成知识库 API（文件上传、搜索）
3. 集成工具台 API（进度推送）

### Phase 4: 高级功能 (2-3天)
1. 3D可视化（Three.js）
2. Markdown渲染
3. 代码高亮
4. 文件拖拽上传

### Phase 5: 优化测试 (1-2天)
1. 性能优化
2. 错误处理
3. 响应式适配
4. 端到端测试

## 📦 依赖清单

```json
{
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "@reduxjs/toolkit": "^2.0.0",
    "react-redux": "^9.0.0",
    "axios": "^1.6.0",
    "react-markdown": "^9.0.0",
    "prismjs": "^1.29.0",
    "three": "^0.160.0",
    "@react-three/fiber": "^8.15.0",
    "react-dropzone": "^14.2.0",
    "react-hot-toast": "^2.4.0"
  },
  "devDependencies": {
    "@vitejs/plugin-react": "^4.2.0",
    "vite": "^5.0.0",
    "tailwindcss": "^3.3.0",
    "postcss": "^8.4.0",
    "autoprefixer": "^10.4.0"
  }
}
```

## 🔧 后端适配

需要确保 Python 后端支持以下功能：

1. **CORS 配置**
```python
# mechforge_web/main.py
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

2. **WebSocket 支持**
```python
# 确保已有 WebSocket 端点
@app.websocket("/ws/chat")
async def websocket_chat(websocket: WebSocket):
    await websocket.accept()
    # ... 处理流式响应
```

3. **静态文件服务**
```python
# 生产环境服务 React 构建文件
app.mount("/", StaticFiles(directory="dist", html=True))
```

## 📚 参考文档

- [React 官方文档](https://react.dev/)
- [Redux Toolkit](https://redux-toolkit.js.org/)
- [FastAPI WebSocket](https://fastapi.tiangolo.com/advanced/websocket/)
- [Three.js 文档](https://threejs.org/docs/)

---

**规划完成日期**: 2026年3月7日  
**预计开发周期**: 10-14天  
**负责人**: MechForge Team
