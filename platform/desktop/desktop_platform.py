"""데스크톱 플랫폼 구현 모듈

PyQt6를 기반으로 한 데스크톱 플랫폼 구현을 제공합니다.
"""
from typing import Dict, Any
from PyQt6.QtWidgets import QMainWindow, QApplication
from dataclasses import dataclass
from platform.interfaces.platform_interface import IPlatform, PlatformConfig, PlatformType


@dataclass
class DesktopPlatformConfig(PlatformConfig):
    """데스크톱 플랫폼 설정"""
    window_width: int = 800
    window_height: int = 600
    window_title: str = "Macro Tree"
    
    def __post_init__(self):
        if not hasattr(self, 'platform_type'):
            self.platform_type = PlatformType.DESKTOP


class DesktopPlatform(IPlatform):
    """데스크톱 플랫폼 구현"""
    
    def __init__(self, config: DesktopPlatformConfig):
        """DesktopPlatform 생성자
        
        Args:
            config: 플랫폼 설정
        """
        self._config = config
        self._app = None
        self._window = None
    
    @property
    def config(self) -> PlatformConfig:
        """플랫폼 설정을 반환합니다."""
        return self._config
    
    def initialize(self) -> bool:
        """플랫폼을 초기화합니다.
        
        Returns:
            초기화 성공 여부
        """
        try:
            self._app = QApplication([])
            self._window = QMainWindow()
            self._window.setWindowTitle(self._config.window_title)
            self._window.resize(self._config.window_width, self._config.window_height)
            return True
        except Exception as e:
            print(f"데스크톱 플랫폼 초기화 오류: {e}")
            return False
    
    def start(self) -> None:
        """플랫폼을 시작합니다."""
        if self._window:
            self._window.show()
        if self._app:
            self._app.exec()
    
    def stop(self) -> None:
        """플랫폼을 중지합니다."""
        if self._app:
            self._app.quit()
    
    def get_platform_info(self) -> Dict[str, Any]:
        """플랫폼 정보를 반환합니다."""
        from platform import system, release, version
        return {
            "platform": "desktop",
            "os": system(),
            "os_release": release(),
            "os_version": version(),
            "qt_version": QApplication.instance().applicationVersion()
        } 