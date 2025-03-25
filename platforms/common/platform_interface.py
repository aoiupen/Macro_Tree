from abc import ABC, abstractmethod
from typing import Protocol, Dict, Any

class IPlatform(ABC):
    """플랫폼별 구현을 위한 기본 인터페이스"""
    
    @abstractmethod
    def initialize(self) -> None:
        """플랫폼 초기화"""
        pass
    
    @abstractmethod
    def create_window(self, title: str) -> Any:
        """플랫폼별 윈도우 생성"""
        pass
    
    @abstractmethod
    def run(self) -> None:
        """플랫폼별 앱 실행"""
        pass

class IPlatformFactory(ABC):
    """플랫폼별 구현을 생성하는 팩토리"""
    
    @abstractmethod
    def create_platform(self) -> IPlatform:
        """플랫폼 인스턴스 생성"""
        pass

class IPlatformConfig(Protocol):
    """플랫폼별 설정을 위한 프로토콜"""
    
    def get_platform_name(self) -> str:
        """플랫폼 이름 반환"""
        pass
    
    def get_platform_version(self) -> str:
        """플랫폼 버전 반환"""
        pass
    
    def get_platform_settings(self) -> Dict[str, Any]:
        """플랫폼별 설정 반환"""
        pass 