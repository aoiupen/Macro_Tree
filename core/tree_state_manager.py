"""트리 상태 관리자 모듈

트리의 상태 이력을 관리하고 undo/redo 기능을 제공합니다.
"""
from collections import deque
from typing import Optional, Deque
import copy
from core.tree_state import TreeState
from PyQt6.QtCore import QObject, pyqtSignal, pyqtProperty, pyqtSlot
from core.tree_state_interface import ITreeStateManager


class TreeStateManager(QObject, ITreeStateManager):
    """트리 상태 관리자
    
    트리의 전체 상태 이력을 관리하고 undo/redo 기능을 제공합니다.
    현재는 전체 상태를 저장하는 방식을 사용하며, 추후 필요시 변경사항만 저장하는 방식으로 개선될 수 있습니다.
    """
    
    stateChanged = pyqtSignal()  # 상태 변경 시그널
    
    def __init__(self):
        """TreeStateManager 생성자"""
        super().__init__()
        self._state_deque: Deque[TreeState] = deque(maxlen=50)  # 최대 50개 상태 저장
        self._current_index: int = -1
    
    def save_state(self, tree_state: TreeState) -> None:
        """현재 상태를 저장합니다.
        
        현재 인덱스 이후의 상태들은 모두 제거되고 새로운 상태가 추가됩니다.
        
        Args:
            tree_state: 저장할 트리 상태
        """
        # 현재 위치 이후의 상태들은 제거
        while len(self._state_deque) > self._current_index + 1:
            self._state_deque.pop()
            
        self._state_deque.append(copy.deepcopy(tree_state))
        self._current_index = len(self._state_deque) - 1
        self.stateChanged.emit()
    
    def can_undo(self) -> bool:
        """Undo 가능 여부를 반환합니다.
        
        Returns:
            Undo 가능 여부
        """
        return self._current_index > 0
    
    def can_redo(self) -> bool:
        """Redo 가능 여부를 반환합니다.
        
        Returns:
            Redo 가능 여부
        """
        return self._current_index < len(self._state_deque) - 1
    
    def undo(self) -> Optional[TreeState]:
        """이전 상태로 되돌립니다.
        
        Returns:
            이전 상태. Undo가 불가능한 경우 None
        """
        if self.can_undo():
            self._current_index -= 1
            self.stateChanged.emit()
            return copy.deepcopy(self._state_deque[self._current_index])
        return None
    
    def redo(self) -> Optional[TreeState]:
        """다음 상태로 복원합니다.
        
        Returns:
            다음 상태. Redo가 불가능한 경우 None
        """
        if self.can_redo():
            self._current_index += 1
            self.stateChanged.emit()
            return copy.deepcopy(self._state_deque[self._current_index])
        return None
    
    def clear(self) -> None:
        """모든 상태 이력을 초기화합니다."""
        self._state_deque.clear()
        self._current_index = -1
        self.stateChanged.emit()

    @pyqtProperty(bool, notify=stateChanged)
    def canUndo(self):
        return self.can_undo()

    @pyqtProperty(bool, notify=stateChanged)
    def canRedo(self):
        return self.can_redo()

    @pyqtSlot(result=bool)
    def undoAction(self):
        result = self.undo()
        return result is not None

    @pyqtSlot(result=bool)
    def redoAction(self):
        result = self.redo()
        return result is not None 