from typing import Callable, Dict, Set
from uuid import uuid4
from model.events.interfaces.base_tree_event_mgr import MTTreeEvent
from core.impl.tree import MTTreeItem
from core.interfaces.base_item_data import MTTreeItemData
from core.interfaces.base_tree import IMTTreeItem, IMTTree
import core.exceptions as exc
from core.interfaces.base_item_data import MTNodeType
from viewmodel.interfaces.base_tree_viewmodel_core import IMTTreeViewModelCore

class MTTreeViewModelCore(IMTTreeViewModelCore):
    """데모 트리 뷰모델 구현"""
    
    def __init__(self, tree) -> None:
        """뷰모델 초기화
        Args:
            tree: 트리 인스턴스
        """
        self._tree: IMTTree | None = tree
        self._selected_items: Set[str] = set()

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
    def add_item(self, name: str, parent_id: str | None = None, index: int = -1, node_type: MTNodeType | None = None) -> str | None:
        tree = self._get_tree()
        item_id = str(uuid4())
        item_data = MTTreeItemData(name=name, node_type=node_type)
        new_item = MTTreeItem(item_id, item_data)
        try:
            tree.add_item(new_item, parent_id, index)
            return item_id
        except exc.MTTreeItemAlreadyExistsError:
            return None
        except exc.MTTreeItemNotFoundError:
            return None
        except exc.MTTreeError:
            return False

    def update_item(self, item_id: str, name: str | None = None, parent_id: str | None = None) -> bool:
        tree = self._get_tree()

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
        return True

    def remove_item(self, item_id: str) -> bool:
        tree = self._get_tree()

        if item_id in self._selected_items:
            self._selected_items.remove(item_id)
        try:
            tree.remove_item(item_id)
            return True
        except exc.MTTreeItemNotFoundError:
            return False

    def move_item(self, item_id: str, new_parent_id: str | None = None, new_index: int = -1) -> bool:
        tree = self._get_tree()

        try:
            result = tree.move_item(item_id, new_parent_id, new_index)
            return result
        except exc.MTTreeItemNotFoundError:
            return False
        except exc.MTTreeError:
            return False

    def get_item_node_type(self, item_id: str) -> MTNodeType | None:
        """지정된 ID를 가진 아이템의 노드 타입을 반환합니다."""
        tree = self._get_tree()
        item = tree.get_item(item_id)
        if item:
            return item.get_property("node_type")
        return None

    def get_item_parent_id(self, item_id: str) -> str | None:
        """지정된 ID를 가진 아이템의 부모 ID를 반환합니다."""
        tree = self._get_tree()
        item = tree.get_item(item_id)
        if item:
            return item.get_property("parent_id")
        return None

    def get_children_ids(self, parent_id: str) -> list[str] | None:
        """지정된 부모 ID를 가진 모든 자식 아이템들의 ID 리스트를 반환합니다."""
        tree = self._get_tree()
        if hasattr(tree, 'get_children_ids'):
            return tree.get_children_ids(parent_id)
        else:
            children_ids = []
            for item_id_key, item_value in tree.items.items():
                if item_value.get_property("parent_id") == parent_id:
                    children_ids.append(item_id_key)
            return children_ids if children_ids else None

    def restore_tree_from_snapshot(self, snapshot_dict: dict) -> None:
        """주어진 스냅샷 딕셔너리로부터 트리 상태를 복원합니다."""
        tree = self._get_tree()
        if hasattr(tree, 'dict_to_state'):
            tree.dict_to_state(snapshot_dict)
        else:
            print("Error: Tree object does not have a dict_to_state method.")

    def to_dict(self):
        return self._tree.to_dict()

    def dict_to_state(self, data):
        return self._tree.dict_to_state(data)