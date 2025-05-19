from typing import Any, Dict, List, Set

from model.events.interfaces.base_tree_event_mgr import IMTTreeEventManager, TreeEventCallback, MTTreeEvent

class EventManagerBase(IMTTreeEventManager):
    def __init__(self):
        self._subscribers: Dict[MTTreeEvent, List[TreeEventCallback]] = {event: [] for event in MTTreeEvent}

    def subscribe(self, event_type: MTTreeEvent, callback: TreeEventCallback) -> None:
        self._subscribers[event_type].append(callback)

    def unsubscribe(self, event_type: MTTreeEvent, callback: TreeEventCallback) -> None:
        self._subscribers[event_type] = [cb for cb in self._subscribers[event_type] if cb != callback]

    def notify(self, event_type: MTTreeEvent, data: Dict[str, Any]) -> None:
        for callback in self._subscribers[event_type]:
            callback(event_type, data)

class EventManagerSet(EventManagerBase):
    def __init__(self):
        self._subscribers: Dict[MTTreeEvent, Set[TreeEventCallback]] = {event: set() for event in MTTreeEvent}

    def subscribe(self, event_type: MTTreeEvent, callback: TreeEventCallback) -> None:
        self._subscribers[event_type].add(callback)

    def unsubscribe(self, event_type: MTTreeEvent, callback: TreeEventCallback) -> None:
        self._subscribers[event_type].discard(callback)

    def notify(self, event_type: MTTreeEvent, data: Dict[str, Any]) -> None:
        for callback in self._subscribers[event_type]:
            callback(event_type, data)

class MTTreeEventManager(EventManagerBase):
    """트리 이벤트 관리자 구현체"""
    pass 