"""
이 모듈은 매크로 트리에서 사용하는 공통 데이터 타입 인터페이스를 정의합니다.
"""
from typing import Protocol, TypeVar, Optional

# 좌표 인터페이스
class IMTPoint(Protocol):
    """2D 좌표 인터페이스"""
    @property
    def x(self) -> int: ...
    
    @property
    def y(self) -> int: ...
    
    def clone(self) -> 'IMTPoint': ...

# 공통 동작(메서드) 프로토콜
class IClearable(Protocol):
    def clear(self) -> None: ...

class ICloneable(Protocol):
    def clone(self): ...