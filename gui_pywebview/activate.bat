@echo off
REM MechForge AI - 快速激活虚拟环境 (Windows)

if exist ".venv\Scripts\activate.bat" (
    call .venv\Scripts\activate.bat
    echo [MechForge] 虚拟环境已激活
    echo.
    echo 可用命令:
    echo   mechforge        - 启动AI对话
    echo   mechforge-gui    - 启动GUI应用
    echo   mechforge-web    - 启动Web服务
    echo   mechforge-k      - 启动知识库
    echo   mechforge-work   - 启动CAE工作台
    echo.
) else (
    echo [错误] 虚拟环境不存在，请先运行 setup_env.bat
)
