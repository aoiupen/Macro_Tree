from PyQt6.QtWidgets import QMainWindow
from typing import Dict, Any
from ..common.platform_interface import IPlatform, IPlatformConfig

class DesktopPlatformConfig(IPlatformConfig):
    def get_platform_name(self) -> str:
        return "desktop"
    
    def get_platform_version(self) -> str:
        return "1.0.0"
    
    def get_platform_settings(self) -> Dict[str, Any]:
        return {
            "window_title": "Macro Tree",
            "window_width": 800,
            "window_height": 600
        }

class DesktopPlatform(IPlatform):
    def __init__(self, config: DesktopPlatformConfig):
        self.config = config
        self.window = None
    
    def initialize(self) -> None:
        """PyQt 초기화"""
        from PyQt6.QtWidgets import QApplication
        self.app = QApplication([])
    
    def create_window(self, title: str) -> QMainWindow:
        """PyQt 윈도우 생성"""
        from PyQt6.QtWidgets import QMainWindow
        self.window = QMainWindow()
        self.window.setWindowTitle(title)
        return self.window
    
    def run(self) -> None:
        """PyQt 앱 실행"""
        if self.window:
            self.window.show()
        self.app.exec() 