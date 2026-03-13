# -*- mode: python ; coding: utf-8 -*-
"""
MechForgeAI PyInstaller 打包配置
包含 llama-cpp-python 动态库支持
"""
import sys
from pathlib import Path
from PyInstaller.utils.hooks import collect_all, collect_dynamic_libs

# 项目路径
SCRIPT_DIR = Path(SPECPATH)
PROJECT_ROOT = SCRIPT_DIR.parent

# ═══════════════════════════════════════════════════════════════════════════════
# 数据文件
# ═══════════════════════════════════════════════════════════════════════════════

datas = []
binaries = []
hiddenimports = []

# 前端文件
frontend_files = [
    "index.html",
    "styles.css",
    "styles-modular.css",
    "dj-whale.png",
    "experience.js",
    "daily_feed_ui.js",
    "server.py",
    "config.py",
    "daily_agent.py",
    "config.yaml.example",
]
for f in frontend_files:
    src = SCRIPT_DIR / f
    if src.exists():
        datas.append((str(src), "."))

# 前端目录
frontend_dirs = ["css", "core", "services", "app", "api", "knowledge"]
for d in frontend_dirs:
    src = SCRIPT_DIR / d
    if src.exists():
        datas.append((str(src), d))

# ═══════════════════════════════════════════════════════════════════════════════
# 项目模块
# ═══════════════════════════════════════════════════════════════════════════════

project_modules = ["mechforge_core", "mechforge_ai", "mechforge_knowledge", "mechforge_theme"]
for mod in project_modules:
    src = PROJECT_ROOT / mod
    if src.exists():
        tmp_ret = collect_all(str(src))
        datas += tmp_ret[0]
        binaries += tmp_ret[1]
        hiddenimports += tmp_ret[2]

# ═══════════════════════════════════════════════════════════════════════════════
# llama-cpp-python 动态库
# ═══════════════════════════════════════════════════════════════════════════════

try:
    tmp_ret = collect_all("llama_cpp")
    datas += tmp_ret[0]
    binaries += tmp_ret[1]
    hiddenimports += tmp_ret[2]
    print(f"[INFO] 收集 llama-cpp-python: {len(tmp_ret[0])} 数据文件, {len(tmp_ret[1])} 二进制文件")
except Exception as e:
    print(f"[WARN] 无法收集 llama-cpp-python: {e}")

# 额外收集动态库
try:
    binaries += collect_dynamic_libs("llama_cpp")
except Exception as e:
    print(f"[WARN] 无法收集 llama-cpp-python 动态库: {e}")

# ═══════════════════════════════════════════════════════════════════════════════
# numpy（llama-cpp-python 依赖）
# ═══════════════════════════════════════════════════════════════════════════════

try:
    tmp_ret = collect_all("numpy")
    datas += tmp_ret[0]
    binaries += tmp_ret[1]
    hiddenimports += tmp_ret[2]
except Exception as e:
    print(f"[WARN] 无法收集 numpy: {e}")

# ═══════════════════════════════════════════════════════════════════════════════
# 隐藏导入
# ═══════════════════════════════════════════════════════════════════════════════

hiddenimports += [
    # FastAPI/Uvicorn
    "chromadb",
    "chromadb.api",
    "chromadb.config",
    "onnxruntime",
    "tokenizers",
    "tqdm",
    "fastapi",
    "uvicorn",
    "uvicorn.logging",
    "uvicorn.protocols",
    "uvicorn.protocols.http",
    "uvicorn.protocols.http.auto",
    "uvicorn.lifespan",
    "uvicorn.lifespan.on",
    "pydantic",
    "webview",
    # llama-cpp-python
    "llama_cpp",
    "llama_cpp.llama",
    "llama_cpp.llama_chat_format",
    "llama_cpp.llama_grammar",
    "llama_cpp.llama_types",
    "llama_cpp.llama_tokenizer",
    "llama_cpp.llama_cache",
    # numpy
    "numpy",
    "numpy.core",
    "numpy.core._multiarray_umath",
    # API 模块
    "api",
    "api.chat",
    "api.config",
    "api.rag",
    "api.health",
    "api.gguf",
    "api.state",
    "api.deps",
    "api.errors",
    "api.middleware",
    "api.database",
    "api.knowledge_engine",
]

# ═══════════════════════════════════════════════════════════════════════════════
# 分析
# ═══════════════════════════════════════════════════════════════════════════════

a = Analysis(
    ["desktop_app.py"],
    pathex=[str(PROJECT_ROOT), str(SCRIPT_DIR)],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[str(SCRIPT_DIR / "hooks")],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
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
    ],
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="MechForgeAI",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=["dj-whale.png"],
)