from typing import Callable, Dict, Set
from uuid import uuid4
from model.events.interfaces.base_tree_event_mgr import MTTreeEvent
from core.impl.tree import MTItem
from core.interfaces.base_item_data import MTItemDomainDTO, MTItemUIStateDTO, MTItemDTO
from core.interfaces.base_tree import IMTItem, IMTTree
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
    def get_all_item_dtos(self) -> Dict[str, MTItemDTO]:
        tree = self._get_tree()
        if hasattr(tree, 'items_dtos') and callable(getattr(tree, 'items_dtos')):
            return tree.items_dtos()
        elif hasattr(tree, 'items_dtos'):
            return tree.items_dtos
        else:
            return {item_id: item.to_dto() for item_id, item in tree.items.items()}

    def get_item(self, item_id: str) -> IMTItem | None:
        """지정된 ID를 가진 아이템을 반환합니다."""
        tree = self._get_tree()
        return tree.get_item(item_id)

    # 2. CRUD/비즈니스 로직
    def add_item(self, item_dto: MTItemDTO, index: int = -1) -> str | None:
        tree = self._get_tree()
        try:
            item_id = tree.add_item(
                item_dto=item_dto,
                index=index
            )
            return item_id
        except exc.MTItemNotFoundError:
            return None
        except exc.MTTreeError as e:
            print(f"Error in add_item: {e}")
            return None

    def update_item(self, item_id: str, item_dto: MTItemDTO) -> bool:
        tree = self._get_tree()
        try:
            return tree.modify_item(item_id, item_dto)
        except exc.MTItemNotFoundError:
            return False
        except Exception as e:
            print(f"Error in update_item: {e}")
            return False

    def remove_item(self, item_id: str) -> bool:
        tree = self._get_tree()
        if item_id in self._selected_items:
            self._selected_items.remove(item_id)
        try:
            tree.remove_item(item_id)
            return True
        except exc.MTItemNotFoundError:
            return False

    def move_item(self, item_id: str, new_parent_id: str | None = None, new_index: int = -1) -> bool:
        tree = self._get_tree()
        try:
            result = tree.move_item(item_id, new_parent_id, new_index)
            return bool(result)
        except exc.MTItemNotFoundError:
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

    def get_children_ids(self, parent_id: str) -> list[str]:
        tree = self._get_tree()
        if hasattr(tree, 'get_children_ids'):
            result = tree.get_children_ids(parent_id)
            return result if result is not None else []
        else:
            children_ids = []
            for item_id_key, item_value in tree.items.items():
                if item_value.get_property("parent_id") == parent_id:
                    children_ids.append(item_id_key)
            return children_ids

    def restore_tree_from_snapshot(self, snapshot_dict: dict) -> None:
        """주어진 스냅샷 딕셔너리로부터 트리 상태를 복원합니다."""
        tree = self._get_tree()
        if hasattr(tree, 'dict_to_state'):
            tree.dict_to_state(snapshot_dict)
        else:
            print("Error: Tree object does not have a dict_to_state method.")

    def to_dict(self) -> dict:
        return self._tree.to_dict() if self._tree else {}

    def dict_to_state(self, data):
        return self._tree.dict_to_state(data)