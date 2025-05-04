from typing import Any, Dict, TypeVar

from core.interfaces.base_item import IMTTreeItem
from core.interfaces.base_item_types import TreeItemData

T = TypeVar('T')  # 제네릭 타입 변수 정의

class MTTreeItem(IMTTreeItem):
    """매크로 트리 아이템 구현 클래스"""
    
    def __init__(self, item_id: str, initial_data: Dict[str, Any] | None = None):
        """아이템 초기화
        
        Args:
            item_id: 아이템 ID
            initial_data: 초기 데이터 (Optional)
        """
        self._id = item_id
        self._data = initial_data or {}
    
    @property
    def id(self) -> str:
        """아이템 ID를 반환합니다."""
        return self._id
    
    @property
    def data(self) -> Dict[str, Any]:
        """아이템 데이터를 반환합니다."""
        return self._data.copy()
    
    def get_property(self, key: str, default: T | None = None) -> T | None:
        """아이템 속성을 가져옵니다."""
        return self._data.get(key, default)
    
    def set_property(self, key: str, value: T) -> None:
        """아이템 속성을 설정합니다."""
        self._data[key] = value
    
    def clone(self) -> 'MTTreeItem':
        """아이템의 복제본을 생성합니다."""
        return MTTreeItem(self._id, self._data.copy())


class SimpleTreeItem(MTTreeItem):
    """간단한 트리 아이템 구현 클래스"""
    
    def __init__(self, item_id: str, name: str) -> None:
        """아이템 초기화
        
        Args:
            item_id: 아이템 ID
            name: 아이템 이름
        """
        initial_data: TreeItemData = {
            "name": name,
            "expanded": False,  # 기본적으로 축소됨
            "selected": False   # 기본적으로 선택되지 않음
        }
        super().__init__(item_id, initial_data) 