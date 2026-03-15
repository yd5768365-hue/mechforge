# -*- mode: python ; coding: utf-8 -*-
"""
MechForge GUI PyInstaller Spec 文件

使用方法:
    pyinstaller mechforge_gui.spec
"""

import sys
from pathlib import Path

# 项目根目录
project_root = Path(SPECPATH)

# 分析入口
a = Analysis(
    ["mechforge_gui/app.py"],
    pathex=[str(project_root)],
    binaries=[],
    datas=[
        ("mechforge_core", "mechforge_core"),
        ("mechforge_ai", "mechforge_ai"),
        ("mechforge_theme", "mechforge_theme"),
        ("mechforge_gui", "mechforge_gui"),
        ("mechforge_knowledge", "mechforge_knowledge"),
        ("config.yaml", "."),
    ],
    hiddenimports=[
        "PySide6",
        "PySide6.QtCore",
        "PySide6.QtGui",
        "PySide6.QtWidgets",
        "rich",
        "rich.console",
        "rich.panel",
        "rich.table",
        "rich.text",
        "pydantic",
        "pydantic_settings",
        "requests",
        "httpx",
        "chromadb",
        "sentence_transformers",
        "rank_bm25",
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        "tkinter",
        "matplotlib",
        "PIL",
        "scipy",
        "numpy.f2py",
        "IPython",
        "jupyter",
        "notebook",
    ],
    noarchive=False,
)

# PYZ 压缩包
pyz = PYZ(a.pure, a.zipped_data)

# EXE 可执行文件
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="MechForge",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,  # 使用 UPX 压缩
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # 无控制台窗口
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    # icon="assets/icon.ico",  # 图标文件
)