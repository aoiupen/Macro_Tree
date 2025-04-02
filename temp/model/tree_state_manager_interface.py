from typing import Protocol, Optional, Dict, Any, List, Callable
from temp.core.tree_interface import IMTTree
from .tree_item_interface import IMTTreeItem


class IMTTreeStateManager(Protocol):
    """매크로 트리 상태 관리자 인터페이스"""
    
    def __init__(self, max_history: int = 50):
        """상태 관리자를 초기화합니다."""
        ...
    
    def save_state(self, tree: IMTTree) -> None:
        """현재 트리 상태를 이력에 저장"""
        ...
    
    def current_state(self) -> Optional[IMTTree]:
        """현재 트리 상태를 반환"""
        ...
    
    def can_undo(self) -> bool:
        """실행 취소 가능 여부 확인"""
        ...
    
    def can_redo(self) -> bool:
        """다시 실행 가능 여부 확인"""
        ...
    
    def undo(self) -> Optional[IMTTree]:
        """이전 상태로 되돌리기"""
        ...
    
    def redo(self) -> Optional[IMTTree]:
        """다음 상태로 복원"""
        ...
    
    def clear(self) -> None:
        """모든 상태 이력 초기화"""
        ...
    
    def subscribe(self, callback: Callable) -> None:
        """상태 변경 이벤트를 구독합니다."""
        ...
    
    def unsubscribe(self, callback: Callable) -> None:
        """상태 변경 이벤트 구독을 해제합니다."""
        ...