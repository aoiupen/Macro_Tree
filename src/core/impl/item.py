from typing import Any, Dict, TypeVar, cast
import copy
import dataclasses
from enum import Enum
import uuid
from dataclasses import asdict, dataclass, field
from core.interfaces.base_item import IMTTreeItem
from core.interfaces.base_item_keys import DomainKeys as DK, UIStateKeys as UK
from core.interfaces.base_item_data import MTItemDomainDTO, MTItemUIStateDTO, MTNodeType, MTItemDTO

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
            domain_data (MTItemDomainDTO | dict | None): 초기 도메인 데이터 (선택)
            ui_state_data (MTItemUIStateDTO | dict | None): 초기 UI 상태 데이터 (선택)
        """
        self._id = item_id if item_id else str(uuid.uuid4())
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
    
    @data.setter
    def data(self, value: MTItemDomainDTO) -> None:
        if isinstance(value, MTItemDomainDTO):
            self._domain_data = copy.deepcopy(value) # DTO로 직접 할당
        else:
            # 또는 여기서 에러를 발생시키거나, dict인 경우 변환 시도
            raise TypeError("data must be an instance of MTItemDomainDTO")
    
    @property
    def ui_state(self) -> 'MTItemUIStateDTO':
        """
        UI 상태 데이터를 깊은 복사로 반환합니다. (불변성 보장)
        Returns:
            MTItemUIStateDTO: UI 상태 데이터
        """
        return copy.deepcopy(self._ui_state_data)
    
    @ui_state.setter
    def ui_state(self, value: 'MTItemUIStateDTO') -> None:
        if isinstance(value, MTItemUIStateDTO):
            self._ui_state_data = copy.deepcopy(value) # DTO로 직접 할당
        else:
            raise TypeError("ui_state must be an instance of MTItemUIStateDTO")
    
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

    def to_dto(self) -> MTItemDTO:
        """MTTreeItem의 현재 상태를 MTItemDTO 객체로 변환합니다. (ID 포함)"""
        return MTItemDTO(
            id=self._id,  # ID 포함
            domain_data=copy.deepcopy(self._domain_data),
            ui_state_data=copy.deepcopy(self._ui_state_data)
        )

    def to_dict(self) -> dict:
        """MTTreeItem의 현재 상태를 딕셔너리로 변환합니다. (ID, domain_data, ui_state 포함)"""
        # 이 메서드는 파일 저장 등을 위해 ID를 포함한 전체 직렬화된 데이터를 반환
        return {
            "id": self._id,
            "domain_data": self._domain_data.to_dict(),
            "ui_state": self._ui_state_data.to_dict()
        }

    @classmethod
    def from_dict(cls, item_dict: dict) -> 'MTTreeItem':
        """딕셔너리로부터 MTTreeItem 객체를 생성합니다."""
        item_id = item_dict.get("id")
        if item_id is None:
            # ID가 없는 경우에 대한 처리 (예: UUID 자동 생성 또는 예외 발생)
            # 여기서는 이전 로직(init에서 자동생성)을 따르거나, 명시적 예외 발생 가능
            # logger.warning("MTTreeItem.from_dict: 'id' not found in item_dict, a new UUID will be generated if not provided to constructor.")
            # 또는 raise ValueError("'id' is required in item_dict for MTTreeItem.from_dict")
            item_id = str(uuid.uuid4()) # 생성자에서 id가 None이면 uuid 생성하므로 None 전달 가능
        
        domain_data_dict = item_dict.get("domain_data", {})
        domain_obj = MTItemDomainDTO.from_dict(domain_data_dict)

        ui_state_data_dict = item_dict.get("ui_state", {})
        ui_state_obj = MTItemUIStateDTO.from_dict(ui_state_data_dict)

        return cls(
            item_id=item_id, 
            domain_data=domain_obj, 
            ui_state_data=ui_state_obj
        )