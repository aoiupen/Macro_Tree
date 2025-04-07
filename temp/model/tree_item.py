from typing import Protocol, List, Optional, Dict, Any, Tuple, Union, TypedDict, TypeVar, Generic
from enum import Enum
from temp.core.base_item import IMTBaseItem


class MTNode(Enum):
    """매크로 트리의 노드 유형"""
    GROUP = "group"
    INSTRUCTION = "instruction"


class MTInputDevice(Enum):
    """매크로 트리에서 사용하는 입력 장치 유형"""
    MOUSE = "mouse"
    KEYBOARD = "keyboard"
    JOYSTICK = "joystick"


class IMTActionType(Protocol):
    def get_action_id(self) -> str:
        ...
    
    def get_action_params(self) -> Dict[str, Any]:
        ...
    
    def get_device_type(self) -> MTInputDevice:
        ...


class MTMouseAction(Enum):
    CLICK = "click"
    DOUBLE_CLICK = "doubleclick"
    RIGHT_CLICK = "rightclick"
    DRAG = "drag"
    MOVE = "move"
    
    def get_action_id(self) -> str:
        return self.value
    
    def get_action_params(self) -> Dict[str, Any]:
        return {}
    
    def get_device_type(self) -> MTInputDevice:
        return MTInputDevice.MOUSE


class MTKeyboardAction(Enum):
    TYPE = "type"
    SHORTCUT = "shortcut"
    
    def get_action_id(self) -> str:
        return self.value
    
    def get_action_params(self) -> Dict[str, Any]:
        return {}
    
    def get_device_type(self) -> MTInputDevice:
        return MTInputDevice.KEYBOARD


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


class TreeItemData(TypedDict, total=False): # dict 의 value 값 검증을 위해 타입을 규정함
    """트리 아이템 데이터 구조 (total=False: 모든 필드 선택적)"""
    node_type: MTNode  # 노드 유형 (그룹/지시 등)
    name: str  # 아이템 이름
    parent_id: Optional[str]  # 부모 아이템 ID
    children_ids: List[str]  # 자식 아이템 ID 목록
    action_type: Optional[IMTActionType]  # MTActionType에서 IMTActionType으로 수정
    action_data: Optional[IMTInputActionData]  # Union 대신 공통 인터페이스

T = TypeVar('T')  # 제네릭 타입 변수 정의

class TreeItemKeys:
    """트리 아이템 속성 키 상수 정의"""
    ID = "id"
    NAME = "name"
    PARENT_ID = "parent_id"
    CHILDREN = "children"
    DATA = "data"
    TYPE = "type"
    ACTION = "action"
    ACTION_DATA = "action_data"
    EXPANDED = "expanded"
    SELECTED = "selected"
    VISIBLE = "visible"
    ICON = "icon"

class IMTTreeItem(IMTBaseItem, Protocol):
    """매크로 트리 아이템 인터페이스
    
    트리에서 사용되는 개별 아이템의 인터페이스입니다.
    id만 직접 접근 속성으로 제공하고, 나머지는 data 딕셔너리를 통해 액세스합니다.
    """
    # id와 data 프로퍼티는 IMTBaseItem에서 이미 정의됨
    
    def get_id(self) -> str:
        """아이템 ID 반환"""
        ...
    
    def get_property(self, key: str, default: Optional[T] = None) -> Optional[T]:
        """아이템 속성을 가져옵니다.
        
        사용 예:
            item.get_property(TreeItemKeys.NAME)
            item.get_property(TreeItemKeys.PARENT_ID)
        """
        ...
    
    def set_property(self, key: str, value: T) -> None:
        """아이템 속성을 설정합니다.
        
        사용 예:
            item.set_property(TreeItemKeys.NAME, "새 이름")
            item.set_property(TreeItemKeys.PARENT_ID, parent_id)
        """
        ...
    
    def clone(self) -> 'IMTTreeItem':
        """아이템의 복제본을 생성합니다."""
        ...