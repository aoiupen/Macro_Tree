from typing import Protocol, Optional, Dict, Any, List, Callable
from temp.tree_interface import IMTTree
from temp.tree_item_interface import IMTTreeItem


class IMTTreeStateManager(Protocol):
    """매크로 트리 상태 관리자 인터페이스
    
    트리의 상태 이력을 관리하고 undo/redo 기능을 제공합니다.
    """
    
    def __init__(self, max_history: int = 50):
        """상태 관리자를 초기화합니다.
        
        Args:
            max_history: 저장할 최대 이력 수 (기본값: 50)
        """
        ...
    
    def save_state(self, tree: IMTTree) -> None:
        """현재 트리 상태를 이력에 저장
        
        Args:
            tree: 저장할 트리 상태
        """
        ...
    
    def current_state(self) -> Optional[IMTTree]:
        """현재 트리 상태를 반환
        
        Returns:
            현재 상태의 트리. 없으면 None
        """
        ...
    
    def can_undo(self) -> bool:
        """실행 취소 가능 여부 확인
        
        Returns:
            실행 취소 가능 여부
        """
        ...
    
    def can_redo(self) -> bool:
        """다시 실행 가능 여부 확인
        
        Returns:
            다시 실행 가능 여부
        """
        ...
    
    def undo(self) -> Optional[IMTTree]:
        """이전 상태로 되돌리기
        
        Returns:
            이전 상태의 트리. 불가능한 경우 None
        """
        ...
    
    def redo(self) -> Optional[IMTTree]:
        """다음 상태로 복원
        
        Returns:
            다음 상태의 트리. 불가능한 경우 None
        """
        ...
    
    def clear(self) -> None:
        """모든 상태 이력 초기화"""
        ...
    
    def subscribe(self, callback: Callable) -> None:
        """상태 변경 이벤트를 구독합니다.
        
        Args:
            callback: 상태 변경 시 호출할 콜백 함수
        """
        ...
    
    def unsubscribe(self, callback: Callable) -> None:
        """상태 변경 이벤트 구독을 해제합니다.
        
        Args:
            callback: 해제할 콜백 함수
        """
        ...