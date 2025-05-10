from typing import Any, Callable, Dict, List, Optional, Protocol

from core.interfaces.base_tree import IMTTree
from core.interfaces.base_item import IMTTreeItem


class IMTTreeStateManager(Protocol):
    """매크로 트리 상태 관리자 인터페이스
    
    트리의 상태 변경을 추적하고 관리합니다.
    """
    
    def __init__(self, max_history: int = 50):
        """상태 관리자를 초기화합니다."""
        ...
    
    def set_initial_state(self, tree: IMTTree) -> None:
        """초기 상태를 설정합니다."""
        ...
    
    @property
    def current_state(self) -> IMTTree | None:
        """현재 상태의 트리를 반환합니다."""
        ...
    
    def save_state(self, tree: IMTTree) -> None:
        """현재 상태를 저장합니다."""
        ...
    
    def can_undo(self) -> bool:
        """되돌리기 가능 여부를 반환합니다."""
        ...
    
    def can_redo(self) -> bool:
        """다시 실행 가능 여부를 반환합니다."""
        ...
    
    def undo(self) -> IMTTree | None:
        """이전 상태로 되돌립니다."""
        ...
    
    def redo(self) -> IMTTree | None:
        """다음 상태로 복원합니다."""
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