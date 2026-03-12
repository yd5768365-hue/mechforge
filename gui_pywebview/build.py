#!/usr/bin/env python3
"""
MechForge AI PyWebView 桌面应用打包脚本
使用 PyInstaller 打包为独立可执行文件

用法:
    python build.py --clean     # 清理构建目录
    python build.py --build     # 构建可执行文件
    python build.py --dev       # 开发模式（不打包，只检查）
    python build.py --optimize  # 优化资源后构建
    python build.py             # 清理 + 构建
"""

from __future__ import annotations

import argparse
import io
import shutil
import subprocess
import sys
import time
from pathlib import Path

# Windows 控制台 UTF-8 编码（避免 emoji 输出错误）
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

# ═══════════════════════════════════════════════════════════════════════════════
# 路径配置
# ═══════════════════════════════════════════════════════════════════════════════

SCRIPT_DIR = Path(__file__).parent.resolve()
PROJECT_ROOT = SCRIPT_DIR.parent.resolve()
DIST_DIR = SCRIPT_DIR / "dist"
BUILD_DIR = SCRIPT_DIR / "build"
CACHE_DIR = SCRIPT_DIR / ".cache"

# 需要打包的数据文件和目录
DATA_FILES: list[str] = [
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
    # Daily Feed UI
    "daily_feed_ui.js",
]

# 父项目模块（api/deps 等会导入）
PROJECT_MODULES = ["mechforge_core", "mechforge_ai", "mechforge_knowledge", "mechforge_theme"]

# 需要排除的文件模式
EXCLUDE_PATTERNS = [
    "__pycache__",
    "*.pyc",
    "*.pyo",
    "*.pyd",
    ".git",
    ".gitignore",
    ".vscode",
    "*.md",
    "tests",
    "*.test.js",
    "*.spec.js",
]

# ═══════════════════════════════════════════════════════════════════════════════
# 工具函数
# ═══════════════════════════════════════════════════════════════════════════════


def print_step(step: str, message: str) -> None:
    """打印步骤信息"""
    print(f"\n{'=' * 60}")
    print(f"[{step}] {message}")
    print("=" * 60)


def print_success(message: str) -> None:
    """打印成功信息"""
    print(f"✅ {message}")


def print_warning(message: str) -> None:
    """打印警告信息"""
    print(f"⚠️  {message}")


def print_error(message: str) -> None:
    """打印错误信息"""
    print(f"❌ {message}")


def print_info(message: str) -> None:
    """打印信息"""
    print(f"ℹ️  {message}")


def get_file_size(path: Path) -> str:
    """获取文件大小（人类可读）"""
    size = path.stat().st_size
    for unit in ["B", "KB", "MB", "GB"]:
        if size < 1024:
            return f"{size:.1f} {unit}"
        size /= 1024
    return f"{size:.1f} TB"


def run_command(
    cmd: list[str], cwd: Path | None = None, check: bool = True
) -> tuple[int, str, str]:
    """运行命令并返回结果"""
    try:
        result = subprocess.run(
            cmd,
            cwd=cwd or SCRIPT_DIR,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="ignore",
        )
        if check and result.returncode != 0:
            print_error(f"Command failed: {' '.join(cmd)}")
            print_error(f"stdout: {result.stdout}")
            print_error(f"stderr: {result.stderr}")
        return result.returncode, result.stdout, result.stderr
    except Exception as e:
        print_error(f"Failed to run command: {e}")
        return -1, "", str(e)


# ═══════════════════════════════════════════════════════════════════════════════
# 清理功能
# ═══════════════════════════════════════════════════════════════════════════════


def clean() -> None:
    """清理构建目录"""
    print_step("CLEAN", "清理构建目录")

    directories = [DIST_DIR, BUILD_DIR, CACHE_DIR]
    cleaned = []

    for directory in directories:
        if directory.exists():
            shutil.rmtree(directory)
            cleaned.append(str(directory))
            print_info(f"已删除: {directory}")

    # 清理 PyInstaller 临时文件
    for pattern in ["*.spec", "*.manifest", "*.log"]:
        for f in SCRIPT_DIR.glob(pattern):
            f.unlink()
            cleaned.append(str(f))
            print_info(f"已删除: {f}")

    # 清理 Python 缓存
    for pycache in SCRIPT_DIR.rglob("__pycache__"):
        if pycache.is_dir():
            shutil.rmtree(pycache)
            print_info(f"已删除: {pycache}")

    if cleaned:
        print_success(f"清理完成，共删除 {len(cleaned)} 个项目")
    else:
        print_info("无需清理")


# ═══════════════════════════════════════════════════════════════════════════════
# 优化功能
# ═══════════════════════════════════════════════════════════════════════════════


def optimize_js() -> dict[str, int]:
    """优化 JavaScript 文件"""
    print_step("OPTIMIZE", "优化 JavaScript 文件")

    stats = {"optimized": 0, "saved": 0}

    # 检查是否有 terser
    returncode, _, _ = run_command(["npx", "terser", "--version"], check=False)
    if returncode != 0:
        print_warning("terser 未安装，跳过 JS 优化")
        return stats

    js_files = list(SCRIPT_DIR.rglob("*.js"))
    for js_file in js_files:
        if "node_modules" in str(js_file):
            continue

        # 创建优化后的文件
        output_file = CACHE_DIR / "optimized" / js_file.relative_to(SCRIPT_DIR)
        output_file.parent.mkdir(parents=True, exist_ok=True)

        returncode, stdout, stderr = run_command(
            ["npx", "terser", str(js_file), "--compress", "--mangle", "--output", str(output_file)],
            check=False,
        )

        if returncode == 0:
            original_size = js_file.stat().st_size
            optimized_size = output_file.stat().st_size
            saved = original_size - optimized_size
            stats["optimized"] += 1
            stats["saved"] += saved
            print_info(
                f"优化 {js_file.name}: {original_size} -> {optimized_size} bytes (节省 {saved} bytes)"
            )

    print_success(f"JS 优化完成: {stats['optimized']} 个文件，共节省 {stats['saved']} bytes")
    return stats


def optimize_css() -> dict[str, int]:
    """优化 CSS 文件"""
    print_step("OPTIMIZE", "优化 CSS 文件")

    stats = {"optimized": 0, "saved": 0}

    # 检查是否有 clean-css-cli
    returncode, _, _ = run_command(["npx", "cleancss", "--version"], check=False)
    if returncode != 0:
        print_warning("clean-css-cli 未安装，跳过 CSS 优化")
        return stats

    css_files = list(SCRIPT_DIR.rglob("*.css"))
    for css_file in css_files:
        if "node_modules" in str(css_file):
            continue

        output_file = CACHE_DIR / "optimized" / css_file.relative_to(SCRIPT_DIR)
        output_file.parent.mkdir(parents=True, exist_ok=True)

        returncode, stdout, stderr = run_command(
            ["npx", "cleancss", "-o", str(output_file), str(css_file)], check=False
        )

        if returncode == 0:
            original_size = css_file.stat().st_size
            optimized_size = output_file.stat().st_size
            saved = original_size - optimized_size
            stats["optimized"] += 1
            stats["saved"] += saved
            print_info(
                f"优化 {css_file.name}: {original_size} -> {optimized_size} bytes (节省 {saved} bytes)"
            )

    print_success(f"CSS 优化完成: {stats['optimized']} 个文件，共节省 {stats['saved']} bytes")
    return stats


def optimize_images() -> dict[str, int]:
    """优化图片文件"""
    print_step("OPTIMIZE", "优化图片文件")

    stats = {"optimized": 0, "saved": 0}

    # 检查图片文件
    image_extensions = {".png", ".jpg", ".jpeg", ".gif", ".svg"}
    image_files = [f for f in SCRIPT_DIR.rglob("*") if f.suffix.lower() in image_extensions]

    for img_file in image_files:
        print_info(f"发现图片: {img_file.name} ({get_file_size(img_file)})")
        stats["optimized"] += 1

    print_info("图片优化需要安装额外工具，跳过")
    return stats


def optimize_resources() -> bool:
    """优化所有资源"""
    print_step("OPTIMIZE", "优化资源文件")

    CACHE_DIR.mkdir(exist_ok=True)

    js_stats = optimize_js()
    css_stats = optimize_css()
    img_stats = optimize_images()

    total_saved = js_stats.get("saved", 0) + css_stats.get("saved", 0)
    total_files = (
        js_stats.get("optimized", 0) + css_stats.get("optimized", 0) + img_stats.get("optimized", 0)
    )

    print_success(f"资源优化完成: {total_files} 个文件，共节省 {total_saved} bytes")
    return True


# ═══════════════════════════════════════════════════════════════════════════════
# 构建功能
# ═══════════════════════════════════════════════════════════════════════════════


def check_dependencies() -> bool:
    """检查依赖"""
    print_step("CHECK", "检查依赖")

    # 检查 Python 依赖（导入即验证可用性）
    try:
        import fastapi  # noqa: F401
        import pydantic  # noqa: F401
        import uvicorn  # noqa: F401
        import webview  # noqa: F401

        print_success("Python 依赖检查通过")
    except ImportError as e:
        print_error(f"缺少 Python 依赖: {e}")
        print_info("请运行: pip install -r requirements.txt")
        return False

    # 检查 PyInstaller
    returncode, _, _ = run_command([sys.executable, "-m", "PyInstaller", "--version"], check=False)
    if returncode != 0:
        print_warning("PyInstaller 未安装")
        print_info("请运行: pip install pyinstaller")
        return False

    print_success("PyInstaller 检查通过")
    return True


def collect_data_files(use_optimized: bool = False) -> list[str]:
    """收集数据文件参数"""
    datas: list[str] = []
    source_dir = CACHE_DIR / "optimized" if use_optimized else SCRIPT_DIR

    for item in DATA_FILES:
        src = source_dir / item if use_optimized else SCRIPT_DIR / item
        if not src.exists():
            src = SCRIPT_DIR / item  # 回退到原始文件

        if not src.exists():
            print_warning(f"跳过不存在的文件: {src}")
            continue

        if src.is_dir():
            datas.append(f"--add-data={src};{item}")
        else:
            datas.append(f"--add-data={src};.")

    return datas


def build(onefile: bool = True, windowed: bool = True, optimize: bool = False) -> bool:
    """构建可执行文件"""
    print_step("BUILD", "构建可执行文件")

    if not check_dependencies():
        return False

    # 收集数据文件
    datas = collect_data_files(use_optimized=optimize)

    if not datas:
        print_error("错误: 没有找到任何数据文件")
        return False

    # PyInstaller 命令
    cmd: list[str] = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--name=MechForgeAI",
        "--icon=dj-whale.png",
        "--noconfirm",
    ]

    if onefile:
        cmd.append("--onefile")
    else:
        cmd.append("--onedir")

    if windowed:
        cmd.append("--windowed")

    # 添加项目根路径，使 PyInstaller 能解析 mechforge_core 等
    cmd.extend(["--paths", str(PROJECT_ROOT)])

    # 添加父项目模块（mechforge_core, mechforge_ai 等）
    for mod in PROJECT_MODULES:
        src = PROJECT_ROOT / mod
        if src.exists() and src.is_dir():
            cmd.extend(["--collect-all", str(src)])
            print_info(f"添加项目模块: {mod}")

    # 添加排除项
    for pattern in EXCLUDE_PATTERNS:
        cmd.extend(["--exclude-module", pattern])

    # 添加数据文件
    cmd.extend(datas)

    # 添加入口文件
    cmd.append("desktop_app.py")

    print_info(f"执行命令: {' '.join(cmd[:5])}...")
    print_info(f"共 {len(datas)} 个数据文件")

    start_time = time.time()
    returncode, stdout, stderr = run_command(cmd, check=False)
    build_time = time.time() - start_time

    if returncode != 0:
        print_error(f"构建失败:\n{stderr}")
        return False

    print_success(f"构建完成! 耗时 {build_time:.1f} 秒")

    # 显示输出文件
    if DIST_DIR.exists():
        print_step("OUTPUT", "生成的文件")
        for f in DIST_DIR.glob("*"):
            if f.is_file():
                print_info(f"  {f.name} ({get_file_size(f)})")

    return True


# ═══════════════════════════════════════════════════════════════════════════════
# 开发功能
# ═══════════════════════════════════════════════════════════════════════════════


def dev_mode() -> bool:
    """开发模式 - 运行应用但不打包"""
    print_step("DEV", "开发模式")

    print_info("启动开发服务器...")
    print_info("按 Ctrl+C 停止")

    try:
        subprocess.run([sys.executable, "desktop_app.py", "--debug"], cwd=SCRIPT_DIR, check=True)
    except KeyboardInterrupt:
        print_info("\n开发服务器已停止")
    except Exception as e:
        print_error(f"开发模式失败: {e}")
        return False

    return True


def run_tests() -> bool:
    """运行测试"""
    print_step("TEST", "运行测试")

    # 检查 pytest
    returncode, _, _ = run_command([sys.executable, "-m", "pytest", "--version"], check=False)
    if returncode != 0:
        print_warning("pytest 未安装，跳过测试")
        return True

    returncode, stdout, stderr = run_command([sys.executable, "-m", "pytest", "-v"], check=False)

    if returncode == 0:
        print_success("测试通过")
        return True
    else:
        print_error("测试失败")
        print(stderr)
        return False


# ═══════════════════════════════════════════════════════════════════════════════
# 主入口
# ═══════════════════════════════════════════════════════════════════════════════


def main() -> int:
    """主入口"""
    parser = argparse.ArgumentParser(
        description="MechForge AI 打包脚本",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
    python build.py --clean           # 清理构建目录
    python build.py --build           # 构建可执行文件
    python build.py --dev             # 开发模式
    python build.py --optimize        # 优化资源后构建
    python build.py --test            # 运行测试
    python build.py                   # 清理 + 构建
        """,
    )
    parser.add_argument("--clean", action="store_true", help="清理构建目录")
    parser.add_argument("--build", action="store_true", help="构建可执行文件")
    parser.add_argument("--dev", action="store_true", help="开发模式")
    parser.add_argument("--optimize", action="store_true", help="优化资源后构建")
    parser.add_argument("--test", action="store_true", help="运行测试")
    parser.add_argument("--onedir", action="store_true", help="构建为目录（而非单文件）")
    parser.add_argument("--console", action="store_true", help="保留控制台窗口")

    args = parser.parse_args()

    # 如果没有指定任何参数，则执行清理 + 构建
    if not any([args.clean, args.build, args.dev, args.optimize, args.test]):
        args.clean = True
        args.build = True

    success = True

    if args.clean:
        clean()

    if args.optimize:
        optimize_resources()

    if args.test:
        success = run_tests() and success

    if args.build:
        success = (
            build(onefile=not args.onedir, windowed=not args.console, optimize=args.optimize)
            and success
        )

    if args.dev:
        success = dev_mode() and success

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
