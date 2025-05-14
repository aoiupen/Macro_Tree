from enum import Enum
from typing import Any, Dict, ClassVar
from core.interfaces.base_item_data import (
    MTMouseAction, MTKeyboardAction,
    IMTMouseActionData, IMTKeyboardActionData, MTKeyState, IMTPoint
)
from core.impl.types import MTPoint
# RF : action과 actiondata 구현

# 마우스 액션 데이터 구현
class MTMouseActionData(IMTMouseActionData):
    def __init__(self, action_type: MTMouseAction, position: IMTPoint, button: str = "left", end_position: IMTPoint | None = None):
        self._action_type = action_type
        self._position = position
        self._button = button
        self._end_position = end_position

    @property
    def action_type(self) -> MTMouseAction:
        return self._action_type

    @property
    def position(self) -> IMTPoint:
        return self._position

    @property
    def end_position(self) -> IMTPoint | None:
        return self._end_position

    @property
    def button(self) -> str:
        return self._button

    def clear(self) -> None:
        # 필요시 내부 상태 초기화
        pass

# 키보드 액션 데이터 구현
class MTKeyboardActionData(IMTKeyboardActionData):
    def __init__(self, action_type: MTKeyboardAction, key: str):
        self._action_type = action_type
        self._key = key
        self._key_sequence: list[tuple[str, MTKeyState]] = []

    @property
    def action_type(self) -> MTKeyboardAction:
        return self._action_type

    @property
    def key(self) -> str:
        return self._key

    def add_key(self, key: str, state: MTKeyState):
        self._key_sequence.append((key, state))

    def get_key_sequence(self):
        return self._key_sequence.copy()

    def clear(self) -> None:
        self._key_sequence.clear()