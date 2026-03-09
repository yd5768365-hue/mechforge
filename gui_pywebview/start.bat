@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

:: MechForge AI 启动脚本
:: 支持: 正常启动、调试模式、服务器模式

set "SCRIPT_DIR=%~dp0"
cd /d "%SCRIPT_DIR%"

:: 解析参数
set "MODE=normal"
set "PORT=5000"
set "DEBUG="

:parse_args
if "%~1"=="" goto :run
if /i "%~1"=="--debug" set "MODE=debug" & set "DEBUG=--debug"
if /i "%~1"=="--server" set "MODE=server"
if /i "%~1"=="--port" set "PORT=%~2" & shift
if /i "%~1"=="--help" goto :show_help
shift
goto :parse_args

:show_help
echo.
echo MechForge AI v0.5.0 - 启动脚本
echo.
echo 用法: start.bat [选项]
echo.
echo 选项:
echo   --debug      以调试模式启动（开启 DevTools）
echo   --server     仅启动后端服务器
echo   --port PORT  指定端口号（默认: 5000）
echo   --help       显示此帮助信息
echo.
goto :eof

:run
echo.
echo ╔════════════════════════════════════════════════════════════╗
echo ║                    MechForge AI v0.5.0                     ║
echo ║               PyWebView 轻量级桌面应用                       ║
echo ╚════════════════════════════════════════════════════════════╝
echo.

:: 检查 Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到 Python，请先安装 Python 3.10+
    goto :error
)

:: 检查依赖
python -c "import webview" >nul 2>&1
if errorlevel 1 (
    echo [警告] 缺少依赖，正在安装...
    pip install -r requirements.txt
)

:: 根据模式启动
if "%MODE%"=="server" (
    echo [信息] 启动后端服务器（端口: %PORT%）...
    python -m uvicorn server:app --host 127.0.0.1 --port %PORT% --reload
) else (
    if "%MODE%"=="debug" (
        echo [信息] 以调试模式启动...
    )
    python desktop_app.py %DEBUG%
)

goto :eof

:error
echo.
echo [错误] 启动失败，请检查错误信息
pause
exit /b 1