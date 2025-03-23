"""저장소 인터페이스 모듈

데이터 접근 계층(Repository)의 인터페이스를 정의합니다.
"""
from typing import Protocol, runtime_checkable, Optional, Dict, Any, List
from core.tree_state import TreeState

@runtime_checkable
class ITreeDataRepository(Protocol):
    """트리 데이터 저장소 인터페이스
    
    트리 데이터의 영속성 관리 기능을 정의합니다.
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
    
    def update_tree(self, changes: Dict[str, Dict[str, Any]]) -> None:
        """트리에 변경 사항을 적용합니다."""
        ... 