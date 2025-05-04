from typing import Any, Callable, Dict, List, Protocol

from core.interfaces.base_tree import IMTTree, IMTTreeModifiable, IMTTreeData, IMTTreeTraversable
from core.interfaces.base_item import IMTTreeItem
from model.tree_repo import IMTTreeRepository
from model.tree_state_mgr import IMTTreeStateManager


class IMTTreeViewModel(Protocol):
    """트리 뷰모델 인터페이스 - 플랫폼 독립적"""
    
    def __init__(self, repository: IMTTreeRepository, state_manager: IMTTreeStateManager):
        """ViewModel 초기화"""
        ...
    
    def load_tree(self, tree_id: str) -> bool:
        """저장소에서 트리 로드"""
        ...
    
    def save_tree(self, tree_id: str | None = None) -> str:
        """현재 트리를 저장소에 저장"""
        ...
    
    def get_current_tree(self) -> IMTTree | None:
        """현재 로드된 트리 반환"""
        ...
    
    def get_items(self) -> List[Dict[str, Any]]:
        """UI 표시용 트리 아이템 목록 반환"""
        ...
    
    def select_item(self, item_id: str) -> bool:
        """트리 아이템 선택"""
        ...
    
    def get_selected_items(self) -> List[str]:
        """선택된 아이템 ID 목록 반환"""
        ...
    
    def add_item(self, parent_id: str | None, data: Dict[str, Any]) -> str:
        """부모 아래에 새 아이템 추가 (IMTTreeModifiable 사용)"""
        ...
    
    def remove_item(self, item_id: str) -> bool:
        """아이템 제거 (IMTTreeModifiable 사용)"""
        ...
    
    def move_item(self, item_id: str, new_parent_id: str | None) -> bool:
        """아이템 이동 (IMTTreeModifiable 사용)"""
        ...
    
    def get_item_children(self, parent_id: str | None) -> List[Dict[str, Any]]:
        """특정 부모의 자식 아이템 목록 (IMTTreeReadable 사용)"""
        ...
    
    def traverse_tree(self, visitor_func: Callable[[Dict[str, Any]], None]) -> None:
        """트리 순회 (IMTTreeTraversable 사용)"""
        ...
