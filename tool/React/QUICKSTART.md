# MechForge React 快速开始指南

## 🚀 5分钟快速启动

### 1. 一键创建项目

```bash
# Windows
cd tool/React
setup-project.bat

# 或手动执行
cd tool/React
npm create vite@latest mechforge-react -- --template react
cd mechforge-react
npm install
npm install @reduxjs/toolkit react-redux axios react-markdown prismjs three @react-three/fiber react-dropzone react-hot-toast
```

### 2. 复制示例代码

```bash
# 复制服务层
mkdir -p src/services
mkdir -p src/hooks
mkdir -p src/modes/AIAssistant
mkdir -p src/modes/KnowledgeBase
mkdir -p src/modes/Workbench
mkdir -p src/components/Layout
mkdir -p src/store

# 复制示例文件
cp src-example/services/*.js src/services/
cp src-example/hooks/*.js src/hooks/
```

### 3. 创建主应用组件

创建 `src/App.jsx`:

```jsx
import { useState } from 'react';
import { AIAssistantMode } from './modes/AIAssistant';
import { KnowledgeBaseMode } from './modes/KnowledgeBase';
import { WorkbenchMode } from './modes/Workbench';
import { Sidebar } from './components/Layout/Sidebar';
import { TitleBar } from './components/Layout/TitleBar';
import { StatusBar } from './components/Layout/StatusBar';
import './App.css';

function App() {
  const [activeMode, setActiveMode] = useState('assistant');

  return (
    <div className="app">
      <div className="window">
        <TitleBar />
        <div className="body">
          <Sidebar activeMode={activeMode} onModeChange={setActiveMode} />
          <main className="main-panel">
            {activeMode === 'assistant' && <AIAssistantMode />}
            {activeMode === 'knowledge' && <KnowledgeBaseMode />}
            {activeMode === 'workbench' && <WorkbenchMode />}
          </main>
        </div>
        <StatusBar />
      </div>
    </div>
  );
}

export default App;
```

### 4. 添加样式

创建 `src/App.css`:

```css
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: 'Courier New', monospace;
  background: #0a0e14;
  color: #c8d8e0;
}

.app {
  width: 100vw;
  height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
}

.window {
  width: 1000px;
  height: 700px;
  background: #0d1117;
  border: 1px solid #1e2d3d;
  border-radius: 12px;
  box-shadow: 0 0 60px rgba(0,229,255,0.08);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.body {
  flex: 1;
  display: flex;
  overflow: hidden;
}

.main-panel {
  flex: 1;
  position: relative;
  background: #0d1117;
  overflow: hidden;
}
```

### 5. 启动开发服务器

```bash
npm run dev
```

访问 http://localhost:5173

---

## 📦 后端启动

确保 Python 后端已启动：

```bash
# 在项目根目录
cd D:\mechforge_ai
mechforge-web --port 8000
```

---

## 🎯 功能验证清单

### AI 助手模式
- [ ] 输入消息并发送
- [ ] 接收流式响应
- [ ] 查看对话历史
- [ ] 清空对话

### 知识库模式
- [ ] 搜索文档
- [ ] 查看索引进度
- [ ] 上传文件
- [ ] 删除文档

### 工具台模式
- [ ] 导入几何文件
- [ ] 生成网格
- [ ] 查看进度条
- [ ] 查看系统日志

---

## 🔧 常见问题

### 1. CORS 错误

**问题**: `Access-Control-Allow-Origin` 错误

**解决**: 确保后端已配置 CORS

```python
# mechforge_web/main.py
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 2. WebSocket 连接失败

**问题**: WebSocket 无法连接

**解决**: 检查后端 WebSocket 端点

```python
# 确保有以下端点
@app.websocket("/ws/chat")
@app.websocket("/ws/cae/progress")
```

### 3. 流式响应不显示

**问题**: AI 响应不实时显示

**解决**: 检查 `sendMessageStream` 函数

```javascript
// 确保正确处理 ReadableStream
const reader = response.body.getReader();
while (true) {
  const { done, value } = await reader.read();
  if (done) break;
  onChunk(new TextDecoder().decode(value));
}
```

---

## 📚 下一步

1. **阅读完整规划**: [INTEGRATION_PLAN.md](./INTEGRATION_PLAN.md)
2. **查看示例代码**: `src-example/` 目录
3. **参考 Python 后端**: `mechforge_web/` 目录

---

## 🎨 自定义主题

修改 `src/styles/theme.js`:

```javascript
export const theme = {
  colors: {
    cyan: '#00e5ff',
    purple: '#8237ff',
    bgDark: '#0a0e14',
    // ...
  },
};
```

---

**快速开始完成！** 🎉

现在你可以开始开发自己的 MechForge React 应用了。
