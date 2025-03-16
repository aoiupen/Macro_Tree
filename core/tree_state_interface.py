# core/interfaces.py
from abc import ABC, abstractmethod
from typing import Optional
from core.tree_state import TreeState

class ITreeStateManager(ABC):
    """트리 상태 관리 인터페이스
    
    상태 이력을 관리하고 undo/redo 기능을 제공합니다.
    """
    
    @abstractmethod
    def save_state(self, tree_state: TreeState) -> None:
        """현재 상태를 저장합니다."""
        pass
    
    @abstractmethod
    def can_undo(self) -> bool:
        """Undo 가능 여부를 반환합니다."""
        pass
    
    @abstractmethod
    def can_redo(self) -> bool:
        """Redo 가능 여부를 반환합니다."""
        pass
    
    @abstractmethod
    def undo(self) -> Optional[TreeState]:
        """이전 상태로 되돌립니다."""
        pass
    
    @abstractmethod
    def redo(self) -> Optional[TreeState]:
        """다음 상태로 복원합니다."""
        pass