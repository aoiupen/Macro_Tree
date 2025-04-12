from typing import Dict, Optional, Any
from temp.model.tree_item import TreeItemData

class SimpleTreeItem:
    def __init__(self, item_id: str, name: str) -> None:
        self._id = item_id
        self._data: TreeItemData = {"name": name}
    
    def get_id(self) -> str:
        return self._id
    
    def get_property(self, key: str, default: Optional[Any] = None) -> Any:
        return self._data.get(key, default)
    
    def set_property(self, key: str, value: Any) -> None:
        self._data[key] = value
