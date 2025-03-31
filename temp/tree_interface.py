from typing import Protocol, Iterator, List, Optional, TypeVar, Generic, Callable, Iterable, Dict, Any
from temp.tree_item_interface import IMTTreeItem

T = TypeVar('T', bound=IMTTreeItem)

class IMTTreeTraversal(Protocol, Generic[T]):
    """매크로 트리 순회 인터페이스 - 필수 기능만 포함"""
    
    def traverse(self, tree: 'IMTTree') -> Iterator[T]:
        """트리를 순회하며 모든 아이템 반환"""
        ...
    
    def execute(self, items: Iterable[T], action: Callable[[T], None]) -> None:
        """선택된 아이템들에 대해 액션 실행"""
        ...

class IMTTreeAdvancedTraversal(IMTTreeTraversal[T], Protocol):
    """확장된 매크로 트리 순회 인터페이스 - 필터링 기능 포함"""
    
    def traverse_filtered(self, predicate: Callable[[T], bool]) -> Iterator[T]:
        """트리를 순회하며 조건에 맞는 아이템 선택"""
        ...

class IMTTree(Protocol):
    """매크로 트리 인터페이스
    
    트리 구조와 조작을 위한 인터페이스입니다.
    """
    
    @property
    def id(self) -> str:
        """트리의 고유 식별자"""
        ...
    
    @property
    def name(self) -> str:
        """트리 이름"""
        ...
    
    @property
    def root_id(self) -> Optional[str]:
        """루트 아이템의 ID"""
        ...
    
    @property
    def items(self) -> Dict[str, IMTTreeItem]:
        """모든 트리 아이템"""
        ...
    
    def add_item(self, item: IMTTreeItem, parent_id: Optional[str] = None) -> bool:
        """아이템을 트리에 추가합니다.
        
        Args:
            item: 추가할 아이템
            parent_id: 부모 아이템 ID (없으면 루트에 추가)
            
        Returns:
            성공 여부
        """
        ...
    
    def remove_item(self, item_id: str) -> bool:
        """아이템을 트리에서 제거합니다.
        
        Args:
            item_id: 제거할 아이템의 ID
            
        Returns:
            성공 여부
        """
        ...
    
    def get_item(self, item_id: str) -> Optional[IMTTreeItem]:
        """지정된 ID의 아이템을 가져옵니다.
        
        Args:
            item_id: 아이템 ID
            
        Returns:
            아이템 또는 None
        """
        ...
    
    def get_children(self, parent_id: Optional[str]) -> List[IMTTreeItem]:
        """지정된 부모의 모든 자식 아이템을 가져옵니다.
        
        Args:
            parent_id: 부모 아이템 ID (None이면 루트 아이템들)
            
        Returns:
            자식 아이템 목록
        """
        ...
    
    def move_item(self, item_id: str, new_parent_id: Optional[str]) -> bool:
        """아이템을 새 부모로 이동합니다.
        
        Args:
            item_id: 이동할 아이템 ID
            new_parent_id: 새 부모 ID (None이면 루트로 이동)
            
        Returns:
            성공 여부
        """
        ...
    
    def traverse_dfs(self) -> Iterator[IMTTreeItem]:
        """깊이 우선 순회(DFS)로 트리를 순회합니다.
        
        Returns:
            아이템 이터레이터
        """
        ...
    
    def traverse_bfs(self) -> Iterator[IMTTreeItem]:
        """너비 우선 순회(BFS)로 트리를 순회합니다.
        
        Returns:
            아이템 이터레이터
        """
        ...
    
    def to_dict(self) -> Dict[str, Any]:
        """트리를 딕셔너리로 변환합니다.
        
        Returns:
            트리 데이터를 포함하는 딕셔너리
        """
        ...
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'IMTTree':
        """딕셔너리에서 트리를 생성합니다.
        
        Args:
            data: 트리 데이터 딕셔너리
            
        Returns:
            생성된 트리
        """
        ...
    
    def clone(self) -> 'IMTTree':
        """트리의 복제본을 생성합니다.
        
        Returns:
            복제된 트리
        """
        ...
    
    def subscribe(self, event_type: str, callback: Callable) -> None:
        """이벤트를 구독합니다.
        
        Args:
            event_type: 이벤트 유형
            callback: 이벤트 발생 시 호출할 콜백 함수
        """
        ...
    
    def unsubscribe(self, event_type: str, callback: Callable) -> None:
        """이벤트 구독을 해제합니다.
        
        Args:
            event_type: 이벤트 유형
            callback: 해제할 콜백 함수
        """
        ...