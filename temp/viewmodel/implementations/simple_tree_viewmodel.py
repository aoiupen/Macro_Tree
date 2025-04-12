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
