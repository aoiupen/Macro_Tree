from enum import Enum
from typing import Any, Callable, Dict, Generic, Iterator, List, Protocol, TypeVar

from core.interfaces.base_item import IMTTreeItem

# 타입 변수 선언
T = TypeVar('T')
T_co = TypeVar('T_co', covariant=True)  # 공변성 타입 변수

# 트리 메타데이터 인터페이스
class IMTTreeReadable (Protocol[T]):
    """트리 데이터 액세스 인터페이스"""
    
    @property
    def id(self) -> str: ...
    
    @property
    def name(self) -> str: ...
    
    @property
    def root_id(self) -> str | None: ...
    
    def get_all_items(self) -> Dict[str, T]: ...
    
    def get_item(self, item_id: str) -> T | None: ...
    
    def get_children(self, parent_id: str | None) -> List[T]: ...

# 트리 수정 작업 인터페이스
class IMTTreeModifiable(Protocol):
    """트리 수정 작업 인터페이스"""
    
    def add_item(self, item: IMTTreeItem, parent_id: str | None = None) -> bool:
        """아이템을 트리에 추가합니다. Raises: ValueError-아이템 ID 중복 시"""
        ...
    
    def remove_item(self, item_id: str) -> bool:
        """아이템을 트리에서 제거합니다. Raises: ValueError-존재하지 않는 아이템 ID"""
        ...
    
    def move_item(self, item_id: str, new_parent_id: str | None) -> bool:
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
                node_id: str | None = None) -> None:
        """트리를 BFS로 순회하면서 각 아이템에 방문자 함수를 적용합니다."""
        ...

# 통합 트리 인터페이스
class IMTTree(IMTTreeReadable, IMTTreeModifiable, IMTTreeTraversable, Protocol):
    """매크로 트리 통합 인터페이스"""
    pass

# RF : 직렬/역직렬은 Tree의 핵심 기능은 아닌데, Tree 내부 기능이므로 core에 놓음
class IMTTreeSerializable(Protocol):
    """트리 기본 직렬화 인터페이스"""
    
    def to_dict(self) -> Dict[str, Any]:
        """트리를 딕셔너리로 변환합니다."""
        ...
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> IMTTree:
        """딕셔너리에서 트리를 생성합니다."""
        ...
    
    def clone(self) -> IMTTree:
        """트리의 복제본을 생성합니다."""
        ...

class IMTTreeJSONSerializable(Protocol):
    """트리 JSON 직렬화 인터페이스"""
    
    def to_json(self) -> str:
        """트리를 JSON 문자열로 변환합니다."""
        ...
    
    @classmethod
    def from_json(cls, json_str: str) -> IMTTree:
        """JSON 문자열에서 트리를 생성합니다. 
        
        Raises:
            ValueError: 잘못된 JSON 형식
        """
        ...