# 前端打包配置 - 打包为静态文件夹
import shutil
from pathlib import Path

# 源目录
SRC_DIR = Path("D:/mechforge_ai/gui_pywebview")
DIST_DIR = SRC_DIR / "dist_frontend"

# 需要复制的文件
FILES = [
    "index.html",
    "dj-whale.png",
    "experience.js",
]

# 需要复制的目录
DIRS = [
    "css",
    "app",
    "core",
    "services",
    "api",
]


def build():
    # 清理旧目录
    if DIST_DIR.exists():
        shutil.rmtree(DIST_DIR)
    DIST_DIR.mkdir(parents=True)

    # 复制文件
    for f in FILES:
        src = SRC_DIR / f
        if src.exists():
            shutil.copy2(src, DIST_DIR / f)
            print(f"复制: {f}")

    # 复制目录
    for d in DIRS:
        src = SRC_DIR / d
        if src.exists() and src.is_dir():
            dst = DIST_DIR / d
            shutil.copytree(src, dst)
            print(f"复制目录: {d}")

    print(f"\n前端打包完成: {DIST_DIR}")
    print("使用方式:")
    print("1. 启动后端: dist/MechForgeBackend.exe")
    print("2. 打开浏览器访问: http://127.0.0.1:5000")


if __name__ == "__main__":
    build()
