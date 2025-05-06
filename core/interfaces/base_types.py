# 공통 기본 데이터 타입 인터페이스
from typing import Protocol, TypeVar, Optional
from core.interfaces.base_item_data import MTTreeItemData

# 좌표 인터페이스
class IMTPoint(Protocol):
    """2D 좌표 인터페이스"""
    @property
    def x(self) -> int: ...
    
    @property
    def y(self) -> int: ...
    
    def clone(self) -> 'IMTPoint': ...

TreeNodeDataT = TypeVar('TreeNodeDataT')

# 공통 동작(메서드) 프로토콜
class IClearable(Protocol):
    def clear(self) -> None: ...

class ICloneable(Protocol):
    def clone(self): ...

from core.interfaces.base_tree import IMTTreeItem

def to_tree_item_data(
    item: IMTTreeItem,
    parent_id: Optional[str],
    selected: bool = False
) -> MTTreeItemData:
    """
    IMTTreeItem 객체와 parent_id, selected 정보를 받아 MTTreeItemData로 변환합니다.
    Args:
        item: 변환할 트리 아이템 객체
        parent_id: 부모 아이템 ID
        selected: 선택 여부
    Returns:
        MTTreeItemData: 변환된 데이터 딕셔너리
    """
    pass