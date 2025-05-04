from enum import Enum
from typing import Any, Dict, Generic, List, Optional, Protocol, Tuple, TypeVar, runtime_checkable

# 타입 변수 정의
T = TypeVar('T')  # 제네릭 타입 변수 정의

@runtime_checkable
class IMTBaseItem(Protocol):
    """기본 아이템 인터페이스"""
    @property
    def id(self) -> str: ...
    
    @property
    def data(self) -> Dict[str, Any]: ...

# MTAction 관련 인터페이스
class IMTAction(Protocol):
    """액션 인터페이스"""
    def get_action_id(self) -> str: ...
    
    def get_action_params(self) -> Dict[str, Any]: ...
    
    def get_device_type(self) -> 'MTDevice': ...

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
    def get_device_type(self) -> 'MTDevice': ...
    
    def clone(self) -> 'IMTActionData': ...

# 마우스 액션 데이터 인터페이스
class IMTMouseActionData(IMTActionData, Protocol):
    """마우스 액션 데이터 인터페이스"""
    @property
    def position(self) -> IMTPoint: ...
    
    @property
    def end_position(self) -> Optional[IMTPoint]: ...
    
    @property
    def button(self) -> str: ...

# 키보드 액션 데이터 인터페이스
class IMTKeyboardActionData(IMTActionData, Protocol):
    """키보드 액션 데이터 인터페이스"""
    @property
    def action_type(self) -> 'MTKeyboardAction': ...
    
    def get_key_sequence(self) -> List[Tuple[str, 'MTKeyState']]: ...
    
    def add_key(self, key: str, state: 'MTKeyState') -> None: ...
    
    def clear(self) -> None: ...

# 트리 아이템 인터페이스
@runtime_checkable
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
        """아이템 속성을 가져옵니다."""
        ...
    
    def set_property(self, key: str, value: T) -> None:
        """아이템 속성을 설정합니다."""
        ...
    
    def clone(self) -> 'IMTTreeItem':
        """아이템의 복제본을 생성합니다."""
        ... 