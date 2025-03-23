# core/interfaces.py
from typing import Protocol, Optional, runtime_checkable
from core.tree_state import TreeState

@runtime_checkable
class ITreeStateManager(Protocol):
    """트리 상태 관리 프로토콜
    
    상태 이력을 관리하고 undo/redo 기능을 제공합니다.
    """
    
    def save_state(self, tree_state: TreeState) -> None:
        """현재 상태를 저장합니다."""
        ...
    
    def can_undo(self) -> bool:
        """Undo 가능 여부를 반환합니다."""
        ...
    
    def can_redo(self) -> bool:
        """Redo 가능 여부를 반환합니다."""
        ...
    
    def undo(self) -> Optional[TreeState]:
        """이전 상태로 되돌립니다."""
        ...
    
    def redo(self) -> Optional[TreeState]:
        """다음 상태로 복원합니다."""
        ...
    
    def clear(self) -> None:
        """모든 상태 이력을 초기화합니다."""
        ...