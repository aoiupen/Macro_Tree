from enum import Enum
from typing import Any, Dict, List, Optional, Tuple, TypedDict, TypeVar

from core.base_item import IMTBaseItem, IMTAction, IMTActionData


class MTNode(Enum):
    """매크로 트리의 노드 유형"""
    GROUP = "group"
    INSTRUCTION = "instruction"


class MTDevice(Enum):
    """매크로 트리에서 사용하는 입력 장치 유형"""
    MOUSE = "mouse"
    KEYBOARD = "keyboard"
    JOYSTICK = "joystick"


class MTAction:
    """기본 액션 클래스"""
    def get_action_name(self) -> str:
        raise NotImplementedError
    
    def get_action_params(self) -> Dict[str, Any]:
        return {}
    
    def get_device_type(self) -> MTDevice:
        raise NotImplementedError


class MTMouseAction(Enum, MTAction):
    CLICK = "click"
    DOUBLE_CLICK = "doubleclick"
    RIGHT_CLICK = "rightclick"
    DRAG = "drag"
    MOVE = "move"
    
    def get_action_name(self) -> str:
        return self.value
    
    def get_action_params(self) -> Dict[str, Any]:
        return {}
    
    def get_device_type(self) -> MTDevice:
        return MTDevice.MOUSE


class MTKeyboardAction(Enum, MTAction):
    TYPE = "type"
    SHORTCUT = "shortcut"
    
    def get_action_name(self) -> str:
        return self.value
    
    def get_action_params(self) -> Dict[str, Any]:
        return {}
    
    def get_device_type(self) -> MTDevice:
        return MTDevice.KEYBOARD


class MTKeyState(Enum):
    """키 상태"""
    PRESSED = "pressed"
    RELEASED = "released"


class TreeItemData(TypedDict, total=False): # dict 의 value 값 검증을 위해 타입을 규정함
    """트리 아이템 데이터 구조 (total=False: 모든 필드 선택적)"""
    node_type: MTNode  # 노드 유형 (그룹/지시 등)
    name: str  # 아이템 이름
    parent_id: Optional[str]  # 부모 아이템 ID
    children_ids: List[str]  # 자식 아이템 ID 목록
    action_type: Optional[IMTAction]  # 액션 타입
    action_data: Optional[IMTActionData]  # 액션 데이터

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