from typing import Callable, Set, Dict, Any

from model.state.impl.tree_state_mgr import MTTreeStateManager
from model.state.interfaces.base_tree_state_mgr import IMTTreeStateManager
from model.store.db.impl.postgres_repo import PostgreSQLTreeRepository
from model.store.repo.interfaces.base_tree_repo import IMTTreeRepository
from viewmodel.interfaces.base_tree_viewmodel_model import IMTTreeViewModelModel
from core.interfaces.base_tree import IMTTree
from model.events.interfaces.base_tree_event_mgr import MTTreeEvent
class MTTreeViewModelModel(IMTTreeViewModelModel):
    def __init__(self, tree: IMTTree, state_manager: IMTTreeStateManager) -> None:
        self._tree = tree
        if not state_manager:
            raise ValueError("MTTreeViewModelModel 생성 시 state_manager는 반드시 제공되어야 합니다.")
        self._state_mgr: IMTTreeStateManager = state_manager
        self._repository: IMTTreeRepository = PostgreSQLTreeRepository()
        self._selected_items: Set[str] = set() # RF : 각 인스턴스마다 독립적인 선택 상태를 가져야 하므로 변수 할당, 초기화

    # ===== 인터페이스 메서드 =====
    def save_tree(self, tree_id: str | None = None) -> str | None:
        tree = self._view.get_current_tree()
        if not tree:
            return None
        try:
            saved_id = self._repository.save(tree, tree_id)
            if isinstance(saved_id, str) or saved_id is None:
                return saved_id
            return str(saved_id)
        except Exception:
            return None

    def load_tree(self, tree_id: str) -> bool:
        try:
            tree = self._repository.load(tree_id)
            if tree:
                self._state_mgr.set_initial_state(tree)
                self._selected_items.clear()
                self._state_mgr
                return True
        except ValueError:
            pass
        return False 

    def subscribe(self, event_type: MTTreeEvent, callback: Callable) -> None:
        self._state_mgr.subscribe(event_type, callback)

    def unsubscribe(self, event_type: MTTreeEvent, callback: Callable) -> None:
        self._state_mgr.unsubscribe(event_type, callback)
