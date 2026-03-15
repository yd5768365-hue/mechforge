"""
MechForge GUI 应用入口
"""

import sys
from pathlib import Path

# 添加项目根目录到路径（支持直接运行）
if __name__ == "__main__":
    project_root = Path(__file__).parent.parent
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))

from PySide6.QtWidgets import QApplication

from mechforge_gui_ai.main_window import MainWindow


class MechForgeApp:
    """MechForge GUI 应用"""
    
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.app.setApplicationName("MechForge AI")
        self.app.setApplicationVersion("0.4.0")
        self.app.setOrganizationName("MechForge")
        
        # 设置 Fusion 风格
        from PySide6.QtWidgets import QStyleFactory
        self.app.setStyle(QStyleFactory.create("Fusion"))
        
        self.window = MainWindow()
    
    def run(self) -> int:
        """运行应用"""
        self.window.show()
        return self.app.exec()


def main():
    """CLI 入口"""
    app = MechForgeApp()
    sys.exit(app.run())


if __name__ == "__main__":
    main()