from typing import Any, Dict, TypeVar, cast
import copy
import dataclasses
from enum import Enum

from core.interfaces.base_item import IMTTreeItem
from core.interfaces.base_item_keys import DomainKeys as DK, UIStateKeys as UK
from core.interfaces.base_item_data import MTItemDomainDTO, MTItemUIStateDTO

"""
이 모듈은 매크로 트리의 아이템(MTTreeItem) 구현을 제공합니다.
"""

class MTTreeItem(IMTTreeItem):
    """
    매크로 트리 아이템 구현 클래스입니다.
    각 아이템의 ID와 데이터를 관리하며, 속성 접근 및 복제 기능을 제공합니다.
    """
    
    def __init__(
        self,
        item_id: str,
        domain_data: MTItemDomainDTO | dict | None = None,
        ui_state_data: MTItemUIStateDTO | dict | None = None
    ):
        """
        아이템을 초기화합니다.
        Args:
            item_id (str): 아이템 ID
            initial_data (MTItemDomainDTO | dict | None): 초기 데이터 (선택)
            ui_state_data (MTItemUIStateDTO | dict | None): 초기 UI 상태 데이터 (선택)
        """
        self._id = item_id
        # 도메인 데이터 처리
        if isinstance(domain_data, dict):
            self._domain_data = MTItemDomainDTO(**domain_data)
        elif isinstance(domain_data, MTItemDomainDTO):
            self._domain_data = domain_data
        else:
            self._domain_data = MTItemDomainDTO(name="")
        # UI 상태 데이터 처리
        if isinstance(ui_state_data, dict):
            self._ui_state_data = MTItemUIStateDTO(**ui_state_data)
        elif isinstance(ui_state_data, MTItemUIStateDTO):
            self._ui_state_data = ui_state_data
        else:
            self._ui_state_data = MTItemUIStateDTO()
    
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
    def data(self) -> MTItemDomainDTO:
        """
        아이템 데이터를 깊은 복사로 반환합니다. (불변성 보장)
        Returns:
            MTItemDomainDTO: 아이템 데이터
        """
        return copy.deepcopy(self._domain_data)
    
    @property
    def ui_state(self) -> 'MTItemUIStateDTO':
        """
        UI 상태 데이터를 깊은 복사로 반환합니다. (불변성 보장)
        Returns:
            MTItemUIStateDTO: UI 상태 데이터
        """
        return copy.deepcopy(self._ui_state_data)
    
    def get_property(self, key: str, default: Any = None) -> Any:
        """
        아이템 데이터에서 속성 값을 반환합니다.
        Args:
            key (str): 속성명
            default (Any): 기본값
        Returns:
            Any: 속성 값 또는 기본값
        """
        if hasattr(DK, key.upper()):
            key = getattr(DK, key.upper())
        elif hasattr(UK, key.upper()):
            key = getattr(UK, key.upper())
        if hasattr(self._domain_data, key):
            value = getattr(self._domain_data, key, default)
        elif hasattr(self._ui_state_data, key):
            value = getattr(self._ui_state_data, key, default)
        else:
            value = default
        if key == DK.CHILDREN and (value is None):
            return []
        return value
    
    def set_property(self, key: str, value: Any) -> None:
        """
        아이템 데이터의 속성 값을 설정합니다.
        Args:
            key (str): 속성명
            value (Any): 설정할 값
        """
        if hasattr(DK, key.upper()):
            key = getattr(DK, key.upper())
        elif hasattr(UK, key.upper()):
            key = getattr(UK, key.upper())
        if hasattr(self._domain_data, key):
            setattr(self._domain_data, key, value)
        elif hasattr(self._ui_state_data, key):
            setattr(self._ui_state_data, key, value)
    
    def clone(self) -> IMTTreeItem:
        """
        아이템의 복제본을 생성합니다.
        Returns:
            IMTTreeItem: 복제된 아이템
        """
        return MTTreeItem(self._id, copy.deepcopy(self._domain_data), copy.deepcopy(self._ui_state_data))

    def to_dict(self) -> dict:
        return {
            "id": self._id,
            DK.DOMAIN: self._domain_data.to_dict(),
            UK.UI_STATE: self._ui_state_data.to_dict()
        }