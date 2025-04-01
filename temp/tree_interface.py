from typing import Protocol, Iterator, List, Optional, TypeVar, Generic, Callable, Dict, Any
from temp.tree_item_interface import IMTTreeItem, TreeItemData
from enum import Enum

class MTTreeEvent(Enum):
    """트리 이벤트 유형"""
    ITEM_ADDED = "item_added"
    ITEM_REMOVED = "item_removed"
    ITEM_MODIFIED = "item_modified"
    ITEM_MOVED = "item_moved"
    TREE_RESET = "tree_reset"

# 명확한 콜백 타입 정의
TreeEventCallback = Callable[[MTTreeEvent, Dict[str, Any]], None]

# 트리 메타데이터 인터페이스
class ITreeMetadata(Protocol):
    """트리 메타데이터 인터페이스"""
    
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

# 트리 읽기 작업 인터페이스
class ITreeReadable(Protocol):
    """트리 읽기 작업 인터페이스"""
    
    @property
    def items(self) -> Dict[str, IMTTreeItem]:
        """모든 트리 아이템"""
        ...
    
    def get_item(self, item_id: str) -> Optional[IMTTreeItem]:
        """지정된 ID의 아이템을 가져옵니다."""
        ...
    
    def get_children(self, parent_id: Optional[str]) -> List[IMTTreeItem]:
        """지정된 부모의 모든 자식 아이템을 가져옵니다."""
        ...

# 트리 수정 작업 인터페이스
class ITreeModifiable(Protocol):
    """트리 수정 작업 인터페이스"""
    
    def add_item(self, item: IMTTreeItem, parent_id: Optional[str] = None) -> bool:
        """아이템을 트리에 추가합니다. Raises: ValueError-아이템 ID 중복 시"""
        ...
    
    def remove_item(self, item_id: str) -> bool:
        """아이템을 트리에서 제거합니다. Raises: ValueError-존재하지 않는 아이템 ID"""
        ...
    
    def move_item(self, item_id: str, new_parent_id: Optional[str]) -> bool:
        """아이템을 새 부모로 이동합니다. Raises: ValueError-유효하지 않은 아이템/부모 ID"""
        ...

# 트리 순회 인터페이스
class ITreeTraversable(Protocol):
    """트리 순회 인터페이스"""
    
    def traverse_dfs(self) -> Iterator[IMTTreeItem]:
        """깊이 우선 순회(DFS)로 트리를 순회합니다."""
        ...
    
    def traverse_bfs(self, parent_id: Optional[str] = None) -> Iterator[IMTTreeItem]:
        """너비 우선 순회(BFS)로 트리를 순회합니다."""
        ...

# 트리 직렬화 인터페이스
class ITreeSerializable(Protocol):
    """트리 직렬화 인터페이스"""
    
    def to_dict(self) -> Dict[str, Any]:
        """트리를 딕셔너리로 변환합니다."""
        ...
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'IMTTree':
        """딕셔너리에서 트리를 생성합니다."""
        ...
    
    def clone(self) -> 'IMTTree':
        """트리의 복제본을 생성합니다."""
        ...

# 트리 이벤트 관리 인터페이스
class ITreeObservable(Protocol):
    """트리 이벤트 관리 인터페이스"""
    
    def subscribe(self, event_type: MTTreeEvent, callback: TreeEventCallback) -> None:
        """이벤트를 구독합니다."""
        ...
    
    def unsubscribe(self, event_type: MTTreeEvent, callback: TreeEventCallback) -> None:
        """이벤트 구독을 해제합니다."""
        ...

# 필터링 기능이 있는 고급 순회 인터페이스
T = TypeVar('T', bound=IMTTreeItem)
class ITreeAdvancedTraversable(Protocol, Generic[T]):
    """확장된 매크로 트리 순회 인터페이스 - 필터링 기능 포함"""
    
    def traverse_filtered(self, predicate: Callable[[T], bool]) -> Iterator[T]:
        """트리를 순회하며 조건에 맞는 아이템 선택"""
        ...

# 통합 트리 인터페이스
class IMTTree(ITreeMetadata, ITreeReadable, ITreeModifiable, ITreeTraversable, ITreeSerializable, ITreeObservable, Protocol):
    """매크로 트리 통합 인터페이스"""
    pass