"""
MechForge AI GUI 测试配置
"""

import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
PROJECT_ROOT = Path(__file__).parent.parent.parent
GUI_DIR = Path(__file__).parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

if str(GUI_DIR) not in sys.path:
    sys.path.insert(0, str(GUI_DIR))