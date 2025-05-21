from enum import Enum
from typing import Protocol, Any, List, TypedDict, TypeVar, Generic, Optional
from core.interfaces.base_types import IMTPoint
from dataclasses import dataclass, field
import dataclasses
import uuid

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
# Enum용 TypeVar
TActionEnum = TypeVar("TActionEnum", bound=Enum, covariant=True)
# ActionData용 TypeVar

class IMTAction(Protocol, Generic[TActionEnum]):
    @property
    def action_type(self) -> TActionEnum: ...
    # 기타 공통 메서드/속성

class IMTActionData(Protocol):
    """액션 데이터 인터페이스 (각 액션 실행에 필요한 데이터)"""
    def clear(self) -> None: ...

TActionData = TypeVar("TActionData", bound=IMTActionData, contravariant=True)

class IMTMouseActionData(IMTActionData, Protocol):
    """마우스 액션 데이터 인터페이스"""
    @property
    def action_type(self) -> MTMouseAction: ...
    @property
    def position(self) -> IMTPoint: ...
    @property
    def end_position(self) -> IMTPoint | None: ...
    @property
    def button(self) -> str: ...

class IMTKeyboardActionData(IMTActionData, Protocol):
    """키보드 액션 데이터 인터페이스"""
    @property
    def action_type(self) -> MTKeyboardAction: ...
    @property
    def key(self) -> str: ...  # 단일 키만 다룬다면
    # 시퀀스가 필요하면 key_sequence 속성/메서드 추가

# 3. ActionPerformer: 실제 동작만 담당 (함수/실행자)
class IMTActionPerformer(Protocol, Generic[TActionData]):
    """액션 실행자 인터페이스 (구현체: model/action/impl/ 등)"""
    def perform(self, action_data: TActionData) -> None: ...

# -------------------
# TreeItemData (TypedDict)
# -------------------
# RF: TypedDict는 구조체. 그 아래는 인터페이스 가질 수 있음
# RF: I는 TypedDict, dataclass, enum에 쓰지 않는다
@dataclass
class MTItemDomainDTO:
    name: str = ""
    parent_id: str | None = None
    children_ids: List[str] = field(default_factory=list)
    node_type: MTNodeType | None = None
    device: MTDevice | None = None
    action: IMTAction | None = None
    action_data: IMTActionData | None = None
    def to_dict(self) -> dict:
        return dataclasses.asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> 'MTItemDomainDTO':
        field_names = {f.name for f in dataclasses.fields(cls)}
        filtered_data = {k: v for k, v in data.items() if k in field_names}
        return cls(**filtered_data)

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
class MTItemDTO: # MTTreeItemSnapshotDTO 대신 MTItemDTO 사용
    """MTTreeItem의 상태(도메인 데이터와 UI 상태)를 포함하는 DTO입니다. ID는 제외됩니다."""
    id: str  # ID 필드 추가
    domain_data: MTItemDomainDTO
    ui_state_data: MTItemUIStateDTO

    def to_dict(self) -> dict:
        return {
            "id": self.id,  # ID 포함
            "domain_data": self.domain_data.to_dict(),
            "ui_state_data": self.ui_state_data.to_dict()
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'MTItemDTO':
        item_id = data.get("id")
        if item_id is None:
            # ID가 없는 경우에 대한 처리 (예: UUID 자동 생성 또는 예외 발생)
            # 여기서는 UUID를 새로 생성하거나, 예외를 발생시킬 수 있습니다.
            # 현재 요구사항에 따라 ID가 항상 있어야 한다면 예외 발생이 적절할 수 있습니다.
            # raise ValueError("ID is required for MTItemDTO")
            item_id = str(uuid.uuid4()) # 또는 기본값으로 UUID 생성

        domain_dto = MTItemDomainDTO.from_dict(data.get("domain_data", {}))
        ui_state_dto = MTItemUIStateDTO.from_dict(data.get("ui_state_data", {}))
        return cls(id=item_id, domain_data=domain_dto, ui_state_data=ui_state_dto)