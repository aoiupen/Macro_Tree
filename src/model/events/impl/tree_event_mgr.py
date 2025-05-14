from typing import Any, Dict, List

from model.events.interfaces.base_tree_event_mgr import IMTTreeEventManager, TreeEventCallback, MTTreeEvent

class MTTreeEventManager(IMTTreeEventManager):
    """트리 이벤트 관리자 구현체"""
    
    def __init__(self) -> None:
        """이벤트 관리자 초기화"""
        self._subscribers: Dict[MTTreeEvent, List[TreeEventCallback]] = {
            event: [] for event in MTTreeEvent
        }
    
    def subscribe(self, event_type: MTTreeEvent, callback: TreeEventCallback) -> None:
        """이벤트를 구독합니다."""
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        
        self._subscribers[event_type].append(callback)
    
    def unsubscribe(self, event_type: MTTreeEvent, callback: TreeEventCallback) -> None:
        """이벤트 구독을 해제합니다."""
        if event_type in self._subscribers:
            self._subscribers[event_type] = [cb for cb in self._subscribers[event_type] if cb != callback]
    
    def notify(self, event_type: MTTreeEvent, data: Dict[str, Any]) -> None:
        """이벤트를 구독자들에게 알립니다."""
        if event_type in self._subscribers:
            for callback in self._subscribers[event_type]:
                callback(event_type, data) 