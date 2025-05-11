from typing import Any, Callable, Dict, Generic, Iterator, Protocol, TypeVar

# 공변성 타입 변수 정의
T_co = TypeVar('T_co', covariant=True)

# 필터링 기능이 있는 고급 순회 인터페이스
class IMTTreeAdvancedTraversable(Protocol, Generic[T_co]):
    """확장된 매크로 트리 순회 인터페이스 - 필터링 기능 포함"""
    
    def traverse_filtered(self, predicate: Callable[[T_co], bool]) -> Iterator[T_co]:
        """트리를 순회하며 조건에 맞는 아이템 선택"""
        ... 