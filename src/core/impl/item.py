from typing import Any, Dict, TypeVar, cast
import copy

from core.interfaces.base_item import IMTTreeItem
from core.interfaces.base_item_data import MTTreeItemData

"""
이 모듈은 매크로 트리의 아이템(MTTreeItem) 구현을 제공합니다.
"""

class MTTreeItem(IMTTreeItem):
    """
    매크로 트리 아이템 구현 클래스입니다.
    각 아이템의 ID와 데이터를 관리하며, 속성 접근 및 복제 기능을 제공합니다.
    """
    
    def __init__(self, item_id: str, initial_data: MTTreeItemData | dict | None = None):
        """
        아이템을 초기화합니다.
        Args:
            item_id (str): 아이템 ID
            initial_data (MTTreeItemData | dict | None): 초기 데이터 (선택)
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
        """
        아이템의 고유 ID를 반환합니다.
        Returns:
            str: 아이템 ID
        """
        return self._id
    
    # RF : 가변 객체의 불변성 보장에는 deepcopy 사용
    # RF : 대신 deepcopy는 속도 저하 가능성. 추구 캡슐화 예정
    # RF : 그러므로 불변 객체는 딕셔너리에 저장하고, 가변 객체는 캡슐화,불변 래퍼로 처리하면 얕은 복사로도 불변 보장
    @property
    def data(self) -> MTTreeItemData:
        """
        아이템 데이터를 깊은 복사로 반환합니다. (불변성 보장)
        Returns:
            MTTreeItemData: 아이템 데이터
        """
        return copy.deepcopy(self._data)
    
    def get_property(self, key: str, default: Any = None) -> Any:
        """
        아이템 데이터에서 속성 값을 반환합니다.
        Args:
            key (str): 속성명
            default (Any): 기본값
        Returns:
            Any: 속성 값 또는 기본값
        """
        value = getattr(self._data, key, default)
        if key == "children_ids" and (value is None):
            return []
        return value
    
    def set_property(self, key: str, value: Any) -> None:
        """
        아이템 데이터의 속성 값을 설정합니다.
        Args:
            key (str): 속성명
            value (Any): 설정할 값
        """
        setattr(self._data, key, value)
    
    def clone(self) -> IMTTreeItem:
        """
        아이템의 복제본을 생성합니다.
        Returns:
            IMTTreeItem: 복제된 아이템
        """
        return MTTreeItem(self._id, copy.deepcopy(self._data))