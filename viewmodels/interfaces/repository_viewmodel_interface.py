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
    
    def load_tree(self) -> Optional[TreeState]:
        """저장소에서 트리를 로드합니다."""
        ...
    
    def save_tree(self, tree_state: TreeState) -> bool:
        """트리를 저장소에 저장합니다."""
        ...
    
    def save_state(self, tree_state: TreeState) -> None:
        """현재 상태를 저장소에 저장합니다."""
        ... 