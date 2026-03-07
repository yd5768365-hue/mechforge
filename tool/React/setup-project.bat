@echo off
chcp 65001 >nul
echo ==========================================
echo MechForge React 项目初始化脚本
echo ==========================================
echo.

REM 检查 Node.js
echo [1/5] 检查 Node.js...
node --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到 Node.js，请先安装 Node.js 18+
    exit /b 1
)
echo [OK] Node.js 已安装

REM 创建 Vite 项目
echo.
echo [2/5] 创建 React + Vite 项目...
npm create vite@latest mechforge-react -- --template react
cd mechforge-react

REM 安装依赖
echo.
echo [3/5] 安装核心依赖...
npm install

REM 安装额外依赖
echo.
echo [4/5] 安装 MechForge 所需依赖...
npm install @reduxjs/toolkit react-redux axios react-markdown prismjs three @react-three/fiber react-dropzone react-hot-toast

REM 安装开发依赖
echo.
echo [5/5] 安装开发工具...
npm install -D tailwindcss postcss autoprefixer
npx tailwindcss init -p

echo.
echo ==========================================
echo 项目创建完成！
echo ==========================================
echo.
echo 下一步：
echo   1. cd mechforge-react
echo   2. 按照 INTEGRATION_PLAN.md 创建组件
echo   3. npm run dev
echo.
echo 目录结构：
echo   src/
echo   ├── components/    # 通用组件
echo   ├── modes/         # 三种模式
echo   ├── services/      # API服务
echo   ├── store/         # 状态管理
echo   └── App.jsx        # 主应用
echo.
pause
