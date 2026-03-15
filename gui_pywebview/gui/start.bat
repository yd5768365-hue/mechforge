@echo off
chcp 65001 >nul
echo.
echo ============================================================
echo                   MechForge AI GUI
echo                PyWebView Desktop Application v0.5.0
echo ============================================================
echo.

REM 切换到 PyWebView 版本
cd /d "%~dp0..\gui_pywebview"
call start.bat