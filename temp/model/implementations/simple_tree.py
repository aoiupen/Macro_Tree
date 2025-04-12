from typing import Dict, Optional, List, Any
import json
from .simple_tree_item import SimpleTreeItem

class SimpleTree:
    def __init__(self):
        self._items: Dict[str, SimpleTreeItem] = {}
    
    def add_item(self, item: SimpleTreeItem, parent_id: Optional[str] = None) -> bool:
        item_id = item.get_id()
        if item_id in self._items:
            return False
        
        self._items[item_id] = item
        if parent_id:
            item.set_property("parent_id", parent_id)
        return True
    
    def remove_item(self, item_id: str) -> bool:
        """
        아이템을 트리에서 제거합니다. 자식 아이템도 함께 제거됩니다.
        
        Args:
            item_id: 제거할 아이템의 ID
            
        Returns:
            성공 여부
        """
        if item_id not in self._items:
            return False
            
        # 자식 아이템 찾기
        children_ids = []
        for child_id, child_item in self._items.items():
            if child_item.get_property("parent_id") == item_id:
                children_ids.append(child_id)
                
        # 자식 아이템 재귀적으로 제거
        for child_id in children_ids:
            self.remove_item(child_id)
            
        # 아이템 제거
        del self._items[item_id]
        return True
    
    def update_item(self, item_id: str, name: Optional[str] = None, parent_id: Optional[str] = None) -> bool:
        """
        아이템 속성을 업데이트합니다.
        
        Args:
            item_id: 업데이트할 아이템의 ID
            name: 새 이름 (변경 시)
            parent_id: 새 부모 ID (변경 시)
            
        Returns:
            성공 여부
        """
        if item_id not in self._items:
            return False
            
        item = self._items[item_id]
        
        if name is not None:
            item.set_property("name", name)
            
        if parent_id is not None:
            # 순환 참조 방지 (부모가 자신이나 자신의 자식이 아닌지 확인)
            if parent_id != item_id and not self._is_descendant(item_id, parent_id):
                item.set_property("parent_id", parent_id)
            else:
                return False
                
        return True
    
    def _is_descendant(self, parent_id: str, child_id: str) -> bool:
        """
        child_id가 parent_id의 자손인지 확인합니다.
        순환 참조 방지를 위해 사용됩니다.
        """
        if child_id not in self._items:
            return False
            
        current_id = self._items[child_id].get_property("parent_id")
        while current_id:
            if current_id == parent_id:
                return True
            if current_id not in self._items:
                break
            current_id = self._items[current_id].get_property("parent_id")
            
        return False
    
    def get_item(self, item_id: str) -> Optional[SimpleTreeItem]:
        return self._items.get(item_id)
    
    def get_all_items(self) -> Dict[str, SimpleTreeItem]:
        return self._items
        
    def to_json(self) -> str:
        """
        트리 구조를 JSON 문자열로 직렬화합니다.
        
        Returns:
            JSON 문자열
        """
        items_data = {}
        
        for item_id, item in self._items.items():
            # 각 아이템의 데이터 복사본 생성
            item_data = {}
            for key, value in item._data.items():
                item_data[key] = value
            
            # ID는 별도로 저장
            item_data["id"] = item.get_id()
            
            items_data[item_id] = item_data
            
        return json.dumps(items_data, ensure_ascii=False, indent=2)
    
    def save_to_file(self, file_path: str) -> bool:
        """
        트리 구조를 JSON 파일로 저장합니다.
        
        Args:
            file_path: 저장할 파일 경로
            
        Returns:
            성공 여부
        """
        try:
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(self.to_json())
            return True
        except Exception as e:
            print(f"파일 저장 실패: {e}")
            return False
    
    @classmethod
    def from_json(cls, json_str: str) -> 'SimpleTree':
        """
        JSON 문자열에서 트리 구조를 로드합니다.
        
        Args:
            json_str: JSON 문자열
            
        Returns:
            SimpleTree 인스턴스
        """
        tree = cls()
        
        try:
            items_data = json.loads(json_str)
            
            # 모든 아이템 먼저 생성
            for item_id, item_data in items_data.items():
                name = item_data.get("name", "")
                item = SimpleTreeItem(item_id, name)
                
                # 기타 속성 복원
                for key, value in item_data.items():
                    if key != "id" and key != "name":  # ID와 이름은 이미 설정됨
                        item.set_property(key, value)
                
                # 부모 ID는 제외 (순환 참조 방지를 위해 별도로 처리)
                parent_id = item_data.get("parent_id")
                if parent_id:
                    item_data["_temp_parent_id"] = parent_id
                
                tree._items[item_id] = item
            
            # 부모-자식 관계 설정
            for item_id, item_data in items_data.items():
                parent_id = item_data.get("_temp_parent_id")
                if parent_id:
                    tree._items[item_id].set_property("parent_id", parent_id)
            
            return tree
        except Exception as e:
            print(f"JSON 파싱 실패: {e}")
            return tree
    
    @classmethod
    def load_from_file(cls, file_path: str) -> Optional['SimpleTree']:
        """
        JSON 파일에서 트리 구조를 로드합니다.
        
        Args:
            file_path: 파일 경로
            
        Returns:
            SimpleTree 인스턴스 또는 None (실패 시)
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                json_str = file.read()
            return cls.from_json(json_str)
        except Exception as e:
            print(f"파일 불러오기 실패: {e}")
            return None
