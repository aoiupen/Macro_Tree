from enum import Enum
from typing import (
    Any,
    Callable,
    Dict,
    Generic,
    Iterator,
    List,
    Optional,
    Protocol,
    TypeVar,
    runtime_checkable,
)

from temp.model.tree_item import IMTTreeItem, TreeItemData


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
class IMTTreeMetadata(Protocol):
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
T = TypeVar('T')
@runtime_checkable
class IMTTreeReadable(Protocol[T]):
    """트리 읽기 작업 인터페이스"""
    
    def get_all_items(self) -> Dict[str, T]:
        """모든 트리 아이템"""
        ...
    
    def get_item(self, item_id: str) -> Optional[T]:
        """지정된 ID의 아이템을 가져옵니다."""
        ...
    
    def get_children(self, parent_id: Optional[str]) -> List[T]:
        """지정된 부모의 모든 자식 아이템을 가져옵니다."""
        ...

# 트리 수정 작업 인터페이스
class IMTTreeModifiable(Protocol):
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
    
    def modify_item(self, item_id: str, changes: Dict[str, Any]) -> bool:
        """아이템의 속성을 변경합니다."""
        ...
    
    def reset_tree(self) -> None:
        """트리를 초기 상태로 리셋합니다."""
        ...

# 트리 순회 인터페이스
class IMTTreeTraversable(Protocol):
    """트리 순회 인터페이스"""
    
    def traverse(self, visitor: Callable[[IMTTreeItem], None], 
                node_id: Optional[str] = None) -> None:
        """트리를 BFS로 순회하면서 각 아이템에 방문자 함수를 적용합니다."""
        ...

# 트리 직렬화 인터페이스
class IMTTreeSerializable(Protocol):
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
class IMTTreeObservable(Protocol):
    """트리 이벤트 관리 인터페이스"""
    
    def subscribe(self, event_type: MTTreeEvent, callback: TreeEventCallback) -> None:
        """이벤트를 구독합니다."""
        ...
    
    def unsubscribe(self, event_type: MTTreeEvent, callback: TreeEventCallback) -> None:
        """이벤트 구독을 해제합니다."""
        ...

# 필터링 기능이 있는 고급 순회 인터페이스
T_co = TypeVar('T_co', covariant=True)
class IMTTreeAdvancedTraversable(Protocol, Generic[T_co]):
    """확장된 매크로 트리 순회 인터페이스 - 필터링 기능 포함"""
    
    def traverse_filtered(self, predicate: Callable[[T_co], bool]) -> Iterator[T_co]:
        """트리를 순회하며 조건에 맞는 아이템 선택"""
        ...

# 통합 트리 인터페이스
class IMTTree(IMTTreeMetadata, IMTTreeReadable, IMTTreeModifiable, IMTTreeTraversable, IMTTreeSerializable, IMTTreeObservable, Protocol):
    """매크로 트리 통합 인터페이스"""
    pass