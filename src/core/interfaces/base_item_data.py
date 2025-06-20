from enum import Enum
from typing import Protocol, TypeVar, Generic, Any
from core.interfaces.base_types import IMTPoint
from dataclasses import dataclass
import dataclasses

"""
이 모듈은 매크로 트리의 도메인 Enum, 타입, 프로토콜, 데이터 구조를 정의합니다.
"""


# -------------------
# Node 관련 Enum
# -------------------


class MTNodeType(Enum):
    """트리 노드 타입 (그룹/실행 단위 등)"""
    GROUP = "group"         # 폴더/그룹 노드
    INSTRUCTION = "instruction"  # 실행 단위 노드


# -------------------
# Device/Action/Key 관련 Enum
# -------------------


class MTDevice(Enum):
    """입력 장치 Enum (마우스, 키보드 등)"""
    MOUSE = "mouse"
    KEYBOARD = "keyboard"
    JOYSTICK = "joystick"
    # 기타 장치(joystick, gamepad 등) 필요시 추가


class MTKeyState(Enum):
    """키 상태"""
    PRESSED = "pressed"
    RELEASED = "released"


class MTMouseAction(Enum):
    """마우스 액션 종류"""
    CLICK = "click"
    DRAG = "drag"
    # ...


class MTKeyboardAction(Enum):
    """키보드 액션 종류"""
    TYPE = "type"
    SHORTCUT = "shortcut"
    # ...


# -------------------
# 액션/액션데이터 인터페이스(프로토콜)
# -------------------

TActionEnum = TypeVar("TActionEnum", bound=Enum, covariant=True)


class IMTAction(Protocol, Generic[TActionEnum]):
    @property
    def action_type(self) -> TActionEnum:
        ...
    # 기타 공통 메서드/속성


class IMTActionData(Protocol):
    """액션 데이터 인터페이스 (각 액션 실행에 필요한 데이터)"""
    def clear(self) -> None:
        ...


TActionData = TypeVar("TActionData", bound=IMTActionData, contravariant=True)


class IMTMouseActionData(IMTActionData, Protocol):
    """마우스 액션 데이터 인터페이스"""
    @property
    def action_type(self) -> MTMouseAction:
        ...

    @property
    def position(self) -> IMTPoint:
        ...

    @property
    def end_position(self) -> IMTPoint | None:
        ...

    @property
    def button(self) -> str:
        ...


class IMTKeyboardActionData(IMTActionData, Protocol):
    """키보드 액션 데이터 인터페이스"""
    @property
    def action_type(self) -> MTKeyboardAction:
        ...

    @property
    def key(self) -> str:
        ...  # 단일 키만 다룬다면
    # 시퀀스가 필요하면 key_sequence 속성/메서드 추가


class IMTActionPerformer(Protocol, Generic[TActionData]):
    """액션 실행자 인터페이스 (구현체: model/action/impl/ 등)"""
    def perform(self, action_data: TActionData) -> None:
        ...


# -------------------
# TreeItemData (TypedDict)
# -------------------

@dataclass
class MTItemDomainDTO:
    name: str = ""
    parent_id: str | None = None
    node_type: MTNodeType | None = None
    device: MTDevice | None = None
    action: IMTAction | None = None
    action_data: IMTActionData | None = None

    def to_dict(self) -> dict:
        d = dataclasses.asdict(self)
        if self.node_type is not None:
            if isinstance(self.node_type, MTNodeType):
                d["node_type"] = self.node_type.value
            else:
                d["node_type"] = self.node_type  # 이미 문자열이면 그대로
        return d

    @classmethod
    def from_dict(cls, data: dict) -> 'MTItemDomainDTO':
        field_names = {f.name for f in dataclasses.fields(cls)}
        filtered_data = {k: v for k, v in data.items() if k in field_names}
        return cls(**filtered_data)

    def get_children(self, tree_items: dict[str, Any]):
        """트리 전체에서 이 아이템의 자식 MTItem 리스트 반환"""
        return [item for item in tree_items.values() if item.parent_id == self.id]


@dataclass
class MTItemUIStateDTO:
    is_selected: bool = False
    is_expanded: bool = False
    visible: bool = True
    icon: str = ""

    def to_dict(self) -> dict:
        return dataclasses.asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> 'MTItemUIStateDTO':
        field_names = {f.name for f in dataclasses.fields(cls)}
        filtered_data = {k: v for k, v in data.items() if k in field_names}
        return cls(**filtered_data)


@dataclass
class MTItemDTO:
    """MTItem의 ID와 상태(도메인 데이터와 UI 상태)를 포함하는 DTO입니다."""
    item_id: str  # id -> item_id 로 변경
    domain_data: MTItemDomainDTO
    ui_state_data: MTItemUIStateDTO

    def to_dict(self) -> dict:
        return {
            "item_id": self.item_id,  # id -> item_id 로 변경
            "domain_data": self.domain_data.to_dict(),
            "ui_state_data": self.ui_state_data.to_dict()
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'MTItemDTO':
        item_id_val = data.get("item_id")  # id -> item_id 로 변경
        if item_id_val is None:
            # 이전 id 키도 호환성을 위해 잠시 확인 (추후 제거 가능)
            item_id_val = data.get("id")
            if item_id_val is None:
                raise ValueError(
                    "item_id is required in the input dictionary for MTItemDTO.from_dict"
                )

        domain_dto = MTItemDomainDTO.from_dict(data.get("domain_data", {}))
        ui_state_dto = MTItemUIStateDTO.from_dict(data.get("ui_state_data", {}))
        return cls(
            item_id=item_id_val,
            domain_data=domain_dto,
            ui_state_data=ui_state_dto
        )
