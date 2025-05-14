from typing import Any, Callable, Dict, List, Set, Optional
from copy import deepcopy

from core.interfaces.base_tree import IMTTree
from model.state.interfaces.base_tree_state_mgr import IMTTreeStateManager

class MTTreeStateManager(IMTTreeStateManager):
    """매크로 트리 상태 관리자 구현"""
    
    def __init__(self, max_history: int = 100):
        """상태 관리자를 초기화합니다."""
        self._max_history = max_history
        self._undo_stack: List[Dict[str, Any]] = []
        self._redo_stack: List[Dict[str, Any]] = []
        self._subscribers: Set[Callable] = set()
    
    def set_initial_state(self, tree: IMTTree) -> None:
        """초기 상태를 설정합니다."""
        # 기존 이력 초기화
        self._undo_stack = []
        self._redo_stack = []
        
        # 새 상태 저장
        self.save_state(tree.to_dict())
    
    def save_state(self, snapshot_data: Dict[str, Any]) -> None:
        """현재 상태를 Undo 스택에 저장하고, Redo 스택을 비웁니다."""
        if not snapshot_data:
            return

        self._undo_stack.append(snapshot_data)
        # 최대 히스토리 수 제한 (오래된 순으로 제거)
        if len(self._undo_stack) > self._max_history:
            self._undo_stack.pop(0)
        
        
        # 구독자에게 알림
        self._notify_subscribers()
    
    @property
    def current_state(self) -> Dict[str, Any] | None:
        """현재 트리 상태를 반환"""
        if self._undo_stack:
            return self._undo_stack[-1]
        return None
    
    def can_undo(self) -> bool:
        """Undo 가능한 상태가 있는지 확인합니다."""
        return len(self._undo_stack) > 0
    
    def can_redo(self) -> bool:
        """Redo 가능한 상태가 있는지 확인합니다."""
        return len(self._redo_stack) > 0
    
    def undo(self) -> Dict[str, Any] | None:
        """Undo 스택에서 이전 상태를 가져와 Redo 스택에 현재 상태(실제로는 직전 상태)를 저장하고, 이전 상태를 반환합니다."""
        if not self.can_undo():
            return None
        
        current_state_for_redo = self._undo_stack.pop() # 가장 최근 상태 (Redo 스택으로 갈 것)
        self._redo_stack.append(current_state_for_redo)
        if len(self._redo_stack) > self._max_history:
            self._redo_stack.pop(0)

        if not self._undo_stack: # Redo로 옮긴 후 Undo 스택이 비었다면, 복원할 과거 상태 없음
            return None 
        
        self._notify_subscribers()
        return self._undo_stack[-1] # 복원할 이전 상태 (pop하지 않고 peek)
    
    def redo(self) -> Dict[str, Any] | None:
        """Redo 스택에서 다음 상태를 가져와 Undo 스택에 현재 상태(실제로는 직전 상태)를 저장하고, 다음 상태를 반환합니다."""
        if not self.can_redo():
            return None
        
        state_to_restore = self._redo_stack.pop()
        self._undo_stack.append(state_to_restore) # 복원되는 상태이므로, 다시 undo 가능하도록 undo 스택에 추가
        if len(self._undo_stack) > self._max_history:
            self._undo_stack.pop(0)
        
        self._notify_subscribers()
        return state_to_restore
    
    def clear(self) -> None:
        """모든 상태 이력 초기화"""
        self._undo_stack = []
        self._redo_stack = []
        self._notify_subscribers()
    
    def subscribe(self, callback: Callable) -> None:
        """상태 변경 이벤트를 구독합니다."""
        self._subscribers.add(callback)
    
    def unsubscribe(self, callback: Callable) -> None:
        """상태 변경 이벤트 구독을 해제합니다."""
        if callback in self._subscribers:
            self._subscribers.remove(callback)
    
    def _notify_subscribers(self) -> None:
        """모든 구독자에게 상태 변경을 알립니다."""
        current = self.current_state
        for callback in self._subscribers:
            callback(current)

    def clear_history(self) -> None:
        """모든 Undo/Redo 히스토리를 삭제합니다."""
        self._undo_stack.clear()
        self._redo_stack.clear()
