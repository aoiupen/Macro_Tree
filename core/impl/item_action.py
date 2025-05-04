from enum import Enum
from typing import Any, Dict

from core.interfaces.base_item_action import IMTAction, MTDevice


class MTMouseAction(Enum, IMTAction):
    """마우스 액션 유형"""
    CLICK = "click"
    DOUBLE_CLICK = "doubleclick"
    RIGHT_CLICK = "rightclick"
    DRAG = "drag"
    MOVE = "move"
    
    def get_action_id(self) -> str:
        """액션 ID(값)을 반환합니다."""
        return self.value
    
    def get_action_params(self) -> Dict[str, Any]:
        """액션 매개변수를 반환합니다."""
        return {}
    
    def get_device_type(self) -> MTDevice:
        """액션의 장치 유형을 반환합니다."""
        return MTDevice.MOUSE


class MTKeyboardAction(Enum, IMTAction):
    """키보드 액션 유형"""
    TYPE = "type"
    SHORTCUT = "shortcut"
    
    def get_action_id(self) -> str:
        """액션 ID(값)을 반환합니다."""
        return self.value
    
    def get_action_params(self) -> Dict[str, Any]:
        """액션 매개변수를 반환합니다."""
        return {}
    
    def get_device_type(self) -> MTDevice:
        """액션의 장치 유형을 반환합니다."""
        return MTDevice.KEYBOARD 