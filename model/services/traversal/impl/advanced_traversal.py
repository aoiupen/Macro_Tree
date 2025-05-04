from typing import Callable, Iterator
from core.interfaces.base_item import IMTTreeItem

class AdvancedTreeTraversal:
    """고급 트리 순회 기능 구현체"""
    
    def __init__(self, items_provider):
        """
        Args:
            items_provider: _items 딕셔너리를 제공하는 객체
        """
        self._items_provider = items_provider
    
    def traverse_filtered(self, predicate: Callable[[IMTTreeItem], bool]) -> Iterator[IMTTreeItem]:
        """트리를 순회하며 조건에 맞는 아이템을 선택합니다.
        
        Args:
            predicate: 필터링 조건 함수
            
        Returns:
            조건에 맞는 아이템 이터레이터
        """
        for item in self._items_provider().values():
            if predicate(item):
                yield item