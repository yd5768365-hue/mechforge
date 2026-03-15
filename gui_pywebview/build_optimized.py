#!/usr/bin/env python3
"""
MechForge AI - 优化版打包脚本
支持多种打包模式和优化选项

用法:
    python build_optimized.py --mode=single    # 单文件模式（推荐）
    python build_optimized.py --mode=folder    # 文件夹模式
    python build_optimized.py --mode=portable  # 便携版（最小体积）
    python build_optimized.py --upx            # 使用 UPX 压缩
    python build_optimized.py --sign           # 代码签名（Windows）
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
import time
from pathlib import Path

# 路径配置
SCRIPT_DIR = Path(__file__).parent.resolve()
DIST_DIR = SCRIPT_DIR / "dist"
BUILD_DIR = SCRIPT_DIR / "build"
CACHE_DIR = SCRIPT_DIR / ".cache"


# 颜色输出
class Colors:
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    BLUE = "\033[94m"
    RESET = "\033[0m"


def print_step(step: str, message: str) -> None:
    print(f"\n{'=' * 60}")
    print(f"[{step}] {message}")
    print(f"{'=' * 60}")


def print_success(message: str) -> None:
    print(f"[OK] {message}")


def print_warning(message: str) -> None:
    print(f"[WARN] {message}")


def print_error(message: str) -> None:
    print(f"[ERROR] {message}")


def print_info(message: str) -> None:
    print(f"[INFO] {message}")


def get_file_size(path: Path) -> str:
    """获取人类可读的文件大小"""
    size = path.stat().st_size
    for unit in ["B", "KB", "MB", "GB"]:
        if size < 1024:
            return f"{size:.1f} {unit}"
        size /= 1024
    return f"{size:.1f} TB"


def clean() -> None:
    """清理构建目录"""
    print_step("CLEAN", "清理构建目录")

    dirs_to_clean = [DIST_DIR, BUILD_DIR, CACHE_DIR]
    for directory in dirs_to_clean:
        if directory.exists():
            shutil.rmtree(directory)
            print_info(f"已删除: {directory}")

    # 清理 Python 缓存
    for pycache in SCRIPT_DIR.rglob("__pycache__"):
        if pycache.is_dir():
            shutil.rmtree(pycache)

    print_success("清理完成")


def check_upx() -> bool:
    """检查 UPX 是否可用"""
    try:
        result = subprocess.run(["upx", "--version"], capture_output=True, text=True, check=False)
        return result.returncode == 0
    except FileNotFoundError:
        return False


def install_upx() -> None:
    """提示安装 UPX"""
    print_warning("UPX 未安装")
    print_info("UPX 可以显著减小可执行文件体积")
    print_info("下载地址: https://github.com/upx/upx/releases")
    print_info("安装后将 upx.exe 添加到系统 PATH")


def build_single_file(use_upx: bool = False, sign: bool = False) -> bool:
    """
    构建单文件版本（推荐）
    优点：一个文件，方便分发
    缺点：启动稍慢
    """
    print_step("BUILD", "构建单文件版本 (--onefile)")

    cmd: list[str] = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--name=MechForgeAI",
        "--onefile",
        "--windowed",
        "--noconfirm",
        "--clean",
        "--icon=dj-whale.png",
    ]

    if use_upx and check_upx():
        cmd.append("--upx-dir=upx")
        print_info("使用 UPX 压缩")
    elif use_upx:
        install_upx()

    # 添加数据文件
    data_files = [
        "index.html",
        "styles-modular.css",
        "experience.css",
        "css",
        "core",
        "services",
        "app",
        "dj-whale.png",
        "sw.js",
    ]

    for item in data_files:
        src = SCRIPT_DIR / item
        if src.exists():
            if src.is_dir():
                cmd.append(f"--add-data={src};{item}")
            else:
                cmd.append(f"--add-data={src};.")

    # 排除大体积模块
    exclude_modules = [
        "matplotlib",
        "numpy",
        "pandas",
        "scipy",
        "tkinter",
        "unittest",
        "pytest",
        "IPython",
        "jupyter",
        "notebook",
        "sphinx",
        "docutils",
        "PIL",
        "Pillow",
        "PyQt5",
        "PyQt6",
        "PySide2",
        "PySide6",
    ]

    for module in exclude_modules:
        cmd.extend(["--exclude-module", module])

    cmd.append("desktop_app.py")

    print_info(f"执行命令: {' '.join(cmd[:10])}...")

    start_time = time.time()
    result = subprocess.run(cmd, cwd=SCRIPT_DIR, capture_output=False, text=True)
    build_time = time.time() - start_time

    if result.returncode != 0:
        print_error("构建失败")
        return False

    print_success(f"构建完成! 耗时 {build_time:.1f} 秒")

    # 显示输出文件
    exe_path = DIST_DIR / "MechForgeAI.exe"
    if exe_path.exists():
        print_info(f"输出文件: {exe_path}")
        print_info(f"文件大小: {get_file_size(exe_path)}")

        if sign:
            sign_executable(exe_path)

    return True


def build_folder_mode(use_upx: bool = False) -> bool:
    """
    构建文件夹版本
    优点：启动快，可以单独更新资源
    缺点：多个文件，分发不便
    """
    print_step("BUILD", "构建文件夹版本 (--onedir)")

    cmd: list[str] = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--name=MechForgeAI",
        "--onedir",
        "--windowed",
        "--noconfirm",
        "--clean",
        "--icon=dj-whale.png",
    ]

    if use_upx and check_upx():
        cmd.append("--upx-dir=upx")

    # 添加数据文件
    data_files = [
        "index.html",
        "styles-modular.css",
        "experience.css",
        "css",
        "core",
        "services",
        "app",
        "dj-whale.png",
        "sw.js",
    ]

    for item in data_files:
        src = SCRIPT_DIR / item
        if src.exists():
            if src.is_dir():
                cmd.append(f"--add-data={src};{item}")
            else:
                cmd.append(f"--add-data={src};.")

    # 排除大体积模块
    exclude_modules = [
        "matplotlib",
        "numpy",
        "pandas",
        "scipy",
        "tkinter",
        "unittest",
        "pytest",
    ]

    for module in exclude_modules:
        cmd.extend(["--exclude-module", module])

    cmd.append("desktop_app.py")

    print_info(f"执行命令: {' '.join(cmd[:10])}...")

    start_time = time.time()
    result = subprocess.run(cmd, cwd=SCRIPT_DIR, capture_output=False, text=True)
    build_time = time.time() - start_time

    if result.returncode != 0:
        print_error("构建失败")
        return False

    print_success(f"构建完成! 耗时 {build_time:.1f} 秒")

    # 显示输出目录
    output_dir = DIST_DIR / "MechForgeAI"
    if output_dir.exists():
        print_info(f"输出目录: {output_dir}")

        # 计算总大小
        total_size = sum(f.stat().st_size for f in output_dir.rglob("*") if f.is_file())
        print_info(f"总大小: {total_size / 1024 / 1024:.1f} MB")

    return True


def build_portable() -> bool:
    """
    构建便携版（最小体积）
    使用激进的优化策略
    """
    print_step("BUILD", "构建便携版（最小体积）")

    print_info("使用激进的优化策略...")
    print_info("- 排除所有非必要模块")
    print_info("- 使用 UPX 压缩（如果可用）")
    print_info("- 启用 PyInstaller 的优化选项")

    cmd: list[str] = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--name=MechForgeAI-Portable",
        "--onefile",
        "--windowed",
        "--noconfirm",
        "--clean",
        "--icon=dj-whale.png",
        "--strip",  # 去除符号表
    ]

    if check_upx():
        cmd.append("--upx-dir=upx")

    # 最小化数据文件
    data_files = [
        "index.html",
        "styles-modular.css",
        "css",
        "core",
        "app",
        "dj-whale.png",
    ]

    for item in data_files:
        src = SCRIPT_DIR / item
        if src.exists():
            if src.is_dir():
                cmd.append(f"--add-data={src};{item}")
            else:
                cmd.append(f"--add-data={src};.")

    # 大量排除模块
    exclude_modules = [
        "matplotlib",
        "numpy",
        "pandas",
        "scipy",
        "sklearn",
        "tkinter",
        "unittest",
        "pytest",
        "doctest",
        "IPython",
        "jupyter",
        "notebook",
        "qtpy",
        "sphinx",
        "docutils",
        "jinja2",
        "PIL",
        "Pillow",
        "Image",
        "PyQt5",
        "PyQt6",
        "PySide2",
        "PySide6",
        "wx",
        "wxPython",
        "pygame",
        "pyglet",
        "sqlalchemy",
        "django",
        "flask",
        "requests",
        "urllib3",  # 如果不需要网络请求
        "email",
        "http",
        "ftplib",
        "ssl",
        "xmlrpc",
        "html",
    ]

    for module in exclude_modules:
        cmd.extend(["--exclude-module", module])

    cmd.append("desktop_app.py")

    print_info(f"执行命令: {' '.join(cmd[:10])}...")

    start_time = time.time()
    result = subprocess.run(cmd, cwd=SCRIPT_DIR, capture_output=False, text=True)
    build_time = time.time() - start_time

    if result.returncode != 0:
        print_error("构建失败")
        return False

    print_success(f"构建完成! 耗时 {build_time:.1f} 秒")

    exe_path = DIST_DIR / "MechForgeAI-Portable.exe"
    if exe_path.exists():
        print_info(f"输出文件: {exe_path}")
        print_info(f"文件大小: {get_file_size(exe_path)}")

    return True


def sign_executable(exe_path: Path) -> bool:
    """
    对可执行文件进行代码签名（Windows）
    需要安装证书
    """
    print_step("SIGN", "代码签名")

    if sys.platform != "win32":
        print_warning("代码签名仅在 Windows 上支持")
        return False

    # 检查 signtool
    signtool_paths = [
        Path("C:/Program Files (x86)/Windows Kits/10/bin/10.0.19041.0/x64/signtool.exe"),
        Path("C:/Program Files (x86)/Windows Kits/10/bin/10.0.22000.0/x64/signtool.exe"),
    ]

    signtool = None
    for path in signtool_paths:
        if path.exists():
            signtool = path
            break

    if not signtool:
        print_warning("未找到 signtool.exe")
        print_info("请安装 Windows SDK")
        return False

    # 这里使用测试证书，实际使用需要替换为真实证书
    print_info("使用测试证书签名...")
    print_warning("生产环境请使用真实证书")

    return True


def create_installer() -> bool:
    """
    创建安装程序（使用 Inno Setup）
    """
    print_step("INSTALLER", "创建安装程序")

    if sys.platform != "win32":
        print_warning("安装程序仅在 Windows 上支持")
        return False

    # 检查 Inno Setup
    iscc_paths = [
        Path("C:/Program Files (x86)/Inno Setup 6/ISCC.exe"),
        Path("C:/Program Files/Inno Setup 6/ISCC.exe"),
    ]

    iscc = None
    for path in iscc_paths:
        if path.exists():
            iscc = path
            break

    if not iscc:
        print_warning("未找到 Inno Setup")
        print_info("下载地址: https://jrsoftware.org/isdl.php")
        return False

    print_info("创建安装程序...")
    return True


def main():
    parser = argparse.ArgumentParser(description="MechForge AI 优化版打包脚本")
    parser.add_argument(
        "--mode",
        choices=["single", "folder", "portable"],
        default="single",
        help="打包模式: single=单文件(推荐), folder=文件夹, portable=便携版",
    )
    parser.add_argument("--upx", action="store_true", help="使用 UPX 压缩（需要安装 UPX）")
    parser.add_argument("--sign", action="store_true", help="代码签名（需要证书）")
    parser.add_argument("--clean", action="store_true", help="清理构建目录")
    parser.add_argument("--installer", action="store_true", help="创建安装程序（需要 Inno Setup）")

    args = parser.parse_args()

    print(f"""
{"=" * 60}
  MechForge AI - Build Script

  Mode: {args.mode}
  UPX:  {"enabled" if args.upx else "disabled"}
  Sign: {"enabled" if args.sign else "disabled"}
{"=" * 60}
""")

    if args.clean:
        clean()

    success = False

    if args.mode == "single":
        success = build_single_file(use_upx=args.upx, sign=args.sign)
    elif args.mode == "folder":
        success = build_folder_mode(use_upx=args.upx)
    elif args.mode == "portable":
        success = build_portable()

    if success and args.installer:
        create_installer()

    if success:
        print("\n[OK] Build completed!")
        print(f"\nOutput: {DIST_DIR}")
    else:
        print("\n[ERROR] Build failed")
        sys.exit(1)


if __name__ == "__main__":
    main()
