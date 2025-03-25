"""트리 ViewModel 인터페이스 모듈

트리 ViewModel의 인터페이스를 정의합니다.
"""
from typing import Protocol, Dict, Any, List, Optional

class ITreeViewModel(Protocol):
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
    
    def get_selected_items(self) -> List[str]:
        """선택된 아이템 ID 목록을 반환합니다."""
        ...
    
    def set_selected_items(self, item_ids: List[str]) -> None:
        """선택된 아이템을 설정합니다."""
        ... 