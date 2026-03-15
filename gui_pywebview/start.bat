@echo off
chcp 65001 >nul
echo.
echo ╔══════════════════════════════════════════════════════════════╗
echo ║           MechForge AI - Desktop Application                 ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.

:: Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python not found! Please install Python 3.10+
    pause
    exit /b 1
)

:: Check dependencies
echo 🔍 Checking dependencies...
python -c "import pywebview" >nul 2>&1
if errorlevel 1 (
    echo 📦 Installing pywebview...
    pip install pywebview
)

python -c "import fastapi" >nul 2>&1
if errorlevel 1 (
    echo 📦 Installing FastAPI...
    pip install fastapi uvicorn
)

echo.
echo 🚀 Starting MechForge AI Desktop...
echo    This will start the backend server and open the desktop window.
echo.

:: Start the application
python desktop_app.py

if errorlevel 1 (
    echo.
    echo ❌ Failed to start application
    pause
)
