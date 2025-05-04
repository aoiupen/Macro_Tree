from enum import Enum
from typing import Any, Dict, List, Protocol, Tuple, TypeVar

class MTNode(Enum):
    """매크로 트리의 노드 유형"""
    GROUP = "group"
    INSTRUCTION = "instruction"


class MTDevice(Enum):
    """매크로 트리에서 사용하는 입력 장치 유형"""
    MOUSE = "mouse"
    KEYBOARD = "keyboard"
    JOYSTICK = "joystick"


class MTKeyState(Enum):
    """키 상태"""
    PRESSED = "pressed"
    RELEASED = "released"


class IMTAction(Protocol):
    """액션 인터페이스"""
    def get_action_id(self) -> str: ...
    
    def get_action_params(self) -> Dict[str, Any]: ...
    
    def get_device_type(self) -> MTDevice: ...


# 좌표 인터페이스
class IMTPoint(Protocol):
    """2D 좌표 인터페이스"""
    @property
    def x(self) -> int: ...
    
    @property
    def y(self) -> int: ...
    
    def clone(self) -> 'IMTPoint': ...


# 액션 데이터 인터페이스
class IMTActionData(Protocol):
    """액션 데이터 기본 인터페이스"""
    def get_device_type(self) -> MTDevice: ...
    
    def clone(self) -> 'IMTActionData': ...


# 마우스 액션 데이터 인터페이스
class IMTMouseActionData(IMTActionData, Protocol):
    """마우스 액션 데이터 인터페이스"""
    @property
    def position(self) -> IMTPoint: ...
    
    @property
    def end_position(self) -> IMTPoint | None: ...
    
    @property
    def button(self) -> str: ...


# 키보드 액션 데이터 인터페이스
class IMTKeyboardActionData(IMTActionData, Protocol):
    """키보드 액션 데이터 인터페이스"""
    @property
    def action_type(self) -> 'MTKeyboardAction': ...
    
    def get_key_sequence(self) -> List[Tuple[str, MTKeyState]]: ...
    
    def add_key(self, key: str, state: MTKeyState) -> None: ...
    
    def clear(self) -> None: ... 