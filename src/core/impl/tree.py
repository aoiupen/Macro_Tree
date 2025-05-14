from typing import Any, Callable, Dict, List, Optional, Set, cast
import json
import copy

from core.interfaces.base_item import IMTTreeItem
from core.interfaces.base_tree import IMTTree
from core.impl.item import MTTreeItem
from model.events.interfaces.base_tree_event_mgr import MTTreeEvent, IMTTreeEventManager
import core.exceptions as exc
from core.interfaces.base_item_data import MTNodeType

# 역할별 내부 구현 클래스 분리
class _MTTreeReadable:
    def __init__(self, tree: "MTTree"):
        self._tree = tree

    @property
    def id(self) -> str:
        return self._tree._id

    @property
    def name(self) -> str:
        return self._tree._name

    @property
    def root_id(self) -> str | None:
        return self._tree._root_id

    @property
    def items(self) -> dict[str, IMTTreeItem]:
        return self._tree._items
    
    def get_item(self, item_id: str) -> IMTTreeItem | None:
        return self._tree._items.get(item_id)

    def get_children(self, parent_id: str | None) -> List[IMTTreeItem]:
        id_to_query_children_for = parent_id
        if parent_id is None:
            id_to_query_children_for = self._tree._root_id

        if id_to_query_children_for is None or id_to_query_children_for not in self._tree._items:
            return []

        parent_item = self._tree._items[id_to_query_children_for]
        children_ids = parent_item.get_property("children_ids", [])
        
        children_items: List[IMTTreeItem] = []
        for child_id in children_ids:
            child = self._tree._items.get(child_id)
            if child:
                children_items.append(child)
        return children_items

class _MTTreeModifiable:
    def __init__(self, tree: "MTTree"):
        self._tree = tree

    def add_item(self, item: IMTTreeItem, parent_id: str | None) -> bool:
        item_id = item.id
        if item_id in self._tree._items:
            raise exc.MTTreeItemAlreadyExistsError(f"중복된 아이템 ID: {item_id}")

        actual_parent_id = parent_id
        if parent_id is None:
            actual_parent_id = self._tree._root_id

        if actual_parent_id is not None and actual_parent_id not in self._tree._items:
            raise exc.MTTreeItemNotFoundError(f"존재하지 않는 부모 아이템 ID: {actual_parent_id}")
        
        item.set_property("parent_id", actual_parent_id)
        self._tree._items[item_id] = item

        if actual_parent_id is not None:
            parent = self._tree._items[actual_parent_id]
            children_ids = parent.get_property("children_ids", [])
            if item_id not in children_ids:
                children_ids.append(item_id)
            parent.set_property("children_ids", children_ids)

        self._tree._notify(MTTreeEvent.ITEM_ADDED, {"item_id": item_id, "parent_id": actual_parent_id})
        return True

    def remove_item(self, item_id: str) -> bool:
        if item_id == self._tree._root_id:
            raise exc.MTTreeError("더미 루트 아이템은 삭제할 수 없습니다.")
        if item_id not in self._tree._items:
            raise exc.MTTreeItemNotFoundError(f"존재하지 않는 아이템 ID: {item_id}")
        
        item_to_remove = self._tree._items[item_id]
        parent_id = item_to_remove.get_property("parent_id")

        if parent_id is not None and parent_id in self._tree._items:
            parent = self._tree._items[parent_id]
            parent_children_ids = parent.get_property("children_ids", [])
            if item_id in parent_children_ids:
                parent_children_ids.remove(item_id)
                parent.set_property("children_ids", parent_children_ids)
        
        children_to_remove_recursively = [child.id for child in self.get_children_for_modification(item_id)]
        
        self._tree._items.pop(item_id)
        
        for child_id in children_to_remove_recursively:
            if child_id in self._tree._items:
                self.remove_item(child_id)
                
        self._tree._notify(MTTreeEvent.ITEM_REMOVED, {"item_id": item_id, "parent_id": parent_id})
        return True

    def get_children_for_modification(self, parent_id: str | None) -> List[IMTTreeItem]:
        if parent_id is None or parent_id not in self._tree._items:
            return []
        parent_item = self._tree._items[parent_id]
        children_ids = parent_item.get_property("children_ids", [])
        children_items: List[IMTTreeItem] = []
        for child_id in children_ids:
            child = self._tree._items.get(child_id)
            if child:
                children_items.append(child)
        return children_items

    def move_item(self, item_id: str, new_parent_id_request: str | None) -> bool:
        if item_id == self._tree._root_id:
            raise exc.MTTreeError("더미 루트 아이템은 이동할 수 없습니다.")
        if item_id not in self._tree._items:
            raise exc.MTTreeItemNotFoundError(f"존재하지 않는 아이템 ID: {item_id}")

        actual_new_parent_id = new_parent_id_request
        if new_parent_id_request is None:
            actual_new_parent_id = self._tree._root_id

        if actual_new_parent_id is not None and actual_new_parent_id not in self._tree._items:
            raise exc.MTTreeItemNotFoundError(f"존재하지 않는 새 부모 아이템 ID: {actual_new_parent_id}")
        if actual_new_parent_id is not None and self._tree._is_descendant(item_id, actual_new_parent_id):
            raise exc.MTTreeError(f"순환 참조 발생: {item_id}는 {actual_new_parent_id}의 조상입니다.")
        
        item = self._tree._items[item_id]
        old_parent_id = item.get_property("parent_id")

        if old_parent_id == actual_new_parent_id:
            return False

        if old_parent_id is not None and old_parent_id in self._tree._items:
            old_parent = self._tree._items[old_parent_id]
            old_children = old_parent.get_property("children_ids", [])
            if item_id in old_children:
                old_children.remove(item_id)
            old_parent.set_property("children_ids", old_children)

        if actual_new_parent_id is not None:
            new_parent = self._tree._items[actual_new_parent_id]
            children_ids = new_parent.get_property("children_ids", [])
            if item_id not in children_ids:
                children_ids.append(item_id)
            new_parent.set_property("children_ids", children_ids)

        item.set_property("parent_id", actual_new_parent_id)

        self._tree._notify(MTTreeEvent.ITEM_MOVED, {
            "item_id": item_id,
            "new_parent_id": actual_new_parent_id,
            "old_parent_id": old_parent_id,
        })

        return True

    def modify_item(self, item_id: str, changes: Dict[str, Any]) -> bool:
        if item_id not in self._tree._items:
            raise exc.MTTreeItemNotFoundError(f"존재하지 않는 아이템 ID: {item_id}")
        item = self._tree._items[item_id]
        for key, value in changes.items():
            item.set_property(key, value)
        self._tree._notify(MTTreeEvent.ITEM_MODIFIED, {"item_id": item_id, "changes": changes})
        return True

    def reset_tree(self) -> None:
        self._tree._items = {}
        self._tree._root_id = None
        self._tree._notify(MTTreeEvent.TREE_RESET, {})

class _MTTreeTraversable:
    def __init__(self, tree):
        self._tree = tree

    def traverse(self, visitor: Callable[[IMTTreeItem], None], node_id: Optional[str] = None) -> None:
        if not self._tree._items:
            return
        start_id = node_id if node_id is not None else self._tree._root_id
        if start_id is None:
            return
        visited: Set[str] = set()
        queue: List[str] = [start_id]
        while queue:
            current_id = queue.pop(0)
            if current_id in visited:
                continue
            visited.add(current_id)
            current_item = self._tree._items.get(current_id)
            if current_item is not None:
                visitor(current_item)
                for child in self._tree.get_children(current_id):
                    queue.append(child.id)

# 직렬화 관련 포괄적 네이밍으로 변경
# IMTTreeDictSerializable, IMTTreeJSONSerializable 두 인터페이스를 모두 만족
class _MTTreeSerializable:
    def __init__(self, tree):
        self._tree = tree

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self._tree._id,
            "name": self._tree._name,
            "root_id": self._tree._root_id,
            "items": {item_id: self._item_to_dict(item) for item_id, item in self._tree._items.items()}
        }

    def _item_to_dict(self, item: IMTTreeItem) -> Dict[str, Any]:
        return {
            "id": item.id,
            "data": item.data
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> IMTTree:
        tree_id = data.get("id", "")
        tree_name = data.get("name", "")
        tree = MTTree(tree_id, tree_name)
        items_data = data.get("items", {})
        for item_id, item_data in items_data.items():
            item = MTTreeItem(item_id, item_data.get("data", {}))
            tree._items[item_id] = item
        tree._root_id = data.get("root_id")
        return tree

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2)

    @classmethod
    def from_json(cls, json_str: str) -> IMTTree:
        try:
            data = json.loads(json_str)
            return cls.from_dict(data)
        except Exception as e:
            print(f"JSON 파싱 실패: {e}")
            return MTTree("", "")

class _MTTreeCommon:
    def __init__(self, tree : "MTTree"):
        self._tree = tree

    def clone(self) -> "MTTree":
        return copy.deepcopy(self._tree)

# MTTree: 역할별 구현체를 컴포지션(위임)으로 합침
class MTTree:
    """매크로 트리 구현 클래스
    
    매크로 트리를 관리하고 조작하는 기능을 제공합니다.
    """
    DUMMY_ROOT_ID = "__MTTREE_DUMMY_ROOT__"
    
    def __init__(self, tree_id: str, name: str, event_manager: IMTTreeEventManager | None = None):
        """트리 초기화
        
        Args:
            tree_id: 트리 ID
            name: 트리 이름
            event_manager: 트리 이벤트 매니저 (선택적)
        """
        self._id = tree_id
        self._name = name
        self._items: Dict[str, IMTTreeItem] = {}
        
        dummy_root_data = {"name": "Dummy Root", "parent_id": None, "children_ids": [], "node_type": MTNodeType.GROUP}
        dummy_root_item = MTTreeItem(MTTree.DUMMY_ROOT_ID, dummy_root_data)
        self._items[MTTree.DUMMY_ROOT_ID] = dummy_root_item
        self._root_id: Optional[str] = MTTree.DUMMY_ROOT_ID
        
        self._event_manager = event_manager
        self._common = _MTTreeCommon(self)
        self._readable = _MTTreeReadable(self)
        self._modifiable = _MTTreeModifiable(self)
        self._traversable = _MTTreeTraversable(self)
        self._serializable = _MTTreeSerializable(self)
    
    @property
    def id(self) -> str:
        """트리 ID를 반환합니다."""
        return self._readable.id
    
    @property
    def name(self) -> str:
        """트리 이름을 반환합니다."""
        return self._readable.name
    
    @property
    def root_id(self) -> Optional[str]:
        """루트 아이템 ID를 반환합니다."""
        return self._readable.root_id
    
    @property
    def items(self) -> dict[str, IMTTreeItem]:
        return self._readable.items
    
    def get_item(self, item_id: str) -> IMTTreeItem | None:
        """ID로 아이템을 찾습니다."""
        return self._readable.get_item(item_id)
    
    def get_children(self, parent_id: str | None) -> List[IMTTreeItem]:
        """지정된 부모의 모든 자식 아이템을 반환합니다.
        
        Args:
            parent_id: 부모 아이템 ID (None이면 루트 아이템 반환)
            
        Returns:
            자식 아이템 목록
        """
        return self._readable.get_children(parent_id)
    
    def add_item(self, item: IMTTreeItem, parent_id: str | None = None) -> bool:
        """아이템을 트리에 추가합니다.
        
        Args:
            item: 추가할 아이템
            parent_id: 부모 아이템 ID (None이면 루트 아이템으로 추가)
            
        Returns:
            성공 여부
            
        Raises:
            ValueError: 아이템 ID가 이미 존재할 경우
        """
        return self._modifiable.add_item(item, parent_id)
    
    def remove_item(self, item_id: str) -> bool:
        """아이템을 트리에서 제거합니다.
        
        Args:
            item_id: 제거할 아이템 ID
            
        Returns:
            성공 여부
            
        Raises:
            ValueError: 존재하지 않는 아이템 ID일 경우
        """
        return self._modifiable.remove_item(item_id)
    
    def move_item(self, item_id: str, new_parent_id: Optional[str]) -> bool:
        """아이템을 새 부모로 이동합니다.
        
        Args:
            item_id: 이동할 아이템 ID
            new_parent_id: 새 부모 아이템 ID (None이면 루트 아이템으로 이동)
            
        Returns:
            성공 여부
            
        Raises:
            ValueError: 존재하지 않는 아이템 ID이거나 부모 ID일 경우
        """
        return self._modifiable.move_item(item_id, new_parent_id)
    
    def modify_item(self, item_id: str, changes: Dict[str, Any]) -> bool:
        """아이템 속성을 변경합니다.
        
        Args:
            item_id: 변경할 아이템 ID
            changes: 변경할 속성 (키-값 쌍)
            
        Returns:
            성공 여부
            
        Raises:
            ValueError: 존재하지 않는 아이템 ID일 경우
        """
        return self._modifiable.modify_item(item_id, changes)
    
    def reset_tree(self) -> None:
        """트리를 초기 상태로 리셋합니다."""
        self._modifiable.reset_tree()
    
    def traverse(self, visitor: Callable[[IMTTreeItem], None], 
                node_id: Optional[str] = None) -> None:
        """트리를 BFS로 순회하면서 각 아이템에 방문자 함수를 적용합니다.
        
        Args:
            visitor: 각 아이템에 적용할 함수
            node_id: 시작 노드 ID (None이면 루트부터 시작)
        """
        self._traversable.traverse(visitor, node_id)
    
    def clone(self) -> IMTTree:
        return self._common.clone()
    
    def _is_descendant(self, ancestor_id: str, descendant_id: str) -> bool:
        """descendant_id가 ancestor_id의 자손인지 확인합니다."""
        if ancestor_id == descendant_id:
            return True
        
        item = self._items.get(descendant_id)
        if item is None:
            return False
        
        parent_id = item.get_property("parent_id")
        if isinstance(parent_id, str):
            return self._is_descendant(ancestor_id, parent_id)
        else:
            return False
    
    def to_dict(self) -> Dict[str, Any]:
        """트리를 딕셔너리로 변환합니다."""
        return self._serializable.to_dict()
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> IMTTree:
        """딕셔너리에서 트리를 생성합니다."""
        return _MTTreeSerializable.from_dict(data)
    
    def to_json(self) -> str:
        """트리 구조를 JSON 문자열로 직렬화합니다.
        
        Returns:
            JSON 문자열
        """
        return self._serializable.to_json()
    
    @classmethod
    def from_json(cls, json_str: str) -> IMTTree:
        """JSON 문자열에서 트리 구조를 로드합니다."""
        return _MTTreeSerializable.from_json(json_str)

    def _notify(self, event_type, data):
        if self._event_manager:
            print(f"[CORE DEBUG] MTTree._notify: Publishing event {event_type} with data {data}")
            self._event_manager.notify(event_type, data)