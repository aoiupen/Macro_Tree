from enum import Enum
from typing import Protocol, Any, List, TypedDict, TypeVar, Generic
from core.interfaces.base_types import IMTPoint

"""
core/interfaces/base_item_data.py
- MacroTree의 도메인 Enum/타입/프로토콜/TypedDict/상수 정의
- 실제 구현체는 core/impl/ 또는 model/action/impl/에 위치
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
E = TypeVar("E", bound=Enum)
# ActionData용 TypeVar

class IMTAction(Protocol, Generic[E]):
    @property
    def action_type(self) -> E: ...
    # 기타 공통 메서드/속성

class IMTActionData(Protocol):
    """액션 데이터 인터페이스 (각 액션 실행에 필요한 데이터)"""
    def clear(self) -> None: ...

D = TypeVar("D", bound=IMTActionData)

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
class IMTActionPerformer(Protocol, Generic[D]):
    """액션 실행자 인터페이스 (구현체: model/action/impl/ 등)"""
    def perform(self, action_data: D) -> None: ...

# -------------------
# TreeItemData (TypedDict)
# -------------------
# RF: TypedDict는 구조체. 그 아래는 인터페이스 가질 수 있음
# RF: I는 TypedDict, dataclass, enum에 쓰지 않는다
class MTTreeItemData(TypedDict, total=False):
    """트리 아이템 데이터 구조 (total=False: 모든 필드 선택적)"""
    name: str
    parent_id: str | None
    children_ids: List[str]
    node_type: MTNodeType
    device: MTDevice | None
    action: IMTAction | None
    action_data: IMTActionData | None
    # 기타 UI/확장 속성은 필요에 따라 추가

# -------------------
# TreeItemKeys (도메인 + UI/확장 키 상수)
# -------------------
class TreeItemKeys:
    """트리 아이템의 속성 키 상수 (도메인 + UI/확장)"""
    # 도메인 속성 키
    NAME = "name"
    PARENT_ID = "parent_id"
    CHILDREN = "children_ids"
    NODE_TYPE = "node_type"
    DEVICE = "device"
    ACTION = "action"
    ACTION_DATA = "action_data"