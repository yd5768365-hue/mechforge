@echo off
REM MechForge GUI 启动脚本

cd /d "%~dp0"
python -m mechforge_gui_ai.app
if errorlevel 1 pause