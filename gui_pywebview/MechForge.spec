# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['mechforge_gui_ai\\app.py'],
    pathex=[],
    binaries=[],
    datas=[('mechforge_core', 'mechforge_core'), ('mechforge_ai', 'mechforge_ai'), ('mechforge_theme', 'mechforge_theme'), ('mechforge_gui_ai', 'mechforge_gui_ai')],
    hiddenimports=['PySide6', 'PySide6.QtCore', 'PySide6.QtGui', 'PySide6.QtWidgets', 'rich', 'pydantic', 'requests', 'httpx'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['torch', 'transformers', 'sklearn', 'pandas', 'numpy', 'matplotlib', 'PIL', 'scipy', 'tkinter', 'PyQt5', 'PyQt6', 'PySide2', 'chromadb', 'sentence_transformers', 'llama_cpp'],
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
    name='MechForge',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
