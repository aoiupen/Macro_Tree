from typing import Callable, Set

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
        self._subscribers: Set[Callable[[], None]] = set()  # 변경 알림을 받을 콜백
        self._selected_items: Set[str] = set() # RF : 각 인스턴스마다 독립적인 선택 상태를 가져야 하므로 변수 할당, 초기화

    # ===== 인터페이스 메서드 =====
    def undo(self, tree: IMTTree) -> bool:
        result = self._state_mgr.undo(self._tree) is not None
        return result

    def redo(self, tree: IMTTree) -> bool:
        result = self._state_mgr.redo(self._tree) is not None
        return result

    def save_tree(self, tree_id: str | None = None) -> str | None:
        tree = self._view.get_current_tree()
        if not tree:
            return None
        try:
            saved_id = self._repository.save(tree, tree_id)
            return saved_id
        except Exception:
            return None

    def load_tree(self, tree_id: str) -> bool:
        try:
            tree = self._repository.load(tree_id)
            if tree:
                self._state_mgr.set_initial_state(tree)
                self._selected_items.clear()
                self._notify_change()
                return True
        except ValueError:
            pass
        return False 

    def subscribe(self, callback: Callable[[], None]) -> None:
        """변경 알림 구독"""
        self._subscribers.add(callback)

    def unsubscribe(self, callback: Callable[[], None]) -> None:
        """변경 알림 구독 해제"""
        if callback in self._subscribers:
            self._subscribers.remove(callback)

    # ===== 추가 메서드 (인터페이스에 없는 것) =====
    def can_undo(self) -> bool:
        """실행 취소 가능 여부를 반환합니다."""
        return self._state_mgr.can_undo()
    
    def can_redo(self) -> bool:
        """다시 실행 가능 여부를 반환합니다."""
        return self._state_mgr.can_redo()
    
    # RF : 각 클래스는 자신의 변경 알림 메커니즘을 독립적으로 가짐
    def _notify_change(self) -> None:
        """모든 구독자에게 변경을 알립니다."""
        for callback in self._subscribers:
            callback()
