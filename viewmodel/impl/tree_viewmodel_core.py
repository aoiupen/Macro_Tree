from typing import Callable, Dict, List, Optional, Set
from uuid import uuid4

from core.impl.tree import MTTreeItem
from core.interfaces.base_item_data import MTTreeItemData
from core.interfaces.base_tree import IMTTreeItem, IMTTree
import core.exceptions as exc
from model.services.state.interfaces.base_tree_state_mgr import IMTTreeStateManager
from model.store.repo.interfaces.base_tree_repo import IMTTreeRepository
from viewmodel.impl.tree_viewmodel_model import MTTreeViewModelModel
from viewmodel.impl.tree_viewmodel_view import MTTreeViewModelView
from viewmodel.interfaces.base_tree_viewmodel_core import IMTTreeViewModelCore
from viewmodel.interfaces.base_tree_viewmodel_model import IMTTreeViewModelModel
from viewmodel.interfaces.base_tree_viewmodel_view import IMTTreeViewModelView

class MTTreeViewModelCore(IMTTreeViewModelCore):
    """데모 트리 뷰모델 구현"""
    
    def __init__(self, tree, repository=None, state_manager=None) -> None:
        """뷰모델 초기화
        
        Args:
            tree: 트리 인스턴스
            repository: 트리 저장소
            state_manager: 트리 상태 관리자
        """
        self._tree: IMTTree | None = tree
        self._repository = repository
        self._state_mgr = state_manager
        self._selected_items: Set[str] = set()  # 선택된 아이템 ID 집합

        # 컴포지션 구조로 각 로직 컴포넌트 초기화
        self._view: IMTTreeViewModelView = MTTreeViewModelView()
        self._model: IMTTreeViewModelModel = MTTreeViewModelModel()
    
    # 1. 데이터 접근/조회
    def get_tree_items(self) -> Dict[str, IMTTreeItem]:
        """트리의 모든 아이템(노드) 객체를 ID → 객체 딕셔너리로 반환"""
        tree = self._tree
        if not tree:
            return {}
        return tree.get_all_items()

    # 2. CRUD/비즈니스 로직
    def add_item(self, name: str, parent_id: str | None = None) -> str | None:
        tree = self._tree
        if not tree:
            return None
        self._state_mgr.save_state(tree)
        item_id = str(uuid4())
        item_data = MTTreeItemData(name=name)
        new_item = MTTreeItem(item_id, item_data)
        try:
            tree.add_item(new_item, parent_id)
            self._notify_change()
            return item_id
        except exc.MTTreeItemAlreadyExistsError:
            return None
        except exc.MTTreeItemNotFoundError:
            return None

    def update_item(self, item_id: str, name: str | None = None, parent_id: str | None = None) -> bool:
        tree = self._tree
        if not tree:
            return False
        self._state_mgr.save_state(tree)
        item = tree.get_item(item_id)
        if not item:
            return False
        if name is not None:
            item.set_property("name", name)
        if parent_id is not None:
            try:
                tree.move_item(item_id, parent_id)
            except exc.MTTreeItemNotFoundError:
                return False
            except exc.MTTreeError:
                return False
        self._notify_change()
        return True

    def remove_item(self, item_id: str) -> bool:
        tree = self._tree
        if not tree:
            return False
        self._state_mgr.save_state(tree)
        if item_id in self._selected_items:
            self._selected_items.remove(item_id)
        try:
            tree.remove_item(item_id)
            self._notify_change()
            return True
        except exc.MTTreeItemNotFoundError:
            return False

    def move_item(self, item_id: str, new_parent_id: str | None = None) -> bool:
        tree = self._tree
        if not tree:
            return False
        self._state_mgr.save_state(tree)
        try:
            tree.move_item(item_id, new_parent_id)
            self._notify_change()
            return True
        except exc.MTTreeItemNotFoundError:
            return False
        except exc.MTTreeError:
            return False

    def _notify_change(self) -> None:
        # 변경 알림 구독자 콜백 호출 (구현 필요시 여기에 추가)
        pass
