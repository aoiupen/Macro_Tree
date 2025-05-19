from typing import Any, Callable, Dict, List, Set, Optional
from copy import deepcopy

from core.interfaces.base_tree import IMTTree
from model.events.interfaces.base_tree_event_mgr import MTTreeEvent
from model.state.interfaces.base_tree_state_mgr import IMTTreeStateManager
from model.events.interfaces.base_tree_event_mgr import TreeEventCallback
from model.events.impl.tree_event_mgr import EventManagerBase

# MTNodeType Enum을 사용한다면 import 필요
# from core.interfaces.base_item_data import MTNodeType # 예시 경로


class History:
    def __init__(self, tree: IMTTree, max_history: int = 100):
        self._max_history = max_history
        self._undo_stack: List[Dict[str, Any]] = []
        self._redo_stack: List[Dict[str, Any]] = []
        self._stage = {}
        self.set_initial_state(tree)

    def set_initial_state(self, tree: IMTTree) -> None:
        self._undo_stack = []
        self._redo_stack = []
        self._stage = tree.to_dict()

    def can_undo(self) -> bool:
        return len(self._undo_stack) > 0

    def can_redo(self) -> bool:
        return len(self._redo_stack) > 0

    def _limit_stack(self, stack: List[Dict[str, Any]]) -> None:
        if len(stack) > self._max_history:
            stack.pop(0)

    def new_undo(self, new_stage: Dict[str, Any]) -> Dict[str, Any] | None:
        if not new_stage:
            return
        self._undo_stack.append(self._stage)
        self._stage = new_stage
        self._limit_stack(self._undo_stack)
        self._redo_stack.clear()
        return self._stage

    def undo(self) -> Dict[str, Any] | None:
        if not self.can_undo():
            return None
        self._redo_stack.append(self._stage)
        self._limit_stack(self._redo_stack)
        self._stage = self._undo_stack.pop()
        return self._stage

    def redo(self) -> Dict[str, Any] | None:
        if not self.can_redo():
            return None
        self._undo_stack.append(self._stage)
        self._limit_stack(self._undo_stack)
        self._stage = self._redo_stack.pop()
        return self._stage

class MTTreeStateManager(EventManagerBase, IMTTreeStateManager):
    """매크로 트리 상태 관리자 구현"""
    def __init__(self, tree: IMTTree, max_history: int = 100):
        super().__init__()
        self._history = History(tree, max_history)

    def set_initial_state(self, tree: IMTTree) -> None:
        self._history.set_initial_state(tree)

    def can_undo(self) -> bool:
        return self._history.can_undo()

    def can_redo(self) -> bool:
        return self._history.can_redo()

    def new_undo(self, new_stage: Dict[str, Any]) -> Dict[str, Any] | None:
        result = self._history.new_undo(new_stage)
        self.notify(MTTreeEvent.TREE_CRUD, self._history._stage)
        return result

    def undo(self) -> Dict[str, Any] | None:
        result = self._history.undo()
        self.notify(MTTreeEvent.TREE_UNDO, self._history._stage)
        return result

    def redo(self) -> Dict[str, Any] | None:
        result = self._history.redo()
        self.notify(MTTreeEvent.TREE_REDO, self._history._stage)
        return result 