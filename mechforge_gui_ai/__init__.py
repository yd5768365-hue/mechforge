"""
MechForge GUI - PySide6 桌面应用

终端风格的桌面 GUI，功能与 mechforge-ai 一致
"""

__version__ = "0.1.0"

from mechforge_gui_ai.main_window import MainWindow
from mechforge_gui_ai.app import MechForgeApp

__all__ = ["MainWindow", "MechForgeApp"]