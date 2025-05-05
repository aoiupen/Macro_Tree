from typing import List, Dict, Any, Protocol
from core.interfaces.base_tree import IMTTree, IMTTreeModifiable, IMTTreeReadable, IMTTreeTraversable
from core.interfaces.base_item import IMTTreeItem
from model.store.repo.interfaces.base_tree_repo import IMTTreeRepository
from model.services.state.interfaces.base_tree_state_mgr import IMTTreeStateManager


class IMTTreeViewModel(Protocol):
    """트리 뷰모델 인터페이스 - 플랫폼 독립적"""
    
    def __init__(self, repository: IMTTreeRepository, state_manager: IMTTreeStateManager):
        """ViewModel 초기화"""
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
    
    def get_item_children(self, parent_id: str | None) -> List[Dict[str, Any]]:
        """특정 부모의 자식 아이템 목록 (IMTTreeReadable 사용)"""
        ...
    
