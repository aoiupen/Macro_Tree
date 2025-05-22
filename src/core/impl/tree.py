from typing import Any, Callable, Dict, List, Set, cast # Optional removed
import json
import copy
import uuid

from core.interfaces.base_item import IMTTreeItem
from core.interfaces.base_tree import IMTTree
from core.impl.item import MTTreeItem
from model.events.interfaces.base_tree_event_mgr import MTTreeEvent, IMTTreeEventManager
import core.exceptions as exc
from core.interfaces.base_item_data import MTNodeType, MTItemDomainDTO, MTItemUIStateDTO, MTItemDTO

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

    def add_item(self, item_dto: MTItemDTO, parent_id: str | None = None, index: int = -1) -> str | None:
        """
        트리에 아이템을 추가합니다.
        Args:
            item_dto (MTItemDTO): 새 아이템 DTO
            parent_id (str | None): 부모 아이템 ID 또는 None(루트)
            index (int): 자식 목록에 삽입할 위치, -1이면 맨 뒤
        Returns:
            str | None: 생성된 아이템 ID 또는 실패 시 None
        Raises:
            MTTreeItemNotFoundError: 부모 아이템이 존재하지 않을 때
        """
        item_id = str(uuid.uuid4())
        domain_data = item_dto.domain_data
        ui_state_data = item_dto.ui_state_data
        new_item = MTTreeItem(item_id=item_id, domain_data=domain_data, ui_state_data=ui_state_data)
        actual_parent_id = parent_id
        if parent_id is None:
            actual_parent_id = self._tree._root_id
        if actual_parent_id is not None and actual_parent_id not in self._tree._items:
            return None
        new_item.set_property("parent_id", actual_parent_id)
        self._tree._items[item_id] = new_item
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
        new_stage = self._tree.to_dict()
        self._tree._notify(MTTreeEvent.TREE_CRUD, {"tree_data": new_stage})
        return item_id

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

    def modify_item(self, item_id: str, item_dto: MTItemDTO) -> bool:
        """
        아이템의 데이터를 수정합니다.
        Args:
            item_id (str): 수정할 아이템 ID
            item_dto (MTItemDTO): 새로운 아이템 데이터 DTO
        Returns:
            bool: 성공 여부
        Raises:
            MTTreeItemNotFoundError: 아이템이 존재하지 않을 때
        """
        if item_id not in self._tree._items:
            raise exc.MTTreeItemNotFoundError(f"존재하지 않는 아이템 ID: {item_id}")

        item = self._tree._items[item_id]
        
        item.data = item_dto.domain_data
        item.ui_state = item_dto.ui_state_data
        
        self._tree._notify(MTTreeEvent.ITEM_MODIFIED, {"item_id": item_id, "changes": item_dto.to_dict()})
        
        new_stage = self._tree.to_dict()
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

    def traverse(self, visitor: Callable[[IMTTreeItem], None], node_id: str | None = None) -> None:
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
        result = {
            "id": self._tree_ref.id,
            "name": self._tree_ref.name,
            "root_id": self._tree_ref.root_id,
            "items": {item_id: self.item_to_dict(item) for item_id, item in self._tree_ref._items.items()}
        }
        return result

    def item_to_dict(self, item: IMTTreeItem) -> Dict[str, Any]:
        """
        아이템을 딕셔너리로 변환합니다.
        Args:
            item (IMTTreeItem): 변환할 아이템
        Returns:
            Dict[str, Any]: 아이템 딕셔너리
        """
        return {
            "id": item.id,
            "data": item.data.to_dict() if hasattr(item.data, 'to_dict') else item.data
        }

    @staticmethod
    def dict_to_item(item_id_from_key: str, item_snapshot_dict_value: Dict[str, Any]) -> IMTTreeItem:
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

    def dict_to_state(self, data: Dict[str, Any]) -> None:
        """
        주어진 데이터로 MTTree 인스턴스의 상태를 복원합니다.
        Args:
            data (Dict[str, Any]): 복원할 트리 데이터
        """
        if not isinstance(data, dict):
            if hasattr(data, 'to_dict') and callable(data.to_dict):
                data = data.to_dict()
            else:
                raise TypeError(f"dict_to_state: Expected dict, got {type(data)}")
        self._tree_ref._items.clear()
        self._tree_ref._name = data.get("name", self._tree_ref._name)
        items_data = data.get("items", {})
        for item_id, item_snapshot_value in items_data.items():
            item = _MTTreeSerializable.dict_to_item(item_id, item_snapshot_value)
            self._tree_ref._items[item_id] = item
        self._tree_ref._root_id = data.get("root_id")

    @classmethod
    def dict_to_tree(cls, data: Dict[str, Any], event_manager: IMTTreeEventManager | None = None) -> IMTTree:
        tree_id = data.get("id", "")
        tree_name = data.get("name", "")
        new_tree = MTTree(tree_id, tree_name, event_manager)
        if new_tree._serializable:
            new_tree._serializable.dict_to_state(data)
        else:
            new_tree._items.clear()
            new_tree._name = data.get("name", new_tree._name)
            items_data_fallback = data.get("items", {})
            for item_id_fb, item_snapshot_value_fb in items_data_fallback.items():
                item_fb = _MTTreeSerializable.dict_to_item(item_id_fb, item_snapshot_value_fb)
                new_tree._items[item_id_fb] = item_fb
            new_tree._root_id = data.get("root_id")
        return new_tree

    def tree_to_json(self) -> str:
        """
        현재 트리 인스턴스의 상태를 JSON 문자열로 직렬화합니다.
        Returns:
            str: JSON 문자열
        """
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2)

    @classmethod
    def json_to_tree(cls, json_str: str, event_manager: IMTTreeEventManager | None = None) -> IMTTree:
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
            return cls.dict_to_tree(data, event_manager)
        except json.JSONDecodeError as e:
            print(f"JSON 파싱 실패: {e}") # This print statement seems like an original, potentially useful debug log.
            return MTTree("", "Error Tree", event_manager)

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
        # 여기서는 event_manager=None을 전달하여 복제본을 기본적으로 독립적으로 만듭니다.
        cloned_tree_data = self._tree.to_dict() # 현재 상태를 dict로
        cloned_tree = MTTree.from_dict(cloned_tree_data, event_manager=None) # Pass event_manager=None
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
        self._root_id: str | None = MTTree.DUMMY_ROOT_ID
        
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
    def root_id(self) -> str | None:
        """
        루트 아이템의 ID를 반환합니다.
        Returns:
            str | None: 루트 아이템 ID
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
    
    def add_item(self, item_dto: MTItemDTO, parent_id: str | None = None, index: int = -1) -> str | None:
        """
        트리에 아이템을 추가합니다.
        Args:
            item_dto (MTItemDTO): 새 아이템 DTO
            parent_id (str | None): 부모 아이템 ID 또는 None(루트)
            index (int): 자식 목록에 삽입할 위치, -1이면 맨 뒤
        Returns:
            str | None: 생성된 아이템 ID 또는 실패 시 None
        Raises:
            MTTreeItemNotFoundError: 부모 아이템이 존재하지 않을 때
        """
        return self._modifiable.add_item(item_dto=item_dto, parent_id=parent_id, index=index)
    
    
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
        아이템을 트리 내 다른 위치로 이동합니다.
        Args:
            item_id (str): 이동할 아이템의 ID.
            new_parent_id (str | None, optional): 새 부모 아이템의 ID. 루트로 이동하려면 None. 기본값은 None.
            new_index (int, optional): 새 부모의 자식 목록 내 위치. 기본값은 -1 (맨 뒤).
        Returns:
            bool: 이동 성공 시 True, 그렇지 않으면 False.
        """
        return self._modifiable.move_item(item_id, new_parent_id, new_index)
    
    def modify_item(self, item_id: str, item_dto: MTItemDTO) -> bool:
        """
        지정된 ID를 가진 아이템의 데이터를 수정합니다.
        Args:
            item_id (str): 수정할 아이템의 ID.
            item_dto (MTItemDTO): 새로운 아이템 데이터 DTO.
        Returns:
            bool: 수정 성공 시 True, 그렇지 않으면 False.
        """
        return self._modifiable.modify_item(item_id, item_dto)
    
    def reset_tree(self) -> None:
        """
        트리의 모든 아이템을 삭제하고 초기화합니다.
        """
        self._modifiable.reset_tree()
    
    def traverse(self, visitor: Callable[[IMTTreeItem], None], 
                node_id: str | None = None) -> None:
        """
        BFS 방식으로 트리를 순회하며 각 아이템에 방문자 함수를 적용합니다.
        Args:
            visitor (Callable[[IMTTreeItem], None]): 방문자 함수
            node_id (str | None): 시작 노드 ID(선택)
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
        tree = _MTTreeSerializable.dict_to_tree(data, event_manager)
        return tree
    
    def tree_to_json(self) -> str:
        """
        트리 구조를 JSON 문자열로 직렬화하여 반환합니다.
        Returns:
            str: JSON 문자열
        """
        return self._serializable.tree_to_json()
    
    @classmethod
    def json_to_tree(cls, json_str: str, event_manager: IMTTreeEventManager | None = None) -> IMTTree:
        """
        JSON 문자열에서 새로운 MTTree 인스턴스를 생성하여 반환합니다.
        Args:
            json_str (str): 트리 데이터 JSON 문자열
            event_manager (IMTTreeEventManager | None): 이벤트 매니저(선택)
        Returns:
            IMTTree: 생성된 트리 인스턴스
        """
        data = json.loads(json_str) # Allow json.JSONDecodeError to propagate
        return _MTTreeSerializable.dict_to_tree(data, event_manager)

    def dict_to_state(self, data: Dict[str, Any]) -> None:
        """
        주어진 데이터로 트리의 상태를 복원합니다.
        Args:
            data (Dict[str, Any]): 복원할 트리 데이터
        """
        self._serializable.dict_to_state(data)

    def _notify(self, event_type, data):
        """
        이벤트 매니저를 통해 이벤트를 알립니다.
        Args:
            event_type: 이벤트 타입
            data: 이벤트 데이터
        """
        if self._event_manager:
            self._event_manager.notify(event_type, data)