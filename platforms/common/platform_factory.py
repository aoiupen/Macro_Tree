from typing import Dict, Type
from .platform_interface import IPlatform, IPlatformFactory, IPlatformConfig
from ..desktop.desktop_platform import DesktopPlatform, DesktopPlatformConfig
from ..web.web_platform import WebPlatform, WebPlatformConfig

class PlatformFactory(IPlatformFactory):
    """플랫폼별 구현을 생성하는 팩토리"""
    
    def __init__(self):
        self._platforms: Dict[str, Type[IPlatform]] = {
            "desktop": DesktopPlatform,
            "web": WebPlatform
        }
        self._configs: Dict[str, Type[IPlatformConfig]] = {
            "desktop": DesktopPlatformConfig,
            "web": WebPlatformConfig
        }
    
    def create_platform(self, platform_name: str) -> IPlatform:
        """플랫폼 인스턴스 생성"""
        if platform_name not in self._platforms:
            raise ValueError(f"Unknown platform: {platform_name}")
        
        platform_class = self._platforms[platform_name]
        config_class = self._configs[platform_name]
        config = config_class()
        
        return platform_class(config) 