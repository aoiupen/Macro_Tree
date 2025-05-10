from typing import Any, Dict, TypeVar, cast
import copy

from core.interfaces.base_item import IMTTreeItem
from core.interfaces.base_item_data import MTTreeItemData

class MTTreeItem(IMTTreeItem):
    """매크로 트리 아이템 구현 클래스"""
    
    def __init__(self, item_id: str, initial_data: MTTreeItemData | dict | None = None):
        """아이템 초기화
        
        Args:
            item_id: 아이템 ID
            initial_data: 초기 데이터 (Optional)
        """
        self._id = item_id
        if isinstance(initial_data, dict):
            self._data = MTTreeItemData(**initial_data)
        elif isinstance(initial_data, MTTreeItemData):
            self._data = initial_data
        else:
            self._data = MTTreeItemData(id=item_id, name="")
    
    @property
    def id(self) -> str:
        """아이템 ID를 반환합니다."""
        return self._id
    
    # RF : 가변 객체의 불변성 보장에는 deepcopy 사용
    # RF : 대신 deepcopy는 속도 저하 가능성. 추구 캡슐화 예정
    # RF : 그러므로 불변 객체는 딕셔너리에 저장하고, 가변 객체는 캡슐화,불변 래퍼로 처리하면 얕은 복사로도 불변 보장
    @property
    def data(self) -> MTTreeItemData:
        """아이템 데이터를 깊은 복사로 반환 (불변성 보장)"""
        return copy.deepcopy(self._data)
    
    def get_property(self, key: str, default: Any = None) -> Any:
        """
        아이템 속성을 가져옵니다.
        dataclass는 dict처럼 get을 지원하지 않으므로, getattr 사용
        """
        return getattr(self._data, key, default)
    
    def set_property(self, key: str, value: Any) -> None:
        """아이템 속성을 설정합니다."""
        setattr(self._data, key, value)
    
    def clone(self) -> 'MTTreeItem':
        """아이템의 복제본을 생성합니다."""
        return MTTreeItem(self._id, copy.deepcopy(self._data))