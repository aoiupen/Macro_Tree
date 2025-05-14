from typing import Any, Callable, Dict, List, Set, Optional
from copy import deepcopy

from core.interfaces.base_tree import IMTTree
from model.state.interfaces.base_tree_state_mgr import IMTTreeStateManager

class MTTreeStateManager(IMTTreeStateManager):
    """매크로 트리 상태 관리자 구현"""
    
    def __init__(self, tree: IMTTree, max_history: int = 100):
        """상태 관리자를 초기화합니다."""
        self._max_history = max_history
        self._undo_stack: List[Dict[str, Any]] = []
        self._redo_stack: List[Dict[str, Any]] = []
        self._subscribers: Set[Callable] = set()
        self._new_stage = {}
        self.set_initial_state(tree)
    
    def set_initial_state(self, tree: IMTTree) -> None:
        """초기 상태를 설정합니다."""
        # 기존 이력 초기화
        self._undo_stack = []
        self._redo_stack = []
        self._new_stage = tree.to_dict()
    
    def can_undo(self) -> bool:
        """Undo 가능한 상태가 있는지 확인합니다."""
        return len(self._undo_stack) > 0
    
    def can_redo(self) -> bool:
        """Redo 가능한 상태가 있는지 확인합니다."""
        return len(self._redo_stack) > 0
    
    # 최대 히스토리 수 제한 (오래된 순으로 제거)
    def _limit_stack(self, stack: List[Dict[str, Any]]) -> None:
        if len(stack) > self._max_history:
            stack.pop(0)

    def new_undo(self, new_stage: Dict[str, Any]) -> Dict[str, Any] | None:
        """Stage를 Undo로, Redo는 비우고"""
        if not new_stage:
            return
        self._undo_stack.append(self._new_stage)
        self._new_stage = new_stage

        self._limit_stack(self._undo_stack)
        self._redo_stack.clear()
        
        self._notify_subscribers()
        return self._new_stage

    def undo(self, stage: Dict[str, Any]) -> Dict[str, Any] | None:
        """Undo를 Stage로, Stage를 Redo로"""
        if not self.can_undo():
            return None
        
        self._redo_stack.append(stage)
        self._limit_stack(self._redo_stack)
        self._new_stage = self._undo_stack.pop() # 가장 최근 상태 (Redo 스택으로 갈 것)
        
        self._notify_subscribers()
        return self._new_stage
    
    def redo(self, stage: Dict[str, Any]) -> Dict[str, Any] | None:
        """Redo를 Stage로, Stage를 Undo로"""
        if not self.can_redo():
            return None
        
        self._undo_stack.append(stage)
        self._limit_stack(self._undo_stack)
        self._new_stage = self._redo_stack.pop()
        
        self._notify_subscribers()
        return self._new_stage
    
    def subscribe(self, callback: Callable) -> None:
        """상태 변경 이벤트를 구독합니다."""
        self._subscribers.add(callback)
    
    def unsubscribe(self, callback: Callable) -> None:
        """상태 변경 이벤트 구독을 해제합니다."""
        if callback in self._subscribers:
            self._subscribers.remove(callback)
    
    def _notify_subscribers(self) -> None:
        """모든 구독자에게 상태 변경을 알립니다."""
        current = self._new_stage
        for callback in self._subscribers:
            callback(current)