from typing import Protocol, List, Optional, Dict, Any, Tuple, Union, TypedDict, TypeVar, Generic
from enum import Enum
from temp.core.base_item_interface import IBaseItem  # 새로 추가


class MTNode(Enum):
    """매크로 트리의 노드 유형"""
    GROUP = "group"
    INSTRUCTION = "instruction"


class MTInputDevice(Enum):
    """매크로 트리에서 사용하는 입력 장치 유형"""
    MOUSE = "mouse"
    KEYBOARD = "keyboard"
    JOYSTICK = "joystick"


class MTMouseAction(Enum):
    """마우스 액션 유형"""
    CLICK = "click"
    DOUBLE_CLICK = "doubleclick"
    RIGHT_CLICK = "rightclick"
    DRAG = "drag"
    MOVE = "move"


class MTKeyboardAction(Enum):
    """키보드 액션 유형"""
    TYPE = "type"          # 일반 타이핑
    SHORTCUT = "shortcut"  # 단축키 조합


class MTKeyState(Enum):
    """키 상태"""
    PRESSED = "pressed"
    RELEASED = "released"


class IMTPoint(Protocol):
    """2D 좌표 인터페이스"""
    @property
    def x(self) -> int: ...
    
    @property
    def y(self) -> int: ...
    
    def clone(self) -> 'IMTPoint': ...


class IMTInputActionData(Protocol):
    """입력 액션 데이터 기본 인터페이스"""
    def get_device_type(self) -> MTInputDevice: ...
    
    def clone(self) -> 'IMTInputActionData': ...


class IMTMouseActionData(IMTInputActionData, Protocol):
    """마우스 액션 데이터 인터페이스"""
    @property
    def position(self) -> IMTPoint: ...
    
    @property
    def end_position(self) -> Optional[IMTPoint]: ...
    
    @property
    def button(self) -> str: ...


class IMTKeyboardActionData(IMTInputActionData, Protocol):
    """키보드 액션 데이터 인터페이스"""
    @property
    def action_type(self) -> MTKeyboardAction: ...
    
    def get_key_sequence(self) -> List[Tuple[str, MTKeyState]]: ...
    
    def add_key(self, key: str, state: MTKeyState) -> None: ...
    
    def clear(self) -> None: ...


class TreeItemData(TypedDict, total=False):
    """트리 아이템 데이터 구조 (total=False: 모든 필드 선택적)"""
    node_type: MTNode  # 노드 유형 (그룹/지시 등)
    name: str  # 아이템 이름
    parent_id: Optional[str]  # 부모 아이템 ID
    children_ids: List[str]  # 자식 아이템 ID 목록
    action_type: Optional[Union[MTMouseAction, MTKeyboardAction]]  # 입력 장치 유형
    action_data: Optional[Union[IMTMouseActionData, IMTKeyboardActionData]]  # 입력 액션 데이터

T = TypeVar('T')  # 제네릭 타입 변수 정의

class IMTTreeItem(IBaseItem, Protocol):  # IBaseItem 상속 추가
    """매크로 트리 아이템 인터페이스
    
    트리에서 사용되는 개별 아이템의 인터페이스입니다.
    id만 직접 접근 속성으로 제공하고, 나머지는 data 딕셔너리를 통해 액세스합니다.
    """
    # id와 data 프로퍼티는 IBaseItem에서 이미 정의됨
    
    def set_property(self, key: str, value: T) -> None:
        """아이템 속성을 설정합니다."""
        ...
    
    def get_property(self, key: str, default: Optional[T] = None) -> Optional[T]:
        """아이템 속성을 가져옵니다."""
        ...
    
    def clone(self) -> 'IMTTreeItem':
        """아이템의 복제본을 생성합니다."""
        ...