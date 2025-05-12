from typing import Callable, Dict, Set
from uuid import uuid4

from core.impl.tree import MTTreeItem
from core.interfaces.base_item_data import MTTreeItemData
from core.interfaces.base_tree import IMTTreeItem, IMTTree
import core.exceptions as exc
#from model.state.interfaces.base_tree_state_mgr import IMTTreeStateManager
#from model.store.repo.interfaces.base_tree_repo import IMTTreeRepository
#from viewmodel.impl.tree_viewmodel_model import MTTreeViewModelModel
#from viewmodel.impl.tree_viewmodel_view import MTTreeViewModelView
from viewmodel.interfaces.base_tree_viewmodel_core import IMTTreeViewModelCore
#from viewmodel.interfaces.base_tree_viewmodel_model import IMTTreeViewModelModel
#from viewmodel.interfaces.base_tree_viewmodel_view import IMTTreeViewModelView

class MTTreeViewModelCore(IMTTreeViewModelCore):
    """데모 트리 뷰모델 구현"""
    
    def __init__(self, tree) -> None:
        """뷰모델 초기화
        Args:
            tree: 트리 인스턴스
        """
        self._tree: IMTTree | None = tree
        self._selected_items: Set[str] = set()  # 선택된 아이템 ID 집합

        # [state manager, repository 관련 코드 모음]
        # self._repository = repository
        # self._state_mgr: IMTTreeStateManager | None = state_manager
        # 필요시 아래와 같이 복원
        # if self._state_mgr:
        #     self._state_mgr.save_state(tree)

    def _get_tree(self) -> IMTTree:
        if not self._tree:
            raise RuntimeError("트리 객체가 존재하지 않습니다.")
        return self._tree

    # 1. 데이터 접근/조회
    def get_tree_items(self) -> Dict[str, IMTTreeItem]:
        tree = self._tree
        if not tree:
            return {}
        return tree.items

    # 2. CRUD/비즈니스 로직
    def add_item(self, name: str, parent_id: str | None = None, node_type: str = "INSTRUCTION") -> str | None:
        tree = self._get_tree()
        item_id = str(uuid4())
        item_data = MTTreeItemData(name=name, node_type=node_type)
        new_item = MTTreeItem(item_id, item_data)
        try:
            tree.add_item(new_item, parent_id)
            # state manager 관련 코드 필요시 아래 주석 해제
            # if self._state_mgr:
            #     self._state_mgr.save_state(tree)
            return item_id
        except exc.MTTreeItemAlreadyExistsError:
            return None
        except exc.MTTreeItemNotFoundError:
            return None

    def update_item(self, item_id: str, name: str | None = None, parent_id: str | None = None) -> bool:
        tree = self._get_tree()
        # if self._state_mgr:
        #     self._state_mgr.save_state(tree)
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
        # self._notify_change()
        return True

    def remove_item(self, item_id: str) -> bool:
        tree = self._get_tree()
        # if self._state_mgr:
        #     self._state_mgr.save_state(tree)
        if item_id in self._selected_items:
            self._selected_items.remove(item_id)
        try:
            tree.remove_item(item_id)
            # self._notify_change()
            return True
        except exc.MTTreeItemNotFoundError:
            return False

    def move_item(self, item_id: str, new_parent_id: str | None = None) -> bool:
        tree = self._get_tree()
        # if self._state_mgr:
        #     self._state_mgr.save_state(tree)
        try:
            tree.move_item(item_id, new_parent_id)
            # self._notify_change()
            return True
        except exc.MTTreeItemNotFoundError:
            return False
        except exc.MTTreeError:
            return False

    def _notify_change(self) -> None:
        # 변경 알림 구독자 콜백 호출 (구현 필요시 여기에 추가)
        pass
