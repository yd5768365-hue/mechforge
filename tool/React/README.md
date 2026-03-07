# MechForge UI - React 版本

现代前端框架实现的 MechForge AI 界面。

## 特性

- **HexGrid**: 六边形网格背景图案
- **NodeNetwork**: 节点网络连接线动画
- **Boot Sequence**: 系统启动动画
- **Chat Interface**: 聊天消息界面
- **Blinking Cursor**: 闪烁光标效果
- **SVG Icons**: 矢量图标系统

## 技术栈

- React 18+
- Hooks (useState, useEffect, useRef)
- Inline Styles (无需CSS文件)

## 安装

```bash
# 创建React项目
npx create-react-app mechforge-ui
cd mechforge-ui

# 或使用Vite
npm create vite@latest mechforge-ui -- --template react
```

## 使用方法

1. 将 `MechForgeUI.jsx` 复制到 `src/` 目录
2. 在 `App.js` 中导入使用：

```jsx
import MechForgeUI from './MechForgeUI';

function App() {
  return <MechForgeUI />;
}

export default App;
```

3. 启动开发服务器：

```bash
npm start
# 或
npm run dev
```

## 界面预览

- **标题栏**: 品牌Logo + 窗口控制按钮
- **侧边栏**: 6个功能图标（AI助手、安全、文档、扫描、插件、数据库）
- **主面板**: 
  - 六边形网格背景
  - 节点网络装饰
  - 启动日志动画
  - 聊天消息区
  - 输入框 + 发送按钮
- **状态栏**: API/模型/RAG/内存状态

## 交互功能

- 点击侧边栏图标切换功能
- 输入框输入消息，Enter或点击Send发送
- 模拟AI回复（800ms延迟）
- 启动动画逐行显示
- 光标闪烁效果

## 配色方案

| 颜色 | 色值 | 用途 |
|------|------|------|
| 背景色 | `#0a0e14` | 主背景 |
| 面板色 | `#0d1117` | 面板背景 |
| 青色霓虹 | `#00e5ff` | 强调色 |
| 冷白 | `#c8d8e0` | 主文字 |
| 暗灰 | `#3a5068` | 次要文字 |

## 文件结构

```
React/
├── MechForgeUI.jsx    # 主组件
└── README.md          # 说明文档
```

## 与Python版本对比

| 特性 | Python (DearPyGUI) | React |
|------|-------------------|-------|
| 运行环境 | 本地桌面 | 浏览器/Web |
| 启动速度 | 快 | 需构建 |
| 动画效果 | 基础 | 流畅 |
| 部署方式 | 打包exe | 网页托管 |
| AI集成 | 直接调用 | 需API |

## 后续优化方向

- [ ] 接入真实AI API
- [ ] 添加WebSocket实时通信
- [ ] 响应式布局适配
- [ ] 暗黑/亮色主题切换
- [ ] 多语言支持
