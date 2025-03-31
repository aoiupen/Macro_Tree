"""플랫폼 인터페이스 모듈

플랫폼 관련 인터페이스를 정의합니다.
"""
from typing import Protocol, Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum

class PlatformType(Enum):
    """플랫폼 타입 열거형"""
    DESKTOP = "desktop"
    WEB = "web"
    MOBILE = "mobile"

@dataclass
class PlatformConfig:
    """플랫폼 설정 데이터 클래스"""
    platform_type: PlatformType
    theme: str
    language: str
    debug_mode: bool = False

class IPlatform(Protocol):
    """플랫폼 인터페이스"""
    
    @property
    def config(self) -> PlatformConfig:
        """플랫폼 설정을 반환합니다."""
        ...
    
    def initialize(self) -> bool:
        """플랫폼을 초기화합니다."""
        ...
    
    def start(self) -> None:
        """플랫폼을 시작합니다."""
        ...
    
    def stop(self) -> None:
        """플랫폼을 중지합니다."""
        ...
    
    def get_platform_info(self) -> Dict[str, Any]:
        """플랫폼 정보를 반환합니다."""
        ...

class IPlatformFactory(Protocol):
    """플랫폼 팩토리 인터페이스"""
    
    def create_platform(self, config: PlatformConfig) -> IPlatform:
        """플랫폼 인스턴스를 생성합니다."""
        ...
    
    def register_platform(self, platform_type: PlatformType, platform_class: type) -> None:
        """플랫폼 클래스를 등록합니다."""
        ... 