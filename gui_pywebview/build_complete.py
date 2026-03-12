#!/usr/bin/env python3
"""
MechForge AI 完整打包脚本
支持 Windows/Mac/Linux，自动选择最佳打包方式
"""

import argparse
import io
import os
import shutil
import subprocess
import sys
from pathlib import Path

# Fix Windows console encoding for Chinese characters
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

# ═══════════════════════════════════════════════════════════════════════════════
# 配置
# ═══════════════════════════════════════════════════════════════════════════════

PROJECT_NAME = "MechForgeAI"
VERSION = "0.5.0"

SCRIPT_DIR = Path(__file__).parent.resolve()
DIST_DIR = SCRIPT_DIR / "dist"
BUILD_DIR = SCRIPT_DIR / "build"

# 项目根目录（gui_pywebview 的父目录）
PROJECT_ROOT = SCRIPT_DIR.parent.resolve()

# 需要打包的资源
RESOURCES = {
    "files": [
        "index.html",
        "dj-whale.png",
        "experience.js",
    ],
    "dirs": [
        "css",
        "app",
        "core",
        "services",
        "api",
    ],
    # 父项目的模块（mechforge_core, mechforge_ai 等）
    "project_modules": [
        "mechforge_core",
        "mechforge_ai",
        "mechforge_knowledge",
        "mechforge_theme",
    ],
}

# ═══════════════════════════════════════════════════════════════════════════════
# 工具函数
# ═══════════════════════════════════════════════════════════════════════════════


def run(cmd: list, cwd: Path = None, check: bool = True):
    """运行命令"""
    result = subprocess.run(
        cmd,
        cwd=cwd or SCRIPT_DIR,
        capture_output=True,
        text=True,
    )
    if check and result.returncode != 0:
        print(f"❌ 命令失败: {' '.join(cmd)}")
        print(result.stderr)
        sys.exit(1)
    return result


def print_step(msg):
    print(f"\n{'=' * 60}")
    print(f"▶ {msg}")
    print("=" * 60)


def print_success(msg):
    print(f"✅ {msg}")


def print_error(msg):
    print(f"❌ {msg}")


# ═══════════════════════════════════════════════════════════════════════════════
# 打包步骤
# ═══════════════════════════════════════════════════════════════════════════════


def install_dependencies():
    """安装 Python 依赖"""
    print_step("安装依赖")
    run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
    print_success("依赖安装完成")


def check_pyinstaller():
    """检查 PyInstaller"""
    print_step("检查 PyInstaller")
    try:
        import PyInstaller

        print_success(f"PyInstaller {PyInstaller.__version__} 已安装")
    except ImportError:
        print_error("PyInstaller 未安装，正在安装...")
        run([sys.executable, "-m", "pip", "install", "pyinstaller"])
        print_success("PyInstaller 安装完成")


def clean():
    """清理构建目录"""
    print_step("清理构建目录")
    for d in [DIST_DIR, BUILD_DIR]:
        if d.exists():
            shutil.rmtree(d)
            print(f"已删除: {d}")

    # 清理临时文件
    for pattern in ["*.spec", "*.log"]:
        for f in SCRIPT_DIR.glob(pattern):
            f.unlink()
    print_success("清理完成")


def build_windows():
    """Windows 打包"""
    print_step("开始 Windows 打包")

    # 构建数据参数
    datas = []
    for f in RESOURCES["files"]:
        src = SCRIPT_DIR / f
        if src.exists():
            # Windows 使用分号分隔源和目标
            datas.append((str(src), "."))
            print(f"添加文件: {src} -> .")
    for d in RESOURCES["dirs"]:
        src = SCRIPT_DIR / d
        if src.exists():
            # Windows 使用分号分隔源和目标
            datas.append((str(src), d))
            print(f"添加目录: {src} -> {d}")

    cmd = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--name",
        PROJECT_NAME,
        "--onefile",
        "--windowed",
        "--icon",
        "dj-whale.png",
        "--noconfirm",
    ]

    # 添加资源 - 使用元组格式避免路径解析问题
    for src, dst in datas:
        cmd.extend(["--add-data", f"{src}{os.pathsep}{dst}"])

    # 使用 --collect-all 确保所有子模块被正确收集
    for d in RESOURCES["dirs"]:
        src = SCRIPT_DIR / d
        if src.exists() and src.is_dir():
            # 收集整个目录的所有模块
            cmd.extend(["--collect-all", str(src)])

    # 添加父项目的模块（mechforge_core, mechforge_ai 等）
    for module_name in RESOURCES.get("project_modules", []):
        src = PROJECT_ROOT / module_name
        if src.exists() and src.is_dir():
            # 使用 --add-data 将模块目录添加到打包
            datas.append((str(src), module_name))
            cmd.extend(["--add-data", f"{src}{os.pathsep}{module_name}"])
            # 也使用 --collect-all 收集模块
            cmd.extend(["--collect-all", str(src)])
            print(f"添加项目模块: {src} -> {module_name}")

    # 排除不需要的模块
    excludes = [
        "pytest",
        "tests",
        "test",
        "testing",
        "sphinx",
        "docs",
        "docutils",
    ]
    for ex in excludes:
        cmd.extend(["--exclude-module", ex])

    # 添加隐藏导入，确保 Python 内置模块被包含
    hidden_imports = [
        "sqlite3",
        "xml.etree.ElementTree",
        "xml.dom.minidom",
        "html.parser",
        "http.cookies",
        "http.cookiejar",
        "urllib.parse",
        "urllib.request",
        "dataclasses",
        "typing_extensions",
    ]
    for imp in hidden_imports:
        cmd.extend(["--hidden-import", imp])

    # 添加入口
    cmd.append("desktop_app.py")

    print(f"\n执行命令: {' '.join(cmd)}\n")
    run(cmd)

    # 输出结果
    exe_path = DIST_DIR / f"{PROJECT_NAME}.exe"
    if exe_path.exists():
        size = exe_path.stat().st_size / 1024 / 1024
        print_success(f"打包完成: {exe_path} ({size:.1f} MB)")
    else:
        print_error("打包失败，未找到输出文件")


def build_macos():
    """macOS 打包"""
    print_step("开始 macOS 打包")

    cmd = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--name",
        PROJECT_NAME,
        "--onefile",
        "--windowed",
        "--noconfirm",
    ]

    for f in RESOURCES["files"]:
        src = SCRIPT_DIR / f
        if src.exists():
            cmd.extend(["--add-data", f"{src}:."])

    for d in RESOURCES["dirs"]:
        src = SCRIPT_DIR / d
        if src.exists():
            cmd.extend(["--add-data", f"{src}:{d}"])

    cmd.append("desktop_app.py")
    run(cmd)

    app_path = DIST_DIR / f"{PROJECT_NAME}.app"
    if app_path.exists():
        print_success(f"打包完成: {app_path}")
    else:
        print_error("打包失败")


def build_linux():
    """Linux 打包"""
    print_step("开始 Linux 打包")

    cmd = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--name",
        PROJECT_NAME,
        "--onefile",
        "--noconfirm",
    ]

    for f in RESOURCES["files"]:
        src = SCRIPT_DIR / f
        if src.exists():
            cmd.extend(["--add-data", f"{src}:."])

    for d in RESOURCES["dirs"]:
        src = SCRIPT_DIR / d
        if src.exists():
            cmd.extend(["--add-data", f"{src}:{d}"])

    cmd.append("desktop_app.py")
    run(cmd)

    bin_path = DIST_DIR / PROJECT_NAME
    if bin_path.exists():
        print_success(f"打包完成: {bin_path}")
    else:
        print_error("打包失败")


# ═══════════════════════════════════════════════════════════════════════════════
# 主入口
# ═══════════════════════════════════════════════════════════════════════════════


def main():
    parser = argparse.ArgumentParser(description="MechForge AI 打包工具")
    parser.add_argument("--clean", action="store_true", help="清理构建目录")
    parser.add_argument("--deps", action="store_true", help="安装依赖")
    parser.add_argument(
        "--platform", choices=["win", "mac", "linux", "auto"], default="auto", help="目标平台"
    )
    parser.add_argument("--check", action="store_true", help="仅检查依赖")

    args = parser.parse_args()

    print(f"""
╔══════════════════════════════════════════════════╗
║         MechForge AI v{VERSION} 打包工具           ║
╚══════════════════════════════════════════════════╝
    """)

    # 安装依赖
    if args.deps:
        install_dependencies()

    # 检查依赖
    check_pyinstaller()

    if args.check:
        print_success("依赖检查通过")
        return

    # 清理
    if args.clean:
        clean()

    # 打包
    if args.platform == "auto":
        if sys.platform.startswith("win"):
            build_windows()
        elif sys.platform.startswith("darwin"):
            build_macos()
        else:
            build_linux()
    elif args.platform == "win":
        build_windows()
    elif args.platform == "mac":
        build_macos()
    elif args.platform == "linux":
        build_linux()

    print("\n🎉 打包完成!")


if __name__ == "__main__":
    main()
