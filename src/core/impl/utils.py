from core.interfaces.base_tree import IMTItem
from core.interfaces.base_item_data import MTItemDomainDTO, MTItemUIStateDTO, MTItemDTO
from dataclasses import asdict

"""
이 모듈은 트리 아이템 데이터 변환 유틸리티 함수를 제공합니다.
"""

def to_tree_item_data(
    item: IMTItem,
    parent_id: str | None,
    selected: bool = False
) -> MTItemDTO:
    """
    IMTItem 객체와 parent_id, selected 정보를 받아 MTItemDTO로 변환합니다.
    Args:
        item (IMTItem): 변환할 트리 아이템
        parent_id (str | None): 부모 아이템 ID
        selected (bool): 선택 여부
    Returns:
        MTItemDTO: 변환된 트리 아이템 데이터
    """
    data = asdict(item.data) if hasattr(item, "data") else {}
    data["parent_id"] = parent_id
    domain_dto = MTItemDomainDTO(
        name=data.get('name', ""),
        parent_id=data.get('parent_id'),
        children_ids=data.get('children_ids', []),
        node_type=data.get('node_type'),
        device=data.get('device'),
        action=data.get('action'),
        action_data=data.get('action_data'),
    )
    ui_state = item.ui_state if hasattr(item, "ui_state") else MTItemUIStateDTO()
    ui_state.is_selected = selected
    return MTItemDTO(
        item_id=item.id,
        domain_data=domain_dto,
        ui_state_data=ui_state
    ) 