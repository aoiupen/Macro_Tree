from typing import Protocol, List, Optional, Dict, Any, Union, Tuple
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

class MTTreeItemId(Protocol):
    """트리 아이템 ID 프로토콜"""
    @property # 단일 값은 Optional으로 표현하는 것이 관용적
    def parent_id(self) -> Optional[str]: ...
    
    @property
    def self_id(self) -> str: ...
    
    @property # 컬렉션은 빈 컬렉션으로 표현하는 것이 관용적
    def child_ids(self) -> List[str]: 
        """Instruction 타입은 이 메서드가 빈 리스트 반환 또는 예외 발생"""
        ...

class MTTreeItem(Protocol):
    """트리 아이템 핵심 프로토콜"""
    @property
    def id(self) -> MTTreeItemId: ...
    
    @property
    def node(self) -> MTNode: ...
    
    @property
    def input_device(self) -> MTInputDevice: ...
    
    @property
    def action(self) -> Union[MTMouseAction, MTKeyboardAction]: ...
    
    @property
    def parameters(self) -> Dict[str, Any]: 
        """
        추가 매개변수 및 메타데이터.
        액션 데이터도 여기에 저장됨.
        """
        ...
    
    @property
    def action_data(self) -> Union[MTMouseActionData, MTKeyboardActionData]: ...
    
    def execute(self) -> None:
        """아이템 실행"""
        ...
    
    def can_have_children(self) -> bool:
        """자식 아이템을 가질 수 있는지 여부"""
        ...