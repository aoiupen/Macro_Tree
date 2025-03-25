"""트리 View 인터페이스 모듈

트리 View의 인터페이스를 정의합니다.
"""
from typing import Protocol, Dict, Any, List, Optional

class ITreeView(Protocol):
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
    
    def set_selected_items(self, item_ids: List[str]) -> None:
        """선택된 아이템을 설정합니다."""
        ...
    
    def get_selected_items(self) -> List[str]:
        """선택된 아이템 ID 목록을 반환합니다."""
        ... 