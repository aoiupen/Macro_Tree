from typing import Protocol, Dict, Any, Optional, List, Callable
from ..tree_item_interface import ITreeItem

class IUIElement(Protocol):
    """UI 요소의 기본 인터페이스"""
    
    def render(self) -> None:
        """UI 요소 렌더링"""
        pass
    
    def update(self, data: Dict[str, Any]) -> None:
        """UI 상태 업데이트"""
        pass
    
    def bind_item(self, item: Optional[ITreeItem]) -> None:
        """트리 아이템 바인딩"""
        pass
    
    def add_event_listener(self, event_type: str, handler: Callable) -> None:
        """이벤트 리스너 등록"""
        pass