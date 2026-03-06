#!/usr/bin/env python
import os
import sys
from pathlib import Path

# 设置环境变量
os.environ["PYTHONIOENCODING"] = "utf-8"

# 强制 UTF-8 输出（Windows）
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

# 获取脚本所在目录
if getattr(sys, "frozen", False):
    # PyInstaller 打包后的可执行文件
    script_dir = Path(sys._MEIPASS)
else:
    script_dir = Path(__file__).parent.resolve()

BASE_DIR = Path.home() / ".mechforge"

# 创建必要的目录
(BASE_DIR / "history").mkdir(parents=True, exist_ok=True)

# 添加各包的 src 目录到 sys.path
for pkg in ["core", "theme", "ai", "knowledge", "work"]:
    src_path = script_dir / "packages" / pkg / "src"
    if src_path.exists():
        sys.path.insert(0, str(src_path))

# 设置 UTF-8 输出
if sys.platform == "win32" and hasattr(sys.stdout, "buffer"):
    import io

    try:
        if not isinstance(sys.stdout, io.TextIOWrapper):
            sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
        if not isinstance(sys.stderr, io.TextIOWrapper):
            sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")
    except Exception:
        pass

# 运行工作台
from mechforge_work.work_cli import main

main()
