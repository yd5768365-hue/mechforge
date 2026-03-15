@echo off
chcp 65001 >nul
title MechForge Work - CAE Workbench
echo.
echo  ========================================
echo   MechForge Work - CAE Workbench
echo   Gmsh + CalculiX + PyVista
echo  ========================================
echo.

REM 检查 Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] Python 未安装或未添加到 PATH
    pause
    exit /b 1
)

REM 检查环境
echo 检查环境...
python check_cae_env.py >nul 2>&1
if errorlevel 1 (
    echo.
    echo [警告] 环境检查未通过，尝试安装依赖...
    pip install -e .[work]
    echo.
)

REM 启动 Work 模式
echo.
echo 启动 MechForge Work...
echo.
python -m mechforge_work.work_cli cli

pause
