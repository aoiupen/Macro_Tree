"""ViewModel 공통 인터페이스 모듈

모든 플랫폼에서 공통으로 사용되는 ViewModel 인터페이스를 정의합니다.
"""
from typing import Protocol, Dict, Any, Optional, List
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

class IViewModel(Protocol):
    """ViewModel 기본 인터페이스"""
    
    @property
    def config(self) -> ViewModelConfig:
        """ViewModel 설정을 반환합니다."""
        ...
    
    def initialize(self) -> bool:
        """ViewModel을 초기화합니다."""
        ...
    
    def dispose(self) -> None:
        """ViewModel을 정리합니다."""
        ...
    
    def get_state(self) -> Dict[str, Any]:
        """현재 상태를 반환합니다."""
        ...

class ITreeViewModel(IViewModel, Protocol):
    """트리 ViewModel 인터페이스"""
    
    def get_items(self) -> List[Dict[str, Any]]:
        """트리 아이템 목록을 반환합니다."""
        ...
    
    def add_item(self, item: Dict[str, Any]) -> bool:
        """아이템을 추가합니다."""
        ...
    
    def remove_item(self, item_id: str) -> bool:
        """아이템을 제거합니다."""
        ...
    
    def update_item(self, item_id: str, data: Dict[str, Any]) -> bool:
        """아이템을 업데이트합니다."""
        ...

class IItemViewModel(IViewModel, Protocol):
    """아이템 ViewModel 인터페이스"""
    
    @property
    def id(self) -> str:
        """아이템 ID를 반환합니다."""
        ...
    
    @property
    def name(self) -> str:
        """아이템 이름을 반환합니다."""
        ...
    
    def is_group(self) -> bool:
        """그룹 여부를 반환합니다."""
        ...
    
    def is_inst(self) -> bool:
        """인스턴스 여부를 반환합니다."""
        ... 