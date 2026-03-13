@echo off
chcp 65001 >nul
echo 构建 MechForge AI PyWebView 桌面应用...
echo.

cd /d "%~dp0"
python build.py --build

pause