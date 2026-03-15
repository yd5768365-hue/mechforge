#!/usr/bin/env python3
"""
项目初始化脚本
设置开发环境
"""

import subprocess
import sys
from pathlib import Path


def print_step(step: str, message: str) -> None:
    """打印步骤"""
    print(f"\n{'=' * 60}")
    print(f"[{step}] {message}")
    print("=" * 60)


def run_command(cmd: list, cwd: Path = None) -> bool:
    """运行命令"""
    try:
        result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, check=True)
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")
        if e.stderr:
            print(e.stderr)
        return False


def check_python_version() -> bool:
    """检查 Python 版本"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 10):
        print(f"❌ Python 3.10+ required, found {version.major}.{version.minor}")
        return False
    print(f"✅ Python {version.major}.{version.minor}.{version.micro}")
    return True


def install_python_deps() -> bool:
    """安装 Python 依赖"""
    print_step("Python", "Installing dependencies")

    requirements = Path(__file__).parent.parent / "requirements.txt"
    if not requirements.exists():
        print("❌ requirements.txt not found")
        return False

    return run_command([sys.executable, "-m", "pip", "install", "-r", str(requirements)])


def install_dev_deps() -> bool:
    """安装开发依赖"""
    print_step("Python", "Installing dev dependencies")

    requirements = Path(__file__).parent.parent / "requirements-dev.txt"
    if not requirements.exists():
        print("⚠️ requirements-dev.txt not found, skipping")
        return True

    return run_command([sys.executable, "-m", "pip", "install", "-r", str(requirements)])


def setup_node() -> bool:
    """设置 Node.js"""
    print_step("Node.js", "Checking Node.js")

    try:
        result = subprocess.run(["node", "--version"], capture_output=True, text=True, check=True)
        print(f"✅ Node.js {result.stdout.strip()}")
    except FileNotFoundError:
        print("❌ Node.js not found, please install Node.js 18+")
        return False

    # 安装 npm 依赖
    print_step("Node.js", "Installing dependencies")
    package_json = Path(__file__).parent.parent / "package.json"
    if package_json.exists():
        return run_command(["npm", "install"], cwd=package_json.parent)

    return True


def create_directories() -> None:
    """创建必要的目录"""
    print_step("Setup", "Creating directories")

    root = Path(__file__).parent.parent
    dirs = [root / "dist", root / "build", root / ".cache", root / "logs", root / "temp"]

    for d in dirs:
        d.mkdir(exist_ok=True)
        print(f"  📁 {d.name}")


def setup_git_hooks() -> bool:
    """设置 Git hooks"""
    print_step("Git", "Setting up hooks")

    git_dir = Path(__file__).parent.parent / ".git"
    if not git_dir.exists():
        print("⚠️ Not a git repository, skipping")
        return True

    hooks_dir = git_dir / "hooks"
    pre_commit = hooks_dir / "pre-commit"

    # 创建 pre-commit hook
    hook_content = """#!/bin/sh
# Run linting before commit
echo "Running pre-commit checks..."

# Python linting
echo "Checking Python code..."
python -m ruff check . || exit 1
python -m black --check . || exit 1

# JavaScript linting
echo "Checking JavaScript code..."
npm run lint || exit 1

echo "All checks passed!"
"""

    pre_commit.write_text(hook_content)
    pre_commit.chmod(0o755)

    print("✅ Pre-commit hook installed")
    return True


def setup_vscode() -> bool:
    """设置 VS Code"""
    print_step("VS Code", "Setting up configuration")

    vscode_dir = Path(__file__).parent.parent / ".vscode"
    if not vscode_dir.exists():
        print("⚠️ .vscode directory not found, skipping")
        return True

    print("✅ VS Code configuration ready")
    return True


def print_success() -> None:
    """打印成功信息"""
    print("""
╔══════════════════════════════════════════════════╗
║           Setup Complete! 🎉                     ║
╠══════════════════════════════════════════════════╣
║                                                  ║
║  Quick Start:                                    ║
║                                                  ║
║  1. Run development server:                      ║
║     python desktop_app.py                        ║
║                                                  ║
║  2. Or with debug mode:                          ║
║     python desktop_app.py --debug                ║
║                                                  ║
║  3. Run tests:                                   ║
║     npm test                                     ║
║                                                  ║
║  4. Build executable:                            ║
║     python build.py                              ║
║                                                  ║
╚══════════════════════════════════════════════════╝
""")


def main() -> int:
    """主函数"""
    print("""
╔══════════════════════════════════════════════════╗
║       MechForge AI - Project Setup               ║
╚══════════════════════════════════════════════════╝
""")

    # 检查 Python 版本
    if not check_python_version():
        return 1

    # 安装依赖
    if not install_python_deps():
        return 1

    if not install_dev_deps():
        return 1

    # 设置 Node.js
    if not setup_node():
        return 1

    # 创建目录
    create_directories()

    # 设置 Git hooks
    setup_git_hooks()

    # 设置 VS Code
    setup_vscode()

    # 打印成功信息
    print_success()

    return 0


if __name__ == "__main__":
    sys.exit(main())
