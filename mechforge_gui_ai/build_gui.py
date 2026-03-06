"""
MechForge GUI 打包脚本

使用 PyInstaller 打包为单文件 exe

使用方法:
    python build_gui.py          # 打包
    python build_gui.py --clean  # 清理后打包
"""

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path


def clean_build():
    """清理构建目录"""
    dirs_to_clean = ["build", "dist", "__pycache__"]
    for dir_name in dirs_to_clean:
        if Path(dir_name).exists():
            shutil.rmtree(dir_name)
            print(f"✓ 已清理: {dir_name}")

    # 清理 .spec 文件
    for spec_file in Path(".").glob("*.spec"):
        spec_file.unlink()
        print(f"✓ 已清理: {spec_file}")


def build_exe():
    """构建 exe"""
    # PyInstaller 参数
    args = [
        sys.executable, "-m", "PyInstaller",
        "--name=MechForge",
        "--onefile",                    # 单文件
        "--windowed",                   # 无控制台窗口
        "--noconfirm",                  # 不确认覆盖
        "--clean",                      # 清理临时文件

        # 添加数据文件
        "--add-data=mechforge_core;mechforge_core",
        "--add-data=mechforge_ai;mechforge_ai",
        "--add-data=mechforge_theme;mechforge_theme",
        "--add-data=mechforge_gui_ai;mechforge_gui_ai",
        "--add-data=mechforge_knowledge;mechforge_knowledge",

        # 隐藏导入
        "--hidden-import=PySide6",
        "--hidden-import=PySide6.QtCore",
        "--hidden-import=PySide6.QtGui",
        "--hidden-import=PySide6.QtWidgets",
        "--hidden-import=rich",
        "--hidden-import=pydantic",
        "--hidden-import=requests",
        "--hidden-import=httpx",
        "--hidden-import=chromadb",
        "--hidden-import=sentence_transformers",

        # 排除不需要的模块
        "--exclude-module=tkinter",
        "--exclude-module=matplotlib",
        "--exclude-module=PIL",
        "--exclude-module=scipy",
        "--exclude-module=numpy.f2py",

        # 图标 (如果存在)
        # "--icon=assets/icon.ico",

        # 入口点
        "-m", "mechforge_gui_ai.app",
    ]

    print("开始打包...")
    print(f"命令: {' '.join(args)}")

    result = subprocess.run(args, cwd=Path(__file__).parent.parent)

    if result.returncode == 0:
        exe_path = Path("dist") / "MechForge.exe"
        if exe_path.exists():
            size_mb = exe_path.stat().st_size / (1024 * 1024)
            print(f"\n✓ 打包成功!")
            print(f"  输出文件: {exe_path.absolute()}")
            print(f"  文件大小: {size_mb:.1f} MB")
        else:
            print("\n✗ 打包失败: 未找到输出文件")
    else:
        print(f"\n✗ 打包失败: 返回码 {result.returncode}")

    return result.returncode


def main():
    parser = argparse.ArgumentParser(description="MechForge GUI 打包脚本")
    parser.add_argument("--clean", action="store_true", help="清理后重新打包")
    args = parser.parse_args()

    # 切换到项目根目录
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)
    print(f"工作目录: {project_root}")

    if args.clean:
        clean_build()

    return build_exe()


if __name__ == "__main__":
    sys.exit(main())