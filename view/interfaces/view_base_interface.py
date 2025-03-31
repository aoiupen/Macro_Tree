"""View 공통 인터페이스 모듈

모든 플랫폼에서 공통으로 사용되는 View 인터페이스를 정의합니다.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from enum import Enum


class ViewType(Enum):
    """View 타입 열거형"""
    TREE = "tree"
    ITEM = "item"
    DIALOG = "dialog"


@dataclass
class ViewConfig:
    """View 설정 데이터 클래스"""
    view_type: ViewType
    platform_type: str
    theme: str
    debug_mode: bool = False


class IView(ABC):
    """View 기본 인터페이스"""
    
    @property
    @abstractmethod
    def config(self) -> ViewConfig:
        """View 설정을 반환합니다."""
        pass
    
    @abstractmethod
    def initialize(self) -> bool:
        """View를 초기화합니다.
        
        Returns:
            초기화 성공 여부
        """
        pass
    
    @abstractmethod
    def dispose(self) -> None:
        """View를 정리합니다."""
        pass
    
    @abstractmethod
    def show(self) -> None:
        """View를 표시합니다."""
        pass
    
    @abstractmethod
    def hide(self) -> None:
        """View를 숨깁니다."""
        pass
    
    @abstractmethod
    def update_theme(self, theme: str) -> None:
        """테마를 업데이트합니다.
        
        Args:
            theme: 적용할 테마
        """
        pass 