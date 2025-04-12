from typing import Dict, Optional, List
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
    
    def get_item(self, item_id: str) -> Optional[SimpleTreeItem]:
        return self._items.get(item_id)
    
    def get_all_items(self) -> Dict[str, SimpleTreeItem]:
        return self._items
