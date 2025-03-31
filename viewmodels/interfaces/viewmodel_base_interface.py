"""ViewModel 공통 인터페이스 모듈

모든 플랫폼에서 공통으로 사용되는 ViewModel 인터페이스를 정의합니다.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from enum import Enum


class ViewModelType(Enum):
    """ViewModel 타입 열거형"""
    TREE = "tree"
    ITEM = "item"
    REPOSITORY = "repository"


@dataclass
class ViewModelConfig:
    """ViewModel 설정 데이터 클래스"""
    viewmodel_type: ViewModelType
    platform_type: str
    debug_mode: bool = False


class IViewModel(ABC):
    """ViewModel 기본 인터페이스"""
    
    @property
    @abstractmethod
    def config(self) -> ViewModelConfig:
        """ViewModel 설정을 반환합니다."""
        pass
    
    @abstractmethod
    def initialize(self) -> bool:
        """ViewModel을 초기화합니다.
        
        Returns:
            초기화 성공 여부
        """
        pass
    
    @abstractmethod
    def dispose(self) -> None:
        """ViewModel을 정리합니다."""
        pass
    
    @abstractmethod
    def get_state(self) -> Dict[str, Any]:
        """현재 상태를 반환합니다.
        
        Returns:
            현재 상태 데이터
        """
        pass 