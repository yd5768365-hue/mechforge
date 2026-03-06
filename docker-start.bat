@echo off
REM MechForge AI - Docker 快速启动脚本 (Windows)

setlocal EnableDelayedExpansion

REM 颜色定义（Windows Terminal 支持）
set "RED=[91m"
set "GREEN=[92m"
set "YELLOW=[93m"
set "BLUE=[94m"
set "NC=[0m"

REM 检查 Docker
docker --version >nul 2>&1
if errorlevel 1 (
    echo %RED%[ERROR]%NC% Docker 未安装，请先安装 Docker Desktop
    exit /b 1
)

REM 检查 Docker Compose
docker compose version >nul 2>&1
if errorlevel 1 (
    docker-compose --version >nul 2>&1
    if errorlevel 1 (
        echo %RED%[ERROR]%NC% Docker Compose 未安装
        exit /b 1
    )
    set "COMPOSE=docker-compose"
) else (
    set "COMPOSE=docker compose"
)

REM 解析命令
set "CMD=%1"
if "%CMD%"=="" set "CMD=help"

REM 执行命令
if "%CMD%"=="start" goto start
if "%CMD%"=="stop" goto stop
if "%CMD%"=="restart" goto restart
if "%CMD%"=="logs" goto logs
if "%CMD%"=="status" goto status
if "%CMD%"=="pull" goto pull
if "%CMD%"=="update" goto update
if "%CMD%"=="clean" goto clean
if "%CMD%"=="help" goto help
if "%CMD%"=="--help" goto help
if "%CMD%"=="-h" goto help
echo %RED%[ERROR]%NC% 未知命令: %CMD%
goto help

:start
set "PROFILE=%2"
if "%PROFILE%"=="" set "PROFILE=full"
echo %BLUE%[INFO]%NC% 启动 MechForge AI (%PROFILE% 模式)...
call :create_dirs
call :init_env
%COMPOSE% --profile %PROFILE% up -d
echo.
echo %GREEN%[SUCCESS]%NC% 服务已启动
echo.
call :show_access_info %PROFILE%
goto :eof

:stop
echo %BLUE%[INFO]%NC% 停止服务...
%COMPOSE% down
echo %GREEN%[SUCCESS]%NC% 服务已停止
goto :eof

:restart
echo %BLUE%[INFO]%NC% 重启服务...
%COMPOSE% restart
echo %GREEN%[SUCCESS]%NC% 服务已重启
goto :eof

:logs
set "SERVICE=%2"
if "%SERVICE%"=="" (
    %COMPOSE% logs -f
) else (
    %COMPOSE% logs -f %SERVICE%
)
goto :eof

:status
%COMPOSE% ps
goto :eof

:pull
echo %BLUE%[INFO]%NC% 拉取最新镜像...
%COMPOSE% pull
echo %GREEN%[SUCCESS]%NC% 镜像已更新
goto :eof

:update
echo %BLUE%[INFO]%NC% 更新服务...
call :pull
call :stop
%COMPOSE% --profile full up -d
echo %GREEN%[SUCCESS]%NC% 服务已更新并重启
goto :eof

:clean
echo %YELLOW%[WARN]%NC% 这将删除所有容器、数据卷和数据！
set /p CONFIRM="确定要继续吗？(y/N) "
if /i "%CONFIRM%"=="y" (
    echo %BLUE%[INFO]%NC% 清理中...
    %COMPOSE% down -v --remove-orphans
    docker system prune -f
    echo %GREEN%[SUCCESS]%NC% 清理完成
) else (
    echo %BLUE%[INFO]%NC% 已取消
)
goto :eof

:help
echo MechForge AI - Docker 快速启动脚本
echo.
echo 用法: %~nx0 [命令] [选项]
echo.
echo 命令:
echo   start [profile]   启动服务 (默认: full)
echo   stop              停止服务
echo   restart           重启服务
echo   logs [service]    查看日志
echo   status            查看状态
echo   pull              拉取最新镜像
echo   update            更新并重启服务
echo   clean             清理所有容器和数据
echo.
echo Profiles:
echo   ai      - AI 对话模式
echo   rag     - 知识库 RAG 模式
echo   work    - CAE 工作台模式
echo   web     - Web 服务模式
echo   full    - 完整版 (默认)
echo.
echo 示例:
echo   %~nx0 start           # 启动完整版
echo   %~nx0 start ai        # 启动 AI 对话模式
echo   %~nx0 logs            # 查看所有日志
echo   %~nx0 logs ollama     # 查看 Ollama 日志
goto :eof

:create_dirs
if not exist "knowledge" mkdir knowledge
if not exist "workdir" mkdir workdir
if not exist "models" mkdir models
if not exist "data" mkdir data
if not exist "logs" mkdir logs
goto :eof

:init_env
if not exist ".env" (
    if exist ".env.example" (
        echo %BLUE%[INFO]%NC% 创建 .env 文件...
        copy .env.example .env >nul
        echo %GREEN%[SUCCESS]%NC% .env 文件已创建
    )
)
goto :eof

:show_access_info
set "PROFILE=%1"
echo.
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo 🚀 MechForge AI 已启动！
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.
if "%PROFILE%"=="ai" (
    echo   模式: AI 对话
    echo   使用: docker-compose exec mechforge-ai python -m mechforge_ai.terminal
)
if "%PROFILE%"=="rag" (
    echo   模式: 知识库 RAG
    echo   使用: docker-compose exec mechforge-k python -m mechforge_knowledge.cli
)
if "%PROFILE%"=="work" (
    echo   模式: CAE 工作台
    echo   使用: docker-compose exec mechforge-work python -m mechforge_work.work_cli
)
if "%PROFILE%"=="web" (
    echo   模式: Web 服务
    echo   访问: http://localhost:8080
    echo   API:  http://localhost:8080/docs
)
if "%PROFILE%"=="full" (
    echo   模式: Web 服务
    echo   访问: http://localhost:8080
    echo   API:  http://localhost:8080/docs
)
echo.
echo   查看日志: %~nx0 logs
echo   停止服务: %~nx0 stop
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
goto :eof