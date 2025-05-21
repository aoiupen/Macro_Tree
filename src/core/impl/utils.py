from core.interfaces.base_tree import IMTTreeItem
from core.interfaces.base_item_data import MTItemDomainDTO
from dataclasses import asdict

"""
이 모듈은 트리 아이템 데이터 변환 유틸리티 함수를 제공합니다.
"""

def to_tree_item_data(
    item: IMTTreeItem,
    parent_id: str | None,
    selected: bool = False
) -> MTItemDomainDTO:
    """
    IMTTreeItem 객체와 parent_id, selected 정보를 받아 MTItemDomainDTO로 변환합니다.
    Args:
        item (IMTTreeItem): 변환할 트리 아이템
        parent_id (str | None): 부모 아이템 ID
        selected (bool): 선택 여부
    Returns:
        MTItemDomainDTO: 변환된 트리 아이템 데이터
    """
    # RF : MTItemDomainDTO를 dataclass로 바꾸면 dict 대신 asdict()로 변환해야 한다.
    data = asdict(item.data) if hasattr(item, "data") else {}
    data["parent_id"] = parent_id
    data["selected"] = selected
    return MTItemDomainDTO(
        id=data.get('id', ""),
        name=data.get('name', ""),
        parent_id=data.get('parent_id'),
        children_ids=data.get('children_ids', []),
        node_type=data.get('node_type'),
        device=data.get('device'),
        action=data.get('action'),
        action_data=data.get('action_data'),
    ) 