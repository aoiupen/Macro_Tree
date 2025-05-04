from typing import Any, Callable, Dict, List, Set
from copy import deepcopy

from core.interfaces.base_tree import IMTTree
from model.tree_state_mgr import IMTTreeStateManager

class SimpleTreeStateManager(IMTTreeStateManager):
    """매크로 트리 상태 관리자 간단 구현"""
    
    def __init__(self, max_history: int = 50):
        """상태 관리자를 초기화합니다."""
        self._max_history = max_history
        self._history: List[IMTTree] = []
        self._current_index: int = -1
        self._subscribers: Set[Callable] = set()
    
    def set_initial_state(self, tree: IMTTree) -> None:
        """초기 상태를 설정합니다."""
        # 기존 이력 초기화
        self._history = []
        self._current_index = -1
        
        # 새 상태 저장
        self.save_state(tree)
    
    def save_state(self, tree: IMTTree) -> None:
        """현재 트리 상태를 이력에 저장"""
        # 현재 상태가 이력 중간인 경우, 이후 이력은 삭제
        if self._current_index < len(self._history) - 1:
            self._history = self._history[:self._current_index + 1]
        
        # 새 상태 복제해서 저장
        new_state = tree.clone()
        self._history.append(new_state)
        
        # 최대 이력 개수를 초과하면 오래된 이력 삭제
        if len(self._history) > self._max_history:
            self._history = self._history[-self._max_history:]
        
        # 현재 인덱스 업데이트
        self._current_index = len(self._history) - 1
        
        # 구독자에게 알림
        self._notify_subscribers()
    
    @property
    def current_state(self) -> IMTTree | None:
        """현재 트리 상태를 반환"""
        if self._current_index >= 0 and self._current_index < len(self._history):
            return self._history[self._current_index]
        return None
    
    def can_undo(self) -> bool:
        """실행 취소 가능 여부 확인"""
        return self._current_index > 0
    
    def can_redo(self) -> bool:
        """다시 실행 가능 여부 확인"""
        return self._current_index < len(self._history) - 1
    
    def undo(self) -> IMTTree | None:
        """이전 상태로 되돌리기"""
        if not self.can_undo():
            return None
        
        self._current_index -= 1
        self._notify_subscribers()
        return self.current_state
    
    def redo(self) -> IMTTree | None:
        """다음 상태로 복원"""
        if not self.can_redo():
            return None
        
        self._current_index += 1
        self._notify_subscribers()
        return self.current_state
    
    def clear(self) -> None:
        """모든 상태 이력 초기화"""
        self._history = []
        self._current_index = -1
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
