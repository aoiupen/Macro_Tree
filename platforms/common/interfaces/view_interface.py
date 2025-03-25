"""View 공통 인터페이스 모듈

모든 플랫폼에서 공통으로 사용되는 View 인터페이스를 정의합니다.
"""
from typing import Protocol, Dict, Any, Optional, List
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

class IView(Protocol):
    """View 기본 인터페이스"""
    
    @property
    def config(self) -> ViewConfig:
        """View 설정을 반환합니다."""
        ...
    
    def initialize(self) -> bool:
        """View를 초기화합니다."""
        ...
    
    def dispose(self) -> None:
        """View를 정리합니다."""
        ...
    
    def show(self) -> None:
        """View를 표시합니다."""
        ...
    
    def hide(self) -> None:
        """View를 숨깁니다."""
        ...
    
    def update_theme(self, theme: str) -> None:
        """테마를 업데이트합니다."""
        ...

class ITreeView(IView, Protocol):
    """트리 View 인터페이스"""
    
    def set_items(self, items: List[Dict[str, Any]]) -> None:
        """트리 아이템을 설정합니다."""
        ...
    
    def add_item(self, item: Dict[str, Any]) -> None:
        """아이템을 추가합니다."""
        ...
    
    def remove_item(self, item_id: str) -> None:
        """아이템을 제거합니다."""
        ...
    
    def update_item(self, item_id: str, data: Dict[str, Any]) -> None:
        """아이템을 업데이트합니다."""
        ...
    
    def expand_item(self, item_id: str) -> None:
        """아이템을 확장합니다."""
        ...
    
    def collapse_item(self, item_id: str) -> None:
        """아이템을 축소합니다."""
        ...

class IItemView(IView, Protocol):
    """아이템 View 인터페이스"""
    
    def set_data(self, data: Dict[str, Any]) -> None:
        """데이터를 설정합니다."""
        ...
    
    def get_data(self) -> Dict[str, Any]:
        """데이터를 반환합니다."""
        ...
    
    def set_editable(self, editable: bool) -> None:
        """편집 가능 여부를 설정합니다."""
        ...
    
    def set_selected(self, selected: bool) -> None:
        """선택 여부를 설정합니다."""
        ... 