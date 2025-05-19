"""
이 모듈은 매크로 트리의 핵심 구현을 제공합니다.
트리의 읽기, 수정, 순회, 직렬화, 복제 등 모든 기능을 담당하는 클래스와 메서드를 포함합니다.
"""
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
    """
    트리의 읽기 전용 인터페이스를 제공하는 내부 클래스입니다.
    트리의 ID, 이름, 루트, 아이템 조회, 자식 아이템 조회 기능을 제공합니다.
    """
    def __init__(self, tree: "MTTree"):
        """
        MTTree 인스턴스를 받아 읽기 전용 속성에 접근할 수 있도록 초기화합니다.
        Args:
            tree (MTTree): 참조할 트리 인스턴스
        """
        self._tree = tree

    @property
    def id(self) -> str:
        """
        트리의 고유 ID를 반환합니다.
        Returns:
            str: 트리 ID
        """
        return self._tree._id

    @property
    def name(self) -> str:
        """
        트리의 이름을 반환합니다.
        Returns:
            str: 트리 이름
        """
        return self._tree._name

    @property
    def root_id(self) -> str | None:
        """
        트리의 루트 아이템 ID를 반환합니다.
        Returns:
            str | None: 루트 아이템 ID 또는 None
        """
        return self._tree._root_id

    @property
    def items(self) -> dict[str, IMTTreeItem]:
        """
        트리의 모든 아이템을 딕셔너리 형태로 반환합니다.
        Returns:
            dict[str, IMTTreeItem]: 아이템 딕셔너리
        """
        return self._tree._items
    
    def get_item(self, item_id: str) -> IMTTreeItem | None:
        """
        주어진 ID에 해당하는 아이템을 반환합니다.
        Args:
            item_id (str): 조회할 아이템의 ID
        Returns:
            IMTTreeItem | None: 해당 아이템 또는 None
        """
        return self._tree._items.get(item_id)

    def get_children(self, parent_id: str | None) -> List[IMTTreeItem]:
        """
        주어진 부모 ID의 자식 아이템 목록을 반환합니다.
        Args:
            parent_id (str | None): 부모 아이템의 ID 또는 None(루트)
        Returns:
            List[IMTTreeItem]: 자식 아이템 리스트
        """
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
    """
    트리의 수정(추가, 삭제, 이동, 수정, 리셋) 기능을 제공하는 내부 클래스입니다.
    """
    def __init__(self, tree: "MTTree"):
        """
        MTTree 인스턴스를 받아 수정 기능에 접근할 수 있도록 초기화합니다.
        Args:
            tree (MTTree): 참조할 트리 인스턴스
        """
        self._tree = tree

    def add_item(self, item: IMTTreeItem, parent_id: str | None, index: int = -1) -> bool:
        """
        트리에 아이템을 추가합니다.
        Args:
            item (IMTTreeItem): 추가할 아이템
            parent_id (str | None): 부모 아이템 ID 또는 None(루트)
            index (int): 자식 목록에 삽입할 위치, -1이면 맨 뒤
        Returns:
            bool: 성공 여부
        Raises:
            MTTreeItemAlreadyExistsError: 중복된 아이템 ID
            MTTreeItemNotFoundError: 부모 아이템이 존재하지 않을 때
        """
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
                if index == -1 or index >= len(children_ids):
                    children_ids.append(item_id)
                else:
                    children_ids.insert(index, item_id)
            parent.set_property("children_ids", children_ids)

        self._tree._notify(MTTreeEvent.ITEM_ADDED, {"item_id": item_id, "parent_id": actual_parent_id})

        new_stage = self._tree.to_dict() # MTTree 인스턴스에서 전체 데이터를 가져옴
        self._tree._notify(MTTreeEvent.TREE_CRUD, {"tree_data": new_stage}) 

        return True

    def remove_item(self, item_id: str) -> bool:
        """
        트리에서 아이템을 삭제합니다. 자식도 재귀적으로 삭제됩니다.
        Args:
            item_id (str): 삭제할 아이템 ID
        Returns:
            bool: 성공 여부
        Raises:
            MTTreeError: 루트 아이템 삭제 시
            MTTreeItemNotFoundError: 아이템이 존재하지 않을 때
        """
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

        new_stage = self._tree.to_dict() # MTTree 인스턴스에서 전체 데이터를 가져옴
        self._tree._notify(MTTreeEvent.TREE_CRUD, {"tree_data": new_stage}) 
        return True

    def get_children_for_modification(self, parent_id: str | None) -> List[IMTTreeItem]:
        """
        수정 목적으로 부모 ID의 자식 아이템 목록을 반환합니다.
        Args:
            parent_id (str | None): 부모 아이템 ID
        Returns:
            List[IMTTreeItem]: 자식 아이템 리스트
        """
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

    def move_item(self, item_id: str, new_parent_id_request: str | None, new_index: int = -1) -> bool:
        """
        아이템을 새로운 부모 아래로 이동합니다.
        Args:
            item_id (str): 이동할 아이템 ID
            new_parent_id_request (str | None): 새 부모 ID 또는 None(루트)
            new_index (int): 새 부모의 자식 목록에서 위치, -1이면 맨 뒤
        Returns:
            bool: 성공 여부
        Raises:
            MTTreeError: 루트 이동 시, 순환 참조 발생 시
            MTTreeItemNotFoundError: 아이템/부모가 존재하지 않을 때
        """
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

        if old_parent_id == actual_new_parent_id and new_index != -1:
            parent = self._tree._items[actual_new_parent_id]
            children_ids = parent.get_property("children_ids", [])
            if item_id in children_ids:
                children_ids.remove(item_id)
                if new_index >= len(children_ids):
                    children_ids.append(item_id)
                else:
                    children_ids.insert(new_index, item_id)
                parent.set_property("children_ids", children_ids)
                item.set_property("parent_id", actual_new_parent_id)
                self._tree._notify(MTTreeEvent.ITEM_MOVED, {
                    "item_id": item_id,
                    "new_parent_id": actual_new_parent_id,
                    "old_parent_id": old_parent_id,
                    "new_index": new_index
                })
                return True
            else:
                pass

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
                if new_index == -1 or new_index >= len(children_ids):
                    children_ids.append(item_id)
                else:
                    children_ids.insert(new_index, item_id)
            new_parent.set_property("children_ids", children_ids)

        item.set_property("parent_id", actual_new_parent_id)

        self._tree._notify(MTTreeEvent.ITEM_MOVED, {
            "item_id": item_id,
            "new_parent_id": actual_new_parent_id,
            "old_parent_id": old_parent_id,
            "new_index": new_index
        })

        new_stage = self._tree.to_dict() # MTTree 인스턴스에서 전체 데이터를 가져옴
        self._tree._notify(MTTreeEvent.TREE_CRUD, {"tree_data": new_stage}) 

        return True

    def modify_item(self, item_id: str, changes: Dict[str, Any]) -> bool:
        """
        아이템의 속성을 수정합니다.
        Args:
            item_id (str): 수정할 아이템 ID
            changes (Dict[str, Any]): 변경할 속성 딕셔너리
        Returns:
            bool: 성공 여부
        Raises:
            MTTreeItemNotFoundError: 아이템이 존재하지 않을 때
        """
        if item_id not in self._tree._items:
            raise exc.MTTreeItemNotFoundError(f"존재하지 않는 아이템 ID: {item_id}")
        item = self._tree._items[item_id]
        for key, value in changes.items():
            item.set_property(key, value)
        self._tree._notify(MTTreeEvent.ITEM_MODIFIED, {"item_id": item_id, "changes": changes})

        new_stage = self._tree.to_dict() # MTTree 인스턴스에서 전체 데이터를 가져옴
        self._tree._notify(MTTreeEvent.TREE_CRUD, {"tree_data": new_stage}) 
        return True

    def reset_tree(self) -> None:
        """
        트리의 모든 아이템을 삭제하고 초기화합니다.
        """
        self._tree._items = {}
        self._tree._root_id = None
        self._tree._notify(MTTreeEvent.TREE_RESET, {})

        new_stage = self._tree.to_dict() # MTTree 인스턴스에서 전체 데이터를 가져옴
        self._tree._notify(MTTreeEvent.TREE_CRUD, {"tree_data": new_stage}) 

class _MTTreeTraversable:
    """
    트리의 순회 기능을 제공하는 내부 클래스입니다.
    """
    def __init__(self, tree):
        """
        MTTree 인스턴스를 받아 순회 기능에 접근할 수 있도록 초기화합니다.
        Args:
            tree (MTTree): 참조할 트리 인스턴스
        """
        self._tree = tree

    def traverse(self, visitor: Callable[[IMTTreeItem], None], node_id: Optional[str] = None) -> None:
        """
        BFS 방식으로 트리를 순회하며 각 노드에 visitor 함수를 적용합니다.
        Args:
            visitor (Callable[[IMTTreeItem], None]): 각 노드에 적용할 함수
            node_id (Optional[str]): 시작 노드 ID, None이면 루트부터
        """
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
    """
    트리의 직렬화/역직렬화 기능을 제공하는 내부 클래스입니다.
    딕셔너리 및 JSON 변환, 복원 기능을 포함합니다.
    """
    def __init__(self, tree_ref: "MTTree"):
        """
        MTTree 인스턴스를 받아 직렬화 기능에 접근할 수 있도록 초기화합니다.
        Args:
            tree_ref (MTTree): 참조할 트리 인스턴스
        """
        self._tree_ref = tree_ref

    def to_dict(self) -> Dict[str, Any]:
        """
        트리의 현재 상태를 딕셔너리로 반환합니다.
        Returns:
            Dict[str, Any]: 트리 상태 딕셔너리
        """
        return {
            "id": self._tree_ref.id, # 프로퍼티를 통해 접근
            "name": self._tree_ref.name, # 프로퍼티를 통해 접근
            "root_id": self._tree_ref.root_id, # 프로퍼티를 통해 접근
            "items": {item_id: self._item_to_dict(item) for item_id, item in self._tree_ref._items.items()} # _items는 직접 접근
        }

    def _item_to_dict(self, item: IMTTreeItem) -> Dict[str, Any]:
        """
        아이템을 딕셔너리로 변환합니다.
        Args:
            item (IMTTreeItem): 변환할 아이템
        Returns:
            Dict[str, Any]: 아이템 딕셔너리
        """
        return {
            "id": item.id,
            "data": item.data # MTTreeItemData 객체 또는 그것의 dict 표현
        }

    @staticmethod
    def _create_item_from_snapshot_data(item_id_from_key: str, item_snapshot_dict_value: Dict[str, Any]) -> IMTTreeItem:
        """
        아이템 ID와 스냅샷 데이터로 MTTreeItem 객체를 생성합니다.
        Args:
            item_id_from_key (str): 아이템 ID
            item_snapshot_dict_value (Dict[str, Any]): 아이템 스냅샷 데이터
        Returns:
            IMTTreeItem: 생성된 아이템 객체
        """
        actual_item_properties = item_snapshot_dict_value.get("data", {})
        return MTTreeItem(item_id_from_key, actual_item_properties)

    def restore_instance_state_from_dict(self, data: Dict[str, Any]) -> None:
        """
        주어진 데이터로 MTTree 인스턴스의 상태를 복원합니다.
        Args:
            data (Dict[str, Any]): 복원할 트리 데이터
        """
        # data가 dict가 아니면 dict로 변환 시도
        if not isinstance(data, dict):
            # MTTree 객체라면 to_dict()로 변환
            if hasattr(data, 'to_dict') and callable(data.to_dict):
                data = data.to_dict()
            else:
                raise TypeError(f"restore_instance_state_from_dict: Expected dict, got {type(data)}")
        
        self._tree_ref._items.clear() # MTTree의 내부 아이템 직접 클리어
        # MTTree의 내부 이름 직접 업데이트, ID는 변경하지 않음
        self._tree_ref._name = data.get("name", self._tree_ref._name)  
        
        items_data = data.get("items", {})
        for item_id, item_snapshot_value in items_data.items():
            # 더미 루트 아이템은 스냅샷에 의해 덮어쓰이지 않도록 하거나,
            # 스냅샷에 더미 루트가 항상 포함되고 올바른 타입으로 저장되도록 보장해야 함.
            # 현재는 모든 아이템을 스냅샷 기준으로 덮어쓰므로, 스냅샷에 더미루트가 없다면 사라질 수 있음.
            # 또는, 더미 루트는 restore 로직에서 별도로 유지하고, 나머지 아이템만 처리.
            # 여기서는 스냅샷이 완전한 상태를 나타낸다고 가정.
            item = _MTTreeSerializable._create_item_from_snapshot_data(item_id, item_snapshot_value)
            self._tree_ref._items[item_id] = item # MTTree의 내부 아이템 직접 추가
            
        self._tree_ref._root_id = data.get("root_id") # MTTree의 내부 루트 ID 직접 업데이트

    @classmethod
    def create_new_tree_from_dict(cls, data: Dict[str, Any], event_manager: IMTTreeEventManager | None = None) -> IMTTree:
        """
        딕셔너리 데이터로부터 새로운 MTTree 인스턴스를 생성합니다.
        Args:
            data (Dict[str, Any]): 트리 데이터
            event_manager (IMTTreeEventManager | None): 이벤트 매니저
        Returns:
            IMTTree: 생성된 트리 인스턴스
        """
        tree_id = data.get("id", "")
        tree_name = data.get("name", "")
        
        # 새 MTTree 인스턴스 생성. 이 때 MTTree.__init__ 내에서 _MTTreeSerializable(self)가 호출됨.
        new_tree = MTTree(tree_id, tree_name, event_manager)
        
        # MTTree의 _serializable 인스턴스를 통해 상태 복원 메서드 호출
        # 단, 이때 new_tree의 _serializable은 new_tree 자신을 참조하므로,
        # _MTTreeSerializable의 restore_instance_state_from_dict 메서드를 사용하면 됨.
        # Dummy root는 MTTree 생성자에서 이미 생성되므로, restore_instance_state_from_dict에서
        # items를 clear하고 다시 채울 때, 스냅샷에 더미 루트 정보가 없다면 문제가 될 수 있다.
        # 가장 안전한 방법은, MTTree 생성 시 더미루트를 만들고,
        # restore_instance_state_from_dict는 더미루트를 제외한 사용자 아이템만 복원하거나,
        # 스냅샷 자체가 더미루트를 포함하고 있어야 한다.
        # 현재 MTTree 생성자에서 더미 루트를 만들고, root_id로 설정.
        # to_dict도 더미루트를 포함하므로, from_dict도 더미루트 포함된 스냅샷으로 복원 가능.

        # 새 트리의 serializable 객체를 통해 상태를 직접 복원
        if new_tree._serializable: # _serializable이 초기화 되었는지 확인 (실제로는 __init__에서 항상 초기화됨)
            new_tree._serializable.restore_instance_state_from_dict(data)
        else: # 이 경우는 발생하지 않아야 함
            # Fallback: 직접 상태 설정 (위의 restore_instance_state_from_dict 로직과 유사하게)
            new_tree._items.clear()
            new_tree._name = data.get("name", new_tree._name)
            items_data_fallback = data.get("items", {})
            for item_id_fb, item_snapshot_value_fb in items_data_fallback.items():
                item_fb = _MTTreeSerializable._create_item_from_snapshot_data(item_id_fb, item_snapshot_value_fb)
                new_tree._items[item_id_fb] = item_fb
            new_tree._root_id = data.get("root_id")
            # 더미 루트가 items_data_fallback에 없다면, MTTree 생성자에서 만든 더미루트가 유지됨.
            # 만약 items_data_fallback에 더미루트가 있고, 그것으로 덮어쓰고 싶다면,
            # MTTree 생성자에서 더미루트를 만들지 않거나, 여기서 덮어쓰도록 해야 함.
            # 현재 구조에서는 MTTree 생성자에서 더미루트를 만들고, to_dict/from_dict 스냅샷에 더미루트가 포함됨.

        return new_tree

    def to_json_string(self) -> str:
        """
        현재 트리 인스턴스의 상태를 JSON 문자열로 직렬화합니다.
        Returns:
            str: JSON 문자열
        """
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2)

    @classmethod
    def create_new_tree_from_json_string(cls, json_str: str, event_manager: IMTTreeEventManager | None = None) -> IMTTree:
        """
        JSON 문자열로부터 새로운 MTTree 인스턴스를 생성합니다.
        Args:
            json_str (str): 트리 데이터 JSON 문자열
            event_manager (IMTTreeEventManager | None): 이벤트 매니저
        Returns:
            IMTTree: 생성된 트리 인스턴스
        """
        try:
            data = json.loads(json_str)
            return cls.create_new_tree_from_dict(data, event_manager)
        except json.JSONDecodeError as e:
            print(f"JSON 파싱 실패: {e}")
            # 예외 발생 또는 기본 빈 트리 반환
            return MTTree("", "Error Tree", event_manager) # ID, 이름, 이벤트 매니저 전달

class _MTTreeCommon:
    """
    트리의 복제(clone) 기능을 제공하는 내부 클래스입니다.
    """
    def __init__(self, tree : "MTTree"):
        """
        MTTree 인스턴스를 받아 복제 기능에 접근할 수 있도록 초기화합니다.
        Args:
            tree (MTTree): 참조할 트리 인스턴스
        """
        self._tree = tree

    def clone(self) -> "MTTree":
        """
        트리의 현재 상태를 복제하여 새로운 MTTree 인스턴스를 반환합니다.
        Returns:
            MTTree: 복제된 트리 인스턴스
        """
        # 현재 clone 메서드는 copy.deepcopy(self._tree)를 사용함.
        # 이는 _event_manager도 복사하려고 시도할 수 있음.
        # 만약 event_manager가 deepcopy 불가능한 객체라면 문제가 될 수 있음.
        # 가장 안전한 방법은 to_dict()로 상태를 가져오고, from_dict()로 새 객체를 만드는 것.
        # 이 때, event_manager는 clone된 객체에 어떻게 전달할 것인가? 원본의 것을 그대로 사용할 것인가, 아니면 None으로 할 것인가?
        # 여기서는 원본의 event_manager를 그대로 사용한다고 가정.
        cloned_tree_data = self._tree.to_dict() # 현재 상태를 dict로
        cloned_tree = MTTree.from_dict(cloned_tree_data, event_manager=self._tree._event_manager)
        return cloned_tree

# MTTree: 역할별 구현체를 컴포지션(위임)으로 합침
class MTTree:
    """
    매크로 트리를 관리하고 조작하는 기능을 제공하는 구현 클래스입니다.
    트리의 아이템 추가/삭제/이동/수정, 순회, 직렬화, 복제 등 모든 핵심 기능을 제공합니다.
    """
    DUMMY_ROOT_ID = "__MTTREE_DUMMY_ROOT__"
    
    def __init__(self, tree_id: str, name: str, event_manager: IMTTreeEventManager | None = None):
        """
        트리 ID, 이름, 선택적 이벤트 매니저로 MTTree를 초기화합니다.
        Args:
            tree_id (str): 트리의 고유 ID
            name (str): 트리 이름
            event_manager (IMTTreeEventManager | None): 이벤트 매니저(선택)
        """
        self._id = tree_id
        self._name = name
        self._items: Dict[str, IMTTreeItem] = {}
        self._event_manager = event_manager # 이벤트 매니저 저장
        
        # _serializable 인스턴스 생성 시 self (MTTree 인스턴스 자신)를 전달
        self._serializable = _MTTreeSerializable(self)
        
        dummy_root_data = {"name": "Dummy Root", "parent_id": None, "children_ids": [], "node_type": MTNodeType.GROUP}
        # 더미 루트 아이템 생성 시 ID를 사용하고, 실제 data는 MTTreeItem 내부에서 관리.
        # MTTreeItem 생성자는 (id, data_dict)를 받음.
        dummy_root_item = MTTreeItem(MTTree.DUMMY_ROOT_ID, dummy_root_data)
        self._items[MTTree.DUMMY_ROOT_ID] = dummy_root_item
        self._root_id: Optional[str] = MTTree.DUMMY_ROOT_ID
        
        self._common = _MTTreeCommon(self)
        self._readable = _MTTreeReadable(self)
        self._modifiable = _MTTreeModifiable(self)
        self._traversable = _MTTreeTraversable(self)
        # self._serializable = _MTTreeSerializable(self) # 위에서 먼저 초기화
    
    @property
    def id(self) -> str:
        """
        트리의 고유 ID를 반환합니다.
        Returns:
            str: 트리 ID
        """
        return self._readable.id
    
    @property
    def name(self) -> str:
        """
        트리의 이름을 반환합니다.
        Returns:
            str: 트리 이름
        """
        return self._readable.name
    
    @property
    def root_id(self) -> Optional[str]:
        """
        루트 아이템의 ID를 반환합니다.
        Returns:
            Optional[str]: 루트 아이템 ID
        """
        return self._readable.root_id
    
    @property
    def items(self) -> dict[str, IMTTreeItem]:
        """
        트리의 모든 아이템을 딕셔너리 형태로 반환합니다.
        Returns:
            dict[str, IMTTreeItem]: 아이템 딕셔너리
        """
        return self._readable.items
    
    def get_item(self, item_id: str) -> IMTTreeItem | None:
        """
        주어진 ID에 해당하는 아이템을 반환합니다.
        Args:
            item_id (str): 조회할 아이템의 ID
        Returns:
            IMTTreeItem | None: 해당 아이템 또는 None
        """
        return self._readable.get_item(item_id)
    
    def get_children(self, parent_id: str | None) -> List[IMTTreeItem]:
        """
        주어진 부모 ID의 자식 아이템 목록을 반환합니다.
        Args:
            parent_id (str | None): 부모 아이템의 ID 또는 None(루트)
        Returns:
            List[IMTTreeItem]: 자식 아이템 리스트
        """
        return self._readable.get_children(parent_id)
    
    def add_item(self, item: IMTTreeItem, parent_id: str | None = None, index: int = -1) -> bool:
        """
        트리에 아이템을 추가합니다.
        Args:
            item (IMTTreeItem): 추가할 아이템
            parent_id (str | None): 부모 아이템 ID 또는 None(루트)
            index (int): 자식 목록에 삽입할 위치, -1이면 맨 뒤
        Returns:
            bool: 성공 여부
        """
        return self._modifiable.add_item(item, parent_id, index)
    
    
    def remove_item(self, item_id: str) -> bool:
        """
        트리에서 아이템을 삭제합니다. 자식도 재귀적으로 삭제됩니다.
        Args:
            item_id (str): 삭제할 아이템 ID
        Returns:
            bool: 성공 여부
        """
        return self._modifiable.remove_item(item_id)
    
    def move_item(self, item_id: str, new_parent_id: str | None = None, new_index: int = -1) -> bool:
        """
        아이템을 새로운 부모로 이동합니다.
        Args:
            item_id (str): 이동할 아이템 ID
            new_parent_id (str | None): 새 부모 ID 또는 None(루트)
            new_index (int): 새 인덱스(선택)
        Returns:
            bool: 성공 여부
        """
        return self._modifiable.move_item(item_id, new_parent_id, new_index)
    
    def modify_item(self, item_id: str, changes: Dict[str, Any]) -> bool:
        """
        아이템의 속성을 수정합니다.
        Args:
            item_id (str): 수정할 아이템 ID
            changes (Dict[str, Any]): 변경할 속성 딕셔너리
        Returns:
            bool: 성공 여부
        """
        return self._modifiable.modify_item(item_id, changes)
    
    def reset_tree(self) -> None:
        """
        트리의 모든 아이템을 삭제하고 초기화합니다.
        """
        self._modifiable.reset_tree()
    
    def traverse(self, visitor: Callable[[IMTTreeItem], None], 
                node_id: Optional[str] = None) -> None:
        """
        BFS 방식으로 트리를 순회하며 각 아이템에 방문자 함수를 적용합니다.
        Args:
            visitor (Callable[[IMTTreeItem], None]): 방문자 함수
            node_id (Optional[str]): 시작 노드 ID(선택)
        """
        self._traversable.traverse(visitor, node_id)
    
    def clone(self) -> IMTTree:
        """
        트리의 복제본을 생성하여 반환합니다.
        Returns:
            IMTTree: 복제된 트리 인스턴스
        """
        return self._common.clone()
    
    def _is_descendant(self, ancestor_id: str, descendant_id: str) -> bool:
        """
        특정 아이템이 다른 아이템의 하위(자손)인지 확인합니다.
        Args:
            ancestor_id (str): 조상 아이템 ID
            descendant_id (str): 자손 아이템 ID
        Returns:
            bool: 자손 여부
        """
        current_id = descendant_id
        while current_id is not None:
            if current_id == ancestor_id:
            return True
            item = self._items.get(current_id)
        if item is None:
                break
            current_id = item.get_property("parent_id")
            return False
    
    def to_dict(self) -> Dict[str, Any]:
        """
        트리의 현재 상태를 딕셔너리로 반환합니다.
        Returns:
            Dict[str, Any]: 트리 상태 딕셔너리
        """
        return self._serializable.to_dict()
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any], event_manager: IMTTreeEventManager | None = None) -> IMTTree:
        """
        딕셔너리에서 새로운 MTTree 인스턴스를 생성하여 반환합니다.
        Args:
            data (Dict[str, Any]): 트리 데이터 딕셔너리
            event_manager (IMTTreeEventManager | None): 이벤트 매니저(선택)
        Returns:
            IMTTree: 생성된 트리 인스턴스
        """
        return _MTTreeSerializable.create_new_tree_from_dict(data, event_manager)
    
    def to_json(self) -> str:
        """
        트리 구조를 JSON 문자열로 직렬화하여 반환합니다.
        Returns:
            str: JSON 문자열
        """
        return self._serializable.to_json_string()
    
    @classmethod
    def from_json(cls, json_str: str, event_manager: IMTTreeEventManager | None = None) -> IMTTree:
        """
        JSON 문자열에서 새로운 MTTree 인스턴스를 생성하여 반환합니다.
        Args:
            json_str (str): 트리 데이터 JSON 문자열
            event_manager (IMTTreeEventManager | None): 이벤트 매니저(선택)
        Returns:
            IMTTree: 생성된 트리 인스턴스
        """
        return _MTTreeSerializable.create_new_tree_from_json_string(json_str, event_manager)

    # restore_from_dict는 이제 restore_state로 이름을 변경하고, _MTTreeSerializable에 위임
    def restore_state(self, data: Dict[str, Any]) -> None:
        """
        주어진 데이터로 트리의 상태를 복원합니다.
        Args:
            data (Dict[str, Any]): 복원할 트리 데이터
        """
        self._serializable.restore_instance_state_from_dict(data)

    def _notify(self, event_type, data):
        """
        이벤트 매니저를 통해 이벤트를 알립니다.
        Args:
            event_type: 이벤트 타입
            data: 이벤트 데이터
        """
        if self._event_manager:
            self._event_manager.notify(event_type, data)