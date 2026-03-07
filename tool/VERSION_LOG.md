# MechForge Tool 版本迭代记录

## 版本命名规范
- `mechforge_tool_v{n}.py` - 第n个迭代版本
- 每次更新创建新版本文件，保留历史版本
- 最新版本在文档底部

---

## v1 - 基础功能版
**文件名**: `mechforge_tool_v1.py`

**创建时间**: 2026年3月7日

**功能特性**:
- 基础DearPyGUI界面框架
- 三种模式：AI对话、知识库、工具台
- 集成AI聊天功能（异步调用）
- 微软雅黑中文字体支持
- 赛博朋克配色方案

**界面元素**:
- 左侧导航栏（文字按钮）
- 聊天历史区
- 输入框和发送按钮
- 底部状态栏

---

## v2 - 美化升级版
**文件名**: `mechforge_tool_v2.py`

**创建时间**: 2026年3月7日

**功能特性**:
- 保留v1所有功能
- Unicode符号图标（🤖📚🛠️⚙️）
- 聊天气泡组件（AI青色/用户紫色）
- HUD机械装饰线
- 无缝布局（去边框）

**界面改进**:
- 左侧导航：Unicode图标 + 极简排版
- 聊天气泡：圆角 + 独立背景色 + 左右对齐
- 发光装饰线：顶部/左侧/底部霓虹线
- 紧凑布局：零边框 + 发光线界定

---

## 版本对比

| 特性 | v1 | v2 |
|------|-----|-----|
| 基础界面 | ✅ | ✅ |
| AI聊天 | ✅ | ✅ |
| 中文支持 | ✅ | ✅ |
| Unicode图标 | ❌ | ✅ |
| 聊天气泡 | ❌ | ✅ |
| HUD装饰线 | ❌ | ✅ |
| 无缝布局 | ❌ | ✅ |

---

## 使用说明

### 运行最新版本
```bash
cd tool
python mechforge_tool_v2.py
```

### 运行历史版本
```bash
python mechforge_tool_v1.py
```

---

## React 版本
**文件夹**: `React/`

**创建时间**: 2026年3月7日

**技术栈**: React 18 + Hooks

**功能特性**:
- 现代前端框架实现
- HexGrid 六边形网格背景
- NodeNetwork 节点网络动画
- Boot Sequence 启动动画
- Chat Interface 聊天界面
- Blinking Cursor 闪烁光标
- SVG Icon System 矢量图标

**文件结构**:
```
React/
├── MechForgeUI.jsx    # 主组件
└── README.md          # 使用说明
```

**使用方法**:
```bash
cd React
# 创建React项目并复制组件
npx create-react-app mechforge-ui
cp MechForgeUI.jsx mechforge-ui/src/
cd mechforge-ui
npm start
```

---

## React v3 - 多模式完整版
**文件名**: `React/MechForgeUI_v3.jsx`

**创建时间**: 2026年3月7日

**功能特性**:
- 玻璃态 + 霓虹青色调设计
- 三种完整模式：AI助手、知识库、工具台
- 知识库面板：搜索框 + 索引进度 + 文档列表
- 工具台面板：工具栏 + 进度条 + 日志区 + 3D预览
- 动态进度动画
- 响应式交互效果

**新增组件**:
- `KnowledgeBasePanel`: 知识库搜索与管理
- `WorkbenchPanel`: CAE工具台界面

**界面改进**:
- 玻璃态卡片设计
- 霓虹发光边框效果
- 文件类型彩色图标
- 3D线框立方体预览
- 实时日志输出

**文件结构**:
```
React/
├── MechForgeUI.jsx      # v2版本
├── MechForgeUI_v3.jsx   # v3最新版本
└── README.md
```

---

## 版本对比总表

| 特性 | Python v1 | Python v2 | React v2 | React v3 |
|------|-----------|-----------|----------|----------|
| 基础界面 | ✅ | ✅ | ✅ | ✅ |
| AI聊天 | ✅ | ✅ | ✅ | ✅ |
| 中文支持 | ✅ | ✅ | ✅ | ✅ |
| Unicode图标 | ❌ | ✅ | ✅ | ✅ |
| 聊天气泡 | ❌ | ✅ | ❌ | ❌ |
| HUD装饰线 | ❌ | ✅ | ✅ | ✅ |
| 知识库模式 | ✅ | ✅ | ❌ | ✅ |
| 工具台模式 | ✅ | ✅ | ❌ | ✅ |
| 玻璃态设计 | ❌ | ❌ | ❌ | ✅ |
| 霓虹发光 | ❌ | ❌ | ✅ | ✅ |

---

## React 集成规划
**文档**: `React/INTEGRATION_PLAN.md`

**创建时间**: 2026年3月7日

**规划内容**:
- 系统架构设计（前后端分离）
- 文件结构规划（组件/服务/状态管理）
- API接口设计（AI/知识库/工具台）
- WebSocket实时通信方案
- 组件集成方案（三种模式）
- 实施步骤（5个阶段）

**示例代码**:
```
React/src-example/
├── services/
│   ├── api.js              # Axios配置
│   ├── aiService.js        # AI对话API
│   ├── knowledgeService.js # 知识库API
│   └── workbenchService.js # 工具台API
└── hooks/
    ├── useChat.js          # 聊天Hook
    ├── useKnowledge.js     # 知识库Hook
    └── useWorkbench.js     # 工具台Hook
```

**快速开始**:
```bash
cd React
setup-project.bat           # Windows一键创建
# 或手动：npm create vite@latest mechforge-react -- --template react
```

**开发周期**: 10-14天

---

## 更新记录

- **v1** (2026-03-07): 初始版本，基础功能
- **v2** (2026-03-07): 美化升级，Unicode图标+气泡+装饰线
- **React v2** (2026-03-07): 现代前端框架版本
- **React v3** (2026-03-07): 多模式完整版，玻璃态+霓虹设计
- **React 集成规划** (2026-03-07): 完整集成方案与示例代码
- **React 项目整合** (2026-03-07): 将 pasted_code 整合到 mechforge-ui 项目
- **粒子特效背景** (2026-03-07): 添加150个粒子的动态粒子场
- **吉祥物鲸鱼** (2026-03-07): 添加DJ鲸鱼吉祥物到聊天界面
- **Electron桌面应用** (2026-03-07): 将React项目打包为桌面.exe应用

---

## Electron桌面应用打包
**时间**: 2026年3月7日

**4步操作流程**:

### 1️⃣ 安装Electron依赖
```bash
npm install electron vite-plugin-electron electron-builder -D
npm install vite @vitejs/plugin-react -D
```

### 2️⃣ 创建electron/main.js
- 窗口大小: 1200x800 (最小900x600)
- 自动隐藏菜单栏
- 支持开发/生产环境切换

### 3️⃣ 配置vite.config.js
- 集成vite-plugin-electron
- 指向electron/main.js入口

### 4️⃣ 修改package.json
- 添加`"type": "module"`
- 添加`"main": "dist-electron/main.js"`
- 添加electron-builder配置
- 新增build脚本

**新增文件**:
```
mechforge-ui/
├── electron/
│   └── main.js          # Electron主进程
├── vite.config.js       # Vite配置
├── index.html           # Vite入口HTML
└── package.json         # 更新配置
```

**可用命令**:
```bash
npm run dev      # 开发模式 (Vite + Electron)
npm run build    # 打包为.exe安装程序
```

**输出位置**: `release/`文件夹

---

## React 项目整合完成
**项目路径**: `React/mechforge-ui/`

**整合时间**: 2026年3月7日

**整合内容**:
将 pasted_code.jsx 中的代码模块化整合到标准 React 项目结构中

**文件结构**:
```
mechforge-ui/src/
├── components/           # 可复用组件
│   ├── HexGrid.jsx      # 六边形网格背景
│   ├── NodeNetwork.jsx  # 节点网络动画
│   ├── BootLine.jsx     # 启动日志行
│   ├── Sidebar.jsx      # 侧边栏导航
│   └── index.js         # 统一导出
├── modes/               # 三种模式页面
│   ├── AIAssistant.jsx  # AI助手模式
│   ├── KnowledgeBase.jsx # 知识库模式
│   ├── Workbench.jsx    # 工具台模式
│   └── index.js         # 统一导出
├── App.js               # 主应用组件
├── App.css              # 应用样式
└── index.css            # 全局样式
```

**组件拆分**:
| 原文件 | 拆分后 |
|--------|--------|
| pasted_code.jsx | 8个独立文件 |
| HexGrid | components/HexGrid.jsx |
| NodeNetwork | components/NodeNetwork.jsx |
| BootLine | components/BootLine.jsx |
| Sidebar | components/Sidebar.jsx |
| AIAssistant | modes/AIAssistant.jsx |
| KnowledgeBase | modes/KnowledgeBase.jsx |
| Workbench | modes/Workbench.jsx |
| MechForgeUI | App.js |

**运行方式**:
```bash
cd React/mechforge-ui
npm start
```

**访问地址**: http://localhost:3000

---

## 粒子特效背景
**文件**: `React/mechforge-ui/src/components/ParticleField.jsx`

**添加时间**: 2026年3月7日

**设计特点**:
- **150个粒子** - 大量粒子营造丰富视觉效果
- **动态连线** - 近距离粒子自动连线
- **鼠标交互** - 粒子会避开鼠标移动
- **脉冲发光** - 粒子呼吸灯效果
- **青色霓虹** - 多种青色渐变色调
- **Canvas渲染** - 高性能动画

**技术参数**:
```javascript
particleCount: 400,        // 粒子数量 - 大量粒子！
connectionDistance: 120,   // 连线距离
mouseDistance: 180,        // 鼠标交互距离
speed: 0.6,                // 基础速度
colors: ["#00e5ff", "#00b8d4", "#0097a7", "#4fc3f7", "#81d4fa", "#b3e5fc"]
```

**层级结构**:
```
App (relative)
├── HexGrid (zIndex: 0)      ← 六边形网格
├── NodeNetwork (zIndex: 0)  ← 节点网络
├── ParticleField (zIndex: 1) ← ✨ 粒子特效场
└── Window (zIndex: 10)      ← 主窗口（毛玻璃效果）
```

**效果**: 150个发光粒子在背景中漂浮，相互连线形成网络，鼠标移动时粒子会避让，营造科技感十足的动态背景

---

## 聊天区域粒子特效
**文件**: `React/mechforge-ui/src/components/ChatParticles.jsx`

**添加时间**: 2026年3月7日

**设计特点**:
- **100个粒子** - 聊天区域专用，数量丰富
- **适中速度** - 0.4速度，柔和动态
- **更低透明度** - 0.1-0.4透明度，不干扰文字
- **自动连线** - 粒子间自动连线
- **呼吸效果** - 脉冲发光动画

**层级结构**:
```
AIAssistant
├── ChatParticles (zIndex: 0)   ← 粒子背景
└── 聊天内容 (zIndex: 2)         ← 文字内容在粒子上方
```

**效果**: 聊天界面内部也有粒子漂浮，文字清晰可读，背景动态有趣

---

## 吉祥物鲸鱼
**文件**: 
- `React/mechforge-ui/src/components/MascotWhale.jsx`
- `React/mechforge-ui/public/dj-whale.png`

**添加时间**: 2026年3月7日

**设计特点**:
- **位置** - 聊天界面右下角
- **透明度** - 15%透明度，作为背景暗纹
- **发光效果** - 青色霓虹发光阴影
- **悬浮动画** - 6秒循环上下浮动+旋转
- **鼠标穿透** - 不影响点击操作

**动画效果**:
```css
@keyframes floatDJ {
  0%, 100% { transform: translateY(0px) rotate(-2deg); }
  50% { transform: translateY(-20px) rotate(2deg); }
}
```

**层级结构**:
```
AIAssistant (聊天界面)
├── ChatParticles (zIndex: 0)   ← 粒子背景
├── MascotWhale (zIndex: 0)     ← 🐋 吉祥物鲸鱼
└── 聊天内容 (zIndex: 2)         ← 文字内容在最上层
```

**效果**: DJ鲸鱼吉祥物在聊天界面右下角悬浮打碟，青色发光，6秒循环动画，不影响文字阅读

