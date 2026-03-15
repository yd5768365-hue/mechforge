@echo off
chcp 65001 >nul
title MechForge AI - 安装程序
echo.
echo ==========================================
echo    MechForge AI - 机械工程智能助手
echo    版本: 0.4.0
echo ==========================================
echo.

REM 检查管理员权限
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo [警告] 建议以管理员身份运行此脚本
    echo.
    pause
)

REM 设置安装目录
set "INSTALL_DIR=%USERPROFILE%\MechForge-AI"
set "DESKTOP_LINK=%USERPROFILE%\Desktop\MechForge AI.lnk"
set "START_MENU=%APPDATA%\Microsoft\Windows\Start Menu\Programs\MechForge AI"

echo [1/5] 准备安装...
echo     安装目录: %INSTALL_DIR%
echo.

REM 检查是否已安装
if exist "%INSTALL_DIR%" (
    echo [提示] 检测到已安装版本
    set /p OVERWRITE="是否覆盖安装? (Y/N): "
    if /i not "!OVERWRITE!"=="Y" (
        echo 安装已取消
        goto :END
    )
    rmdir /s /q "%INSTALL_DIR%"
)

REM 创建安装目录
echo [2/5] 创建安装目录...
mkdir "%INSTALL_DIR%" 2>nul
mkdir "%INSTALL_DIR%\config" 2>nul
mkdir "%INSTALL_DIR%\knowledge" 2>nul
mkdir "%INSTALL_DIR%\logs" 2>nul
mkdir "%START_MENU%" 2>nul
echo     完成
echo.

REM 复制文件
echo [3/5] 复制程序文件...
if exist "..\dist\MechForge-AI.exe" (
    copy "..\dist\MechForge-AI.exe" "%INSTALL_DIR%\" >nul
) else if exist "..\MechForge-AI.exe" (
    copy "..\MechForge-AI.exe" "%INSTALL_DIR%\" >nul
) else (
    echo [错误] 找不到 MechForge-AI.exe
    echo        请先运行 build_gui_complete.py 进行打包
    pause
    exit /b 1
)

REM 复制默认配置
if exist "..\build_complete\config\default_config.yaml" (
    copy "..\build_complete\config\default_config.yaml" "%INSTALL_DIR%\config\config.yaml" >nul
)
echo     完成
echo.

REM 创建启动脚本
echo [4/5] 创建快捷方式...
(
echo @echo off
echo chcp 65001 ^>nul
echo set "MECHFORGE_CONFIG_PATH=%%~dp0config\config.yaml"
echo set "MECHFORGE_KNOWLEDGE_PATH=%%~dp0knowledge"
echo set "MECHFORGE_LOG_PATH=%%~dp0logs"
echo start "" "%%~dp0MechForge-AI.exe"
) > "%INSTALL_DIR%\启动 MechForge AI.bat"

REM 创建卸载脚本
(
echo @echo off
echo echo 正在卸载 MechForge AI...
echo rmdir /s /q "%INSTALL_DIR%"
echo rmdir /s /q "%START_MENU%"
echo del "%DESKTOP_LINK%" 2^>nul
echo echo 卸载完成
echo pause
) > "%INSTALL_DIR%\卸载.bat"

REM 创建桌面快捷方式（使用 PowerShell）
powershell -Command "$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%DESKTOP_LINK%'); $Shortcut.TargetPath = '%INSTALL_DIR%\启动 MechForge AI.bat'; $Shortcut.IconLocation = '%INSTALL_DIR%\MechForge-AI.exe'; $Shortcut.WorkingDirectory = '%INSTALL_DIR%'; $Shortcut.Save()" 2>nul

REM 创建开始菜单快捷方式
powershell -Command "$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%START_MENU%\MechForge AI.lnk'); $Shortcut.TargetPath = '%INSTALL_DIR%\启动 MechForge AI.bat'; $Shortcut.IconLocation = '%INSTALL_DIR%\MechForge-AI.exe'; $Shortcut.WorkingDirectory = '%INSTALL_DIR%'; $Shortcut.Save()" 2>nul

echo     完成
echo.

REM 检查 Ollama
echo [5/5] 检查 Ollama 环境...
where ollama >nul 2>&1
if %errorLevel% equ 0 (
    echo     Ollama 已安装
echo.
    echo     检查默认模型...
    ollama list | findstr "qwen2.5:1.5b" >nul
    if %errorLevel% equ 0 (
        echo     默认模型已存在
    ) else (
        echo     默认模型未安装，首次运行时会自动下载
    )
) else (
    echo     [提示] Ollama 未安装
    echo.
    echo     MechForge AI 使用 Ollama 运行本地 AI 模型。
    echo     请访问 https://ollama.com/download 下载安装
    echo     或使用以下命令安装:
    echo         winget install Ollama.Ollama
)
echo.

echo ==========================================
echo    安装完成！
echo ==========================================
echo.
echo 安装目录: %INSTALL_DIR%
echo.
echo 启动方式:
echo   1. 桌面快捷方式: MechForge AI
echo   2. 开始菜单: MechForge AI
echo   3. 安装目录: %INSTALL_DIR%\启动 MechForge AI.bat
echo.
echo 提示:
echo   - 首次运行会自动创建用户配置
echo   - 知识库文件可放入: %INSTALL_DIR%\knowledge\
echo   - 配置文件位置: %INSTALL_DIR%\config\config.yaml
echo.

:END
pause
