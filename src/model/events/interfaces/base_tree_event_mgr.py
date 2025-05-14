from typing import Any, Callable, Dict, Protocol
from enum import Enum

# 트리 이벤트 유형을 직접 정의
class MTTreeEvent(Enum):
    """트리 이벤트 유형"""
    ITEM_ADDED = "item_added"
    ITEM_REMOVED = "item_removed"
    ITEM_MODIFIED = "item_modified"
    ITEM_MOVED = "item_moved"
    TREE_RESET = "tree_reset"
    TREE_CRUD = "tree_crud"

class MTTreeUIEvent(Enum):
    """트리 UI 이벤트 유형"""
    ITEM_SELECTED = "item_selected"
    ITEM_EXPANDED = "item_expanded"
    ITEM_COLLAPSED = "item_collapsed"

# 콜백 타입 정의 (타입 힌트)
TreeEventCallback = Callable[[MTTreeEvent, Dict[str, Any]], None]

class IMTTreeEventHandler(Protocol):
    """트리 이벤트 처리 인터페이스"""
    
    def handle_event(self, event_type: MTTreeEvent, data: Dict[str, Any]) -> None:
        """이벤트를 처리합니다."""
        ...

class IMTTreeEventManager(Protocol):
    """트리 이벤트 관리 인터페이스"""
    
    def subscribe(self, event_type: MTTreeEvent, callback: TreeEventCallback) -> None:
        """이벤트를 구독합니다."""
        ...
    
    def unsubscribe(self, event_type: MTTreeEvent, callback: TreeEventCallback) -> None:
        """이벤트 구독을 해제합니다."""
        ...
        
    def notify(self, event_type: MTTreeEvent, data: Dict[str, Any]) -> None:
        """이벤트를 구독자들에게 알립니다."""
        ... 