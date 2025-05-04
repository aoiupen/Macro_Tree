from enum import Enum
from typing import Any, Dict, ClassVar

from model.action.interfaces.base_action import IMTAction, MTDevice

class MTBaseAction(Enum, IMTAction):
    """기본 액션 클래스"""
    
    # 각 하위 클래스에서 설정할 디바이스 타입
    DEVICE_TYPE: ClassVar[MTDevice] = None
    
    def get_action_id(self) -> str:
        """액션 ID(값)을 반환합니다."""
        return self.value
    
    def get_action_params(self) -> Dict[str, Any]:
        """액션 매개변수를 반환합니다."""
        return {}
    
    def get_device_type(self) -> MTDevice:
        """액션의 장치 유형을 반환합니다."""
        return self.__class__.DEVICE_TYPE


class MTMouseAction(MTBaseAction):
    """마우스 액션 유형"""
    DEVICE_TYPE = MTDevice.MOUSE
    
    CLICK = "click"
    DOUBLE_CLICK = "doubleclick"
    RIGHT_CLICK = "rightclick"
    DRAG = "drag"
    MOVE = "move"


class MTKeyboardAction(MTBaseAction):
    """키보드 액션 유형"""
    DEVICE_TYPE = MTDevice.KEYBOARD
    
    TYPE = "type"
    SHORTCUT = "shortcut" 


class MTPoint:
    """간단한 2D 좌표 구현"""
    
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y
    
    def clone(self):
        return MTPoint(self.x, self.y)


class MTMouseActionData:
    """간단한 마우스 액션 데이터 구현"""
    
    def __init__(self, position, button="left", end_position=None):
        self.position = position
        self.button = button
        self.end_position = end_position
    
    def get_device_type(self):
        return MTDevice.MOUSE
    
    def clone(self):
        end_pos = self.end_position.clone() if self.end_position else None
        return MTMouseActionData(self.position.clone(), self.button, end_pos)


class MTKeyboardActionData:
    """간단한 키보드 액션 데이터 구현"""
    
    def __init__(self, action_type):
        self.action_type = action_type
        self._key_sequence = []
    
    def get_key_sequence(self):
        return self._key_sequence.copy()
    
    def add_key(self, key, state):
        self._key_sequence.append((key, state))
    
    def clear(self):
        self._key_sequence.clear()
    
    def get_device_type(self):
        return MTDevice.KEYBOARD
    
    def clone(self):
        new_data = MTKeyboardActionData(self.action_type)
        for key, state in self._key_sequence:
            new_data.add_key(key, state)
        return new_data 