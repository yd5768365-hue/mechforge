@echo off
chcp 65001 >nul
echo ==========================================
echo MechForge AI - Python环境设置脚本 (Windows)
echo ==========================================
echo.

REM 检查Python版本
echo [1/5] 检查Python版本...
py --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到Python。请安装Python 3.10+
    exit /b 1
)

for /f "tokens=2" %%a in ('py --version 2^>^&1') do set PYTHON_VERSION=%%a
echo [OK] 找到Python %PYTHON_VERSION%

REM 创建虚拟环境
echo.
echo [2/5] 创建虚拟环境...
if exist ".venv" (
    echo [提示] 虚拟环境已存在，跳过创建
) else (
    py -3.12 -m venv .venv
    if errorlevel 1 (
        echo [警告] Python 3.12不可用，尝试使用默认版本
        py -m venv .venv
    )
    echo [OK] 虚拟环境创建完成
)

REM 激活虚拟环境
echo.
echo [3/5] 激活虚拟环境...
call .venv\Scripts\activate.bat
if errorlevel 1 (
    echo [错误] 无法激活虚拟环境
    exit /b 1
)
echo [OK] 虚拟环境已激活

REM 升级pip
echo.
echo [4/5] 升级pip...
python -m pip install --upgrade pip setuptools wheel -q
echo [OK] pip已升级

REM 安装依赖
echo.
echo [5/5] 安装项目依赖...
echo 安装基础依赖...
pip install -e . -q

echo.
echo 安装开发依赖...
pip install -e ".[dev]" -q

echo.
echo 安装完整功能依赖（这可能需要几分钟）...
pip install -e ".[all]" -q

echo.
echo [OK] 依赖安装完成

REM 验证安装
echo.
echo ==========================================
echo 验证安装...
echo ==========================================
python -c "import mechforge_core; print('[OK] mechforge_core 导入成功')"
python -c "import mechforge_ai; print('[OK] mechforge_ai 导入成功')"
python -c "import mechforge_knowledge; print('[OK] mechforge_knowledge 导入成功')"
python -c "import mechforge_work; print('[OK] mechforge_work 导入成功')"
python -c "import mechforge_web; print('[OK] mechforge_web 导入成功')"
python -c "import mechforge_gui_ai; print('[OK] mechforge_gui_ai 导入成功')"

echo.
echo ==========================================
echo 环境设置完成！
echo ==========================================
echo.
echo 使用方法:
echo   1. 激活环境: .venv\Scripts\activate.bat
echo   2. 运行程序: mechforge
echo   3. 运行GUI:  mechforge-gui
echo   4. 运行Web:  mechforge-web
echo.
echo 常用命令:
echo   mechforge --help
echo   mechforge-k --help
echo   mechforge-work --help
echo.
pause
