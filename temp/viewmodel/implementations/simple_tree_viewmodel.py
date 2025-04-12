from typing import Dict, List, Any, Optional
from ...model.implementations.simple_tree import SimpleTree
from ...model.implementations.simple_tree_item import SimpleTreeItem

class SimpleTreeViewModel:
    def __init__(self, tree: SimpleTree):
        self._tree = tree
        self._selected_ids: List[str] = []
    
    def get_items_for_display(self) -> List[Dict[str, Any]]:
        tree_items = self._tree.get_all_items()
        
        # 리스트 컴프리헨션 사용
        return [{
            "id": item.get_id(),
            "name": item.get_property("name", ""),
            "selected": item.get_id() in self._selected_ids
        } for item_id, item in tree_items.items()]
    
    def select_item(self, item_id: str) -> bool:
        item = self._tree.get_item(item_id)
        if not item:
            return False
        
        if item_id not in self._selected_ids:
            self._selected_ids.append(item_id)
        return True
    
    def get_selected_items(self) -> List[str]:
        return self._selected_ids

    def get_visible_items(self) -> List[Dict[str, Any]]:
        """화면에 표시할 아이템만 반환 (확장 상태에 따라 필터링)"""
        result = []
        
        # 루트 레벨 아이템 먼저 가져오기
        root_items = [item for item_id, item in self._tree.get_all_items().items() 
                     if not item.get_property("parent_id")]
        
        # 각 루트 아이템에 대해 자식 아이템 재귀적으로 처리
        for item in root_items:
            result.append({
                "id": item.get_id(),
                "name": item.get_property("name", ""),
                "level": 0,  # 루트 레벨
                "expanded": item.get_property("expanded", False),
                "selected": item.get_id() in self._selected_ids,
                "has_children": self._has_children(item.get_id())
            })
            
            # 확장된 상태면 자식도 포함
            if item.get_property("expanded", False):
                self._add_children_to_result(item.get_id(), result, 1)  # 레벨 1부터 시작
        
        return result

    def _add_children_to_result(self, parent_id: str, result: List[Dict[str, Any]], level: int) -> None:
        """특정 부모의 자식 아이템을 결과 목록에 추가"""
        children = self._get_children(parent_id)
        
        for child in children:
            child_id = child.get_id()
            result.append({
                "id": child_id,
                "name": child.get_property("name", ""),
                "level": level,
                "expanded": child.get_property("expanded", False),
                "selected": child_id in self._selected_ids,
                "has_children": self._has_children(child_id)
            })
            
            # 이 자식이 확장되어 있으면 그 자식들도 추가
            if child.get_property("expanded", False):
                self._add_children_to_result(child_id, result, level + 1)

    def _get_children(self, parent_id: str) -> List[SimpleTreeItem]:
        """특정 부모의 모든 자식 아이템 반환"""
        return [item for item_id, item in self._tree.get_all_items().items() 
                if item.get_property("parent_id") == parent_id]

    def _has_children(self, item_id: str) -> bool:
        """아이템이 자식을 가지고 있는지 확인"""
        for item in self._tree.get_all_items().values():
            if item.get_property("parent_id") == item_id:
                return True
        return False

    def toggle_expanded(self, item_id: str) -> bool:
        """아이템의 확장/축소 상태 토글"""
        item = self._tree.get_item(item_id)
        if not item:
            return False
        
        current = item.get_property("expanded", False)
        item.set_property("expanded", not current)
        return True
