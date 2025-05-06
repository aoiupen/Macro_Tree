from core.interfaces.base_types import IMTPoint
from typing import Optional
from core.interfaces.base_tree import IMTTreeItem
from core.interfaces.base_item_data import MTTreeItemData

class MTPoint(IMTPoint):
    def __init__(self, x: int, y: int):
        self._x = x
        self._y = y

    @property
    def x(self) -> int:
        return self._x

    @property
    def y(self) -> int:
        return self._y

    def clone(self) -> 'MTPoint':
        return MTPoint(self._x, self._y)

def to_tree_item_data(
    item: IMTTreeItem,
    parent_id: Optional[str],
    selected: bool = False
) -> MTTreeItemData:
    """
    IMTTreeItem 객체와 parent_id, selected 정보를 받아 MTTreeItemData로 변환합니다.
    """
    data = dict(item.data) if hasattr(item, "data") else {}
    data["parent_id"] = parent_id
    data["selected"] = selected
    return MTTreeItemData(**data)