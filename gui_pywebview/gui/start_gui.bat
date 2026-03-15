@echo off
chcp 65001 >nul
echo ============================================
echo        MechForge AI GUI 启动器
echo        PyWebView Desktop Application
echo ============================================
echo.

REM 切换到 PyWebView 版本
cd /d "%~dp0..\gui_pywebview"
call start.bat