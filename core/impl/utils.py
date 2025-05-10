from core.interfaces.base_tree import IMTTreeItem
from core.interfaces.base_item_data import MTTreeItemData
from dataclasses import asdict

def to_tree_item_data(
    item: IMTTreeItem,
    parent_id: str | None,
    selected: bool = False
) -> MTTreeItemData:
    """
    IMTTreeItem 객체와 parent_id, selected 정보를 받아 MTTreeItemData로 변환합니다.
    """
    # RF : MTTreeItemData를 dataclass로 바꾸면 dict 대신 asdict()로 변환해야 한다.
    data = asdict(item.data) if hasattr(item, "data") else {}
    data["parent_id"] = parent_id
    data["selected"] = selected
    return MTTreeItemData(
        id=data.get('id', ""),
        name=data.get('name', ""),
        parent_id=data.get('parent_id'),
        children_ids=data.get('children_ids', []),
        node_type=data.get('node_type'),
        device=data.get('device'),
        action=data.get('action'),
        action_data=data.get('action_data'),
    ) 