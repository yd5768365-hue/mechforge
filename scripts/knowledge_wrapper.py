"""
MechForge Knowledge Wrapper - 负责设置路径并启动知识库程序
"""

import os
import sys
from pathlib import Path

# 设置环境变量
os.environ["PYTHONIOENCODING"] = "utf-8"

# 获取项目根目录
SCRIPT_DIR = Path(__file__).parent.resolve()

# 添加各包的 src 目录到 sys.path
for pkg in ["core", "theme", "ai", "knowledge", "work"]:
    src_path = SCRIPT_DIR / "packages" / pkg / "src"
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


def main():
    """知识库入口"""
    from mechforge_knowledge.cli import main as knowledge_main

    knowledge_main()


if __name__ == "__main__":
    main()
