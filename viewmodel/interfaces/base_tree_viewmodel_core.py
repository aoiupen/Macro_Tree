from typing import List, Protocol

from core.interfaces.base_item import IMTTreeItem
from model.services.state.interfaces.base_tree_state_mgr import IMTTreeStateManager
from model.store.repo.interfaces.base_tree_repo import IMTTreeRepository

class IMTTreeViewModelCore(Protocol):
    """트리 뷰모델 인터페이스 - 플랫폼 독립적 (Core)"""
    
    def __init__(self, repository: IMTTreeRepository, state_manager: IMTTreeStateManager):
        """ViewModel 초기화"""
        ...

    # 1. 데이터 접근/조회
    def get_tree_items(self) -> dict[str, IMTTreeItem]: ...

    # 2. CRUD/비즈니스 로직
    def add_item(self, name: str, parent_id: str | None = None) -> str | None: ...
    def update_item(self, item_id: str, name: str | None = None, parent_id: str | None = None) -> bool: ...
    def remove_item(self, item_id: str) -> bool: ...
    def move_item(self, item_id: str, new_parent_id: str | None = None) -> bool: ...
