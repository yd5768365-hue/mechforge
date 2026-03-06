"""
MechForge GUI 轻量打包脚本

排除大型依赖（torch/transformers），仅打包核心功能
"""

import subprocess
import sys
from pathlib import Path


def build_light():
    """轻量打包 - 不包含大型ML库"""
    args = [
        sys.executable, "-m", "PyInstaller",
        "--name=MechForge",
        "--onefile",
        "--windowed",
        "--noconfirm",
        "--clean",

        # 添加数据文件
        "--add-data=mechforge_core;mechforge_core",
        "--add-data=mechforge_ai;mechforge_ai",
        "--add-data=mechforge_theme;mechforge_theme",
        "--add-data=mechforge_gui_ai;mechforge_gui_ai",

        # 隐藏导入
        "--hidden-import=PySide6",
        "--hidden-import=PySide6.QtCore",
        "--hidden-import=PySide6.QtGui",
        "--hidden-import=PySide6.QtWidgets",
        "--hidden-import=rich",
        "--hidden-import=pydantic",
        "--hidden-import=requests",
        "--hidden-import=httpx",

        # 排除大型依赖
        "--exclude-module=torch",
        "--exclude-module=transformers",
        "--exclude-module=sklearn",
        "--exclude-module=pandas",
        "--exclude-module=numpy",
        "--exclude-module=matplotlib",
        "--exclude-module=PIL",
        "--exclude-module=scipy",
        "--exclude-module=tkinter",
        "--exclude-module=PyQt5",
        "--exclude-module=PyQt6",
        "--exclude-module=PySide2",
        "--exclude-module=chromadb",
        "--exclude-module=sentence_transformers",
        "--exclude-module=llama_cpp",

        # 入口点
        "mechforge_gui_ai/app.py",
    ]

    print("开始轻量打包（不包含torch/transformers）...")
    result = subprocess.run(args, cwd=Path(__file__).parent)

    if result.returncode == 0:
        exe_path = Path("dist") / "MechForge.exe"
        if exe_path.exists():
            size_mb = exe_path.stat().st_size / (1024 * 1024)
            print(f"\n[OK] 打包成功!")
            print(f"  输出文件: {exe_path.absolute()}")
            print(f"  文件大小: {size_mb:.1f} MB")
            print(f"\n注意：此版本不包含本地模型支持（GGUF/Ollama）")
            print(f"      如需完整功能，请使用完整版打包脚本")
    else:
        print(f"\n[ERROR] 打包失败: 返回码 {result.returncode}")

    return result.returncode


if __name__ == "__main__":
    sys.exit(build_light())
