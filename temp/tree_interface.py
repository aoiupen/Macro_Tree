from typing import Protocol, Iterator, List, Optional, TypeVar, Generic, Callable, Iterable
from temp.tree_item_interface import MTTreeItem

T = TypeVar('T', bound='MTTreeItem')

class MTTreeTraversal(Protocol, Generic[T]):
    """
    핵심 트리 순회 인터페이스 - 필수 기능만 포함
    """
    
    def traverse(self) -> Iterator[T]:
        """
        트리를 순회하며 모든 아이템 반환
        
        Returns:
            트리 아이템 이터레이터
        """
        ...
    
    def execute(self, items: Iterable[T], action: Callable[[T], None]) -> None:
        """
        선택된 아이템들에 대해 액션 실행
        
        Args:
            items: 액션을 실행할 아이템 목록
            action: 실행할 액션 함수
        """
        ...

class MTTreeAdvancedTraversal(MTTreeTraversal[T], Protocol):
    """
    확장된 트리 순회 인터페이스 - 필터링 기능 포함
    """
    
    def traverse_filtered(self, predicate: Callable[[T], bool]) -> Iterator[T]:
        """
        트리를 순회하며 조건에 맞는 아이템 선택
        
        Args:
            predicate: 선택 조건
            
        Returns:
            조건에 맞는 아이템 이터레이터
        """
        ...