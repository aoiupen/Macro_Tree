from typing import Protocol, List, Optional, Dict, Any, Union
from enum import Enum


class MTNode(Enum):
    """매크로 트리의 노드 유형"""
    GROUP = "group"
    INSTRUCTION = "instruction"

class MTInputDevice(Enum):
    """매크로 트리에서 사용하는 입력 장치 유형"""
    MOUSE = "mouse"
    KEYBOARD = "keyboard"
    JOYSTICK = "joystick"

# 마우스 액션 Enum
class MTMouseAction(Enum):
    """마우스 액션 유형"""
    CLICK = "click"
    DOUBLE_CLICK = "doubleclick"
    RIGHT_CLICK = "rightclick"
    DRAG = "drag"
    MOVE = "move"

# 키보드 액션 Enum
class MTKeyboardAction(Enum):
    """키보드 액션 유형"""
    TYPE = "type"          # 일반 타이핑
    SHORTCUT = "shortcut"  # 단축키 조합

# 키 상태 Enum
class MTKeyState(Enum):
    """키 상태"""
    PRESSED = "pressed"
    RELEASED = "released"

# 마우스 좌표 클래스
class MTPoint:
    """2D 좌표 표현"""
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y

# 마우스 액션 데이터
class MTMouseActionData:
    """마우스 액션 관련 데이터"""
    def __init__(self, position: MTPoint, 
                 end_position: Optional[MTPoint] = None,
                 button: str = "left"):
        self.position = position
        self.end_position = end_position  # drag용
        self.button = button

class MTKeyboardActionData:
    """키보드 액션 관련 데이터"""
    def __init__(self):
        self.key_sequence = []  # [(key, state), ...]
    
    def add_key(self, key: str, state: MTKeyState = MTKeyState.PRESSED):
        """키 상태 추가"""
        self.key_sequence.append((key, state))
    
    def clear(self):
        """시퀀스 초기화"""
        self.key_sequence.clear()


class IMTTreeItem(Protocol):
    """매크로 트리 아이템 인터페이스
    
    트리에서 사용되는 개별 아이템의 인터페이스입니다.
    id만 직접 접근 속성으로 제공하고, 나머지는 data 딕셔너리를 통해 액세스합니다.
    """
    @property
    def id(self) -> str:
        """아이템 고유 식별자"""
        ...
    
    @property
    def data(self) -> Dict[str, Any]:
        """아이템의 모든 데이터"""
        ...
    
    def set_property(self, key: str, value: Any) -> None:
        """아이템 속성을 설정합니다.
        
        Args:
            key: 속성 키
            value: 설정할 값
        """
        ...
    
    def get_property(self, key: str, default: Any = None) -> Any:
        """아이템 속성을 가져옵니다.
        
        Args:
            key: 속성 키
            default: 속성이 없을 경우 반환할 기본값
            
        Returns:
            속성 값 또는 기본값
        """
        ...
    
    def clone(self) -> 'IMTTreeItem':
        """아이템의 복제본을 생성합니다.
        
        Returns:
            복제된 아이템
        """
        ...