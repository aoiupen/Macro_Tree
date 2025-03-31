"""저장소 뷰모델 인터페이스 모듈

데이터 저장소와 View 사이의 중개자 역할을 하는 뷰모델 인터페이스를 정의합니다.
"""
from typing import Protocol, runtime_checkable, Optional
from core.tree_state import TreeState

@runtime_checkable
class IRepositoryViewModel(Protocol):
    """저장소 뷰모델 인터페이스
    
    데이터 저장소와 View 사이의 상호작용을 정의합니다.
    """
    
    def get_current_state(self) -> Optional[TreeState]:
        """현재 상태를 반환합니다."""
        ...
    
    def create_new_tree(self) -> bool:
        """새 트리를 생성합니다."""
        ...
    
    def load_tree_from_db(self) -> bool:
        """데이터베이스에서 트리를 로드합니다."""
        ...
    
    def save_tree(self, tree_state: TreeState) -> bool:
        """트리를 저장소에 저장합니다."""
        ...
    
    def save_current_tree(self) -> bool:
        """현재 트리 상태를 DB에 저장합니다."""
        ...
    
    def save_state(self, tree_state: TreeState) -> None:
        """현재 상태를 상태 관리자에 저장합니다."""
        ...
    
    def can_undo(self) -> bool:
        """실행 취소 가능 여부를 반환합니다."""
        ...
    
    def can_redo(self) -> bool:
        """다시 실행 가능 여부를 반환합니다."""
        ...
    
    def undo(self) -> bool:
        """변경 사항을 취소합니다."""
        ...
    
    def redo(self) -> bool:
        """취소한 변경 사항을 다시 적용합니다."""
        ...
    
    def clear_history(self) -> None:
        """상태 이력을 모두 지웁니다."""
        ... 