#!/usr/bin/env python3
"""
MechForge AI PyWebView 桌面应用打包脚本
使用 PyInstaller 打包为独立可执行文件

用法:
    python build.py --clean     # 清理构建目录
    python build.py --build     # 构建可执行文件
    python build.py             # 清理 + 构建
"""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import List

# ═══════════════════════════════════════════════════════════════════════════════
# 路径配置
# ═══════════════════════════════════════════════════════════════════════════════

SCRIPT_DIR = Path(__file__).parent.resolve()
PROJECT_ROOT = SCRIPT_DIR.parent
DIST_DIR = SCRIPT_DIR / "dist"
BUILD_DIR = SCRIPT_DIR / "build"

# 需要打包的数据文件和目录
DATA_FILES: List[str] = [
    # HTML 和 CSS
    "index.html",
    "styles.css",
    "styles-modular.css",
    "experience.css",
    "dj-whale.png",
    # CSS 模块
    "css",
    # JavaScript 核心模块
    "core",
    # JavaScript 服务模块
    "services",
    # JavaScript 应用模块
    "app",
    # Experience Library
    "experience.js",
]


def clean() -> None:
    """清理构建目录"""
    print("🧹 清理构建目录...")
    
    for directory in [DIST_DIR, BUILD_DIR]:
        if directory.exists():
            shutil.rmtree(directory)
            print(f"   已删除: {directory}")
    
    # 清理 PyInstaller 临时文件
    for pattern in ["*.spec", "*.manifest"]:
        for f in SCRIPT_DIR.glob(pattern):
            f.unlink()
            print(f"   已删除: {f}")
    
    print("✅ 清理完成")


def build() -> bool:
    """构建可执行文件"""
    print("🔨 开始构建...")
    
    # 收集数据文件参数
    datas: List[str] = []
    for item in DATA_FILES:
        src = SCRIPT_DIR / item
        if not src.exists():
            print(f"⚠️  跳过不存在的文件: {src}")
            continue
        
        if src.is_dir():
            datas.append(f"--add-data={src};{item}")
        else:
            datas.append(f"--add-data={src};.")
    
    if not datas:
        print("❌ 错误: 没有找到任何数据文件")
        return False
    
    # PyInstaller 命令
    cmd: List[str] = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--onefile",
        "--windowed",
        "--name=MechForgeAI",
        "--icon=dj-whale.png",
        "--noconfirm",
        *datas,
        "desktop_app.py",
    ]
    
    print(f"📦 执行命令:")
    print(f"   {' '.join(cmd[:5])}...")
    print(f"   共 {len(datas)} 个数据文件")
    
    try:
        result = subprocess.run(cmd, cwd=SCRIPT_DIR, check=True)
        print(f"\n✅ 构建完成!")
        print(f"   输出目录: {DIST_DIR}")
        
        # 列出生成的文件
        if DIST_DIR.exists():
            print(f"   生成的文件:")
            for f in DIST_DIR.glob("*"):
                size_mb = f.stat().st_size / (1024 * 1024)
                print(f"   - {f.name} ({size_mb:.1f} MB)")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ 构建失败: {e}")
        return False
    except FileNotFoundError:
        print("❌ 错误: PyInstaller 未安装")
        print("   请运行: pip install pyinstaller")
        return False


def main() -> int:
    """主入口"""
    parser = argparse.ArgumentParser(
        description="MechForge AI 打包脚本",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
    python build.py --clean     # 清理构建目录
    python build.py --build     # 构建可执行文件
    python build.py             # 清理 + 构建
        """
    )
    parser.add_argument(
        "--clean",
        action="store_true",
        help="清理构建目录"
    )
    parser.add_argument(
        "--build",
        action="store_true",
        help="构建可执行文件"
    )
    
    args = parser.parse_args()
    
    # 如果没有指定任何参数，则执行清理 + 构建
    if not args.clean and not args.build:
        args.clean = True
        args.build = True
    
    success = True
    
    if args.clean:
        clean()
    
    if args.build:
        success = build()
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())