from typing import Optional
from core.interfaces.base_tree import IMTTreeItem
from core.interfaces.base_item_data import MTTreeItemData

def to_tree_item_data(
    item: IMTTreeItem,
    parent_id: Optional[str],
    selected: bool = False
) -> MTTreeItemData:
    """
    IMTTreeItem 객체와 parent_id, selected 정보를 받아 MTTreeItemData로 변환하는 함수의 인터페이스입니다.
    """
    pass 