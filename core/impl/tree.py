from typing import Any, Callable, Dict, Iterator, List, Optional, Set, TypeVar
import json

from core.interfaces.base_item import IMTTreeItem
from core.interfaces.base_tree import IMTTree
from core.impl.item import MTTreeItem

T = TypeVar('T', bound=IMTTreeItem)

class MTTree:
    """매크로 트리 구현 클래스
    
    매크로 트리를 관리하고 조작하는 기능을 제공합니다.
    """
    
    def __init__(self, tree_id: str, name: str):
        """트리 초기화
        
        Args:
            tree_id: 트리 ID
            name: 트리 이름
        """
        self._id = tree_id
        self._name = name
        self._items: Dict[str, IMTTreeItem] = {}
        self._root_id: Optional[str] = None
    
    @property
    def id(self) -> str:
        """트리 ID를 반환합니다."""
        return self._id
    
    @property
    def name(self) -> str:
        """트리 이름을 반환합니다."""
        return self._name
    
    @property
    def root_id(self) -> Optional[str]:
        """루트 아이템 ID를 반환합니다."""
        return self._root_id
    
    def get_all_items(self) -> Dict[str, IMTTreeItem]:
        """모든 아이템을 반환합니다."""
        return self._items.copy()
    
    def get_item(self, item_id: str) -> IMTTreeItem | None:
        """ID로 아이템을 찾습니다."""
        return self._items.get(item_id)
    
    def get_children(self, parent_id: str | None) -> List[IMTTreeItem]:
        """지정된 부모의 모든 자식 아이템을 반환합니다.
        
        Args:
            parent_id: 부모 아이템 ID (None이면 루트 아이템 반환)
            
        Returns:
            자식 아이템 목록
        """
        result = []
        for item in self._items.values():
            item_parent_id = item.get_property("parent_id")
            if (parent_id is None and item_parent_id is None) or \
               (parent_id is not None and item_parent_id == parent_id):
                result.append(item)
        return result
    
    def add_item(self, item: IMTTreeItem, parent_id: str | None) -> bool:
        """아이템을 트리에 추가합니다.
        
        Args:
            item: 추가할 아이템
            parent_id: 부모 아이템 ID (None이면 루트 아이템으로 추가)
            
        Returns:
            성공 여부
            
        Raises:
            ValueError: 아이템 ID가 이미 존재할 경우
        """
        item_id = item.id
        if item_id in self._items:
            raise ValueError(f"중복된 아이템 ID: {item_id}")
        
        # 부모 아이템 존재 여부 확인
        if parent_id is not None and parent_id not in self._items:
            raise ValueError(f"존재하지 않는 부모 아이템 ID: {parent_id}")
        
        # 루트 아이템이 없으면 루트로 설정
        if self._root_id is None and parent_id is None:
            self._root_id = item_id
        
        # 부모 ID 설정
        item.set_property("parent_id", parent_id)
        
        # 아이템 추가
        self._items[item_id] = item
        
        return True
    
    def remove_item(self, item_id: str) -> bool:
        """아이템을 트리에서 제거합니다.
        
        Args:
            item_id: 제거할 아이템 ID
            
        Returns:
            성공 여부
            
        Raises:
            ValueError: 존재하지 않는 아이템 ID일 경우
        """
        if item_id not in self._items:
            raise ValueError(f"존재하지 않는 아이템 ID: {item_id}")
        
        # 루트 아이템인 경우 루트 재설정
        if item_id == self._root_id:
            self._root_id = None
        
        # 자식 아이템들도 모두 제거
        children_to_remove = []
        for child in self.get_children(item_id):
            children_to_remove.append(child.id)
        
        # 아이템 제거
        removed_item = self._items.pop(item_id)
        
        # 자식 아이템 제거
        for child_id in children_to_remove:
            self.remove_item(child_id)
        
        return True
    
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
        if item_id not in self._items:
            raise ValueError(f"존재하지 않는 아이템 ID: {item_id}")
        
        if new_parent_id is not None and new_parent_id not in self._items:
            raise ValueError(f"존재하지 않는 부모 아이템 ID: {new_parent_id}")
        
        # 순환 참조 확인
        if new_parent_id is not None and self._is_descendant(item_id, new_parent_id):
            raise ValueError(f"순환 참조 발생: {item_id}는 {new_parent_id}의 조상입니다.")
        
        # 이전 부모
        item = self._items[item_id]
        old_parent_id = item.get_property("parent_id")
        
        # 동일한 부모로의 이동 무시
        if old_parent_id == new_parent_id:
            return False
        
        # 부모 변경
        item.set_property("parent_id", new_parent_id)
        
        # 이벤트 발생
        self._notify(MTTreeEvent.ITEM_MOVED, {
            "item_id": item_id,
            "old_parent_id": old_parent_id,
            "new_parent_id": new_parent_id
        })
        
        return True
    
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
        if item_id not in self._items:
            raise ValueError(f"존재하지 않는 아이템 ID: {item_id}")
        
        item = self._items[item_id]
        
        # 속성 변경
        for key, value in changes.items():
            item.set_property(key, value)
        
        # 이벤트 발생
        self._notify(MTTreeEvent.ITEM_MODIFIED, {"item_id": item_id, "changes": changes})
        
        return True
    
    def reset_tree(self) -> None:
        """트리를 초기 상태로 리셋합니다."""
        self._items = {}
        self._root_id = None
        
        # 이벤트 발생
        self._notify(MTTreeEvent.TREE_RESET, {})
    
    def traverse(self, visitor: Callable[[IMTTreeItem], None], 
                node_id: Optional[str] = None) -> None:
        """트리를 BFS로 순회하면서 각 아이템에 방문자 함수를 적용합니다.
        
        Args:
            visitor: 각 아이템에 적용할 함수
            node_id: 시작 노드 ID (None이면 루트부터 시작)
        """
        if not self._items:
            return
        
        # 시작 노드 ID가 없으면 루트부터 시작
        start_id = node_id if node_id is not None else self._root_id
        if start_id is None:
            return
        
        # BFS 순회
        visited: Set[str] = set()
        queue: List[str] = [start_id]
        
        while queue:
            current_id = queue.pop(0)
            
            if current_id in visited:
                continue
            
            # 방문 처리
            visited.add(current_id)
            current_item = self._items.get(current_id)
            
            if current_item is not None:
                # 방문자 함수 적용
                visitor(current_item)
                
                # 자식 노드 큐에 추가
                for child in self.get_children(current_id):
                    queue.append(child.id)
    
    def clone(self) -> 'MTTree':
        """트리의 복제본을 생성합니다."""
        new_tree = MTTree(self._id, self._name)
        
        # 아이템 복제
        for item_id, item in self._items.items():
            new_tree._items[item_id] = item.clone()
        
        # 루트 아이템 ID 복제
        new_tree._root_id = self._root_id
        
        # 이벤트 구독 정보는 복제하지 않음 (새 인스턴스에서 필요시 다시 구독)
        
        return new_tree
    
    def _is_descendant(self, ancestor_id: str, descendant_id: str) -> bool:
        """descendant_id가 ancestor_id의 자손인지 확인합니다."""
        if ancestor_id == descendant_id:
            return True
        
        item = self._items.get(descendant_id)
        if item is None:
            return False
        
        parent_id = item.get_property("parent_id")
        if parent_id is None:
            return False
        
        return self._is_descendant(ancestor_id, parent_id)
    
    def _item_to_dict(self, item: IMTTreeItem) -> Dict[str, Any]:
        """아이템을 딕셔너리로 변환합니다."""
        return {
            "id": item.id,
            "data": item.data
        }

    def to_dict(self) -> Dict[str, Any]:
            """트리를 딕셔너리로 변환합니다."""
            return {
                "id": self._id,
                "name": self._name,
                "root_id": self._root_id,
                "items": {item_id: self._item_to_dict(item) for item_id, item in self._items.items()}
            }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MTTree':
        """딕셔너리에서 트리를 생성합니다."""
        # 트리 생성
        tree_id = data.get("id", "")
        tree_name = data.get("name", "")
        tree = cls(tree_id, tree_name)
        
        # 아이템 복원
        items_data = data.get("items", {})
        for item_id, item_data in items_data.items():
            # 아이템 생성
            item = MTTreeItem(item_id, item_data.get("data", {}))
            # 아이템 추가 (부모 설정 없이)
            tree._items[item_id] = item
        
        # 루트 아이템 설정
        tree._root_id = data.get("root_id")
        
        return tree
    
    def to_json(self) -> str:
        """트리 구조를 JSON 문자열로 직렬화합니다.
        
        Returns:
            JSON 문자열
        """
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2)
    
 
    @classmethod
    def from_json(cls, json_str: str) -> IMTTree:
        """JSON 문자열에서 트리 구조를 로드합니다.
        
        Args:
            json_str: JSON 문자열
            
        Returns:
            Tree 인스턴스
        """
        try:
            data = json.loads(json_str)
            tree = cls()
            
            # 아이템 생성 및 추가
            items_data = data.get("items", {})
            
            # 먼저 모든 아이템 생성
            for item_id, item_dict in items_data.items():
                item_data = item_dict.get("data", {})
                name = item_data.get("name", "")
                item = IMTTreeItem(item_id, name)
                
                # 다른 속성 설정
                for key, value in item_data.items():
                    if key != "name":  # 이름은 이미 설정됨
                        item.set_property(key, value)
                
                # 아이템 추가 (부모 ID 없이)
                tree._items[item_id] = item
            
            # 부모-자식 관계 설정
            for item_id, item_dict in items_data.items():
                item_data = item_dict.get("data", {})
                parent_id = item_data.get("parent_id")
                if parent_id:
                    tree._items[item_id].set_property("parent_id", parent_id)
            
            # 루트 아이템 설정
            tree._root_id = data.get("root_id")
            
            return tree
        except Exception as e:
            print(f"JSON 파싱 실패: {e}")
            return cls()