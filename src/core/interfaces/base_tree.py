"""
이 모듈은 매크로 트리의 트리 인터페이스(읽기, 수정, 순회, 직렬화, 복제 등)를 정의합니다.
"""
from typing import Any, Callable, Dict, List, Protocol
from core.interfaces.base_item import IMTItem
from core.interfaces.base_item_data import MTItemDTO
from abc import ABC, abstractmethod

class IMTTreeReadable (Protocol):
    """트리 데이터 액세스 인터페이스"""
    
    @property
    def id(self) -> str: ...
    
    @property
    def name(self) -> str: ...

    @property
    def root_id(self) -> str | None: ...

    @property
    def items(self) -> dict[str, IMTItem]: ...

    def get_item(self, item_id: str) -> IMTItem | None: ...
    
    def get_children(self, parent_id: str | None) -> List[IMTItem]: ...

# 트리 수정 작업 인터페이스
class IMTTreeModifiable(Protocol):
    """트리 수정 작업 인터페이스"""
    
    def add_item(self, item_dto: MTItemDTO, parent_id: str | None = None, index: int = -1) -> bool:
        """아이템을 트리에 추가합니다. Raises: ValueError-아이템 ID 중복 시"""
        ...
    
    def remove_item(self, item_id: str) -> bool:
        """아이템을 트리에서 제거합니다. Raises: ValueError-존재하지 않는 아이템 ID"""
        ...
    
    def move_item(self, item_id: str, new_parent_id: str | None) -> bool:
        """아이템을 새 부모로 이동합니다. Raises: ValueError-유효하지 않은 아이템/부모 ID"""
        ...
    
    def modify_item(self, item_id: str, item_dto: MTItemDTO) -> bool:
        """아이템의 속성을 변경합니다."""
        ...
    
    def reset_tree(self) -> None:
        """트리를 초기 상태로 리셋합니다."""
        ...

# 트리 순회 인터페이스
class IMTTreeTraversable(Protocol):
    """트리 순회 인터페이스"""
    
    def traverse(self, visitor: Callable[[IMTItem], None], 
                node_id: str | None = None) -> None:
        """트리를 BFS로 순회하면서 각 아이템에 방문자 함수를 적용합니다."""
        ...

class IMTTreeSerializable(Protocol):
    """
    트리 직렬화/역직렬화 인터페이스.
    구현 클래스는 dict_to_tree, json_to_tree 클래스 메서드도 제공해야 함 (규약 사항).
    """
    def to_dict(self) -> Dict[str, Any]:
        """트리를 딕셔너리로 변환합니다."""
        ...
    def tree_to_json(self) -> str:
        """트리 구조를 JSON 문자열로 직렬화합니다."""
        ...
    @abstractmethod
    def dict_to_state(self, data: Dict[str, Any]) -> None:
        """
        주어진 딕셔너리 데이터로부터 현재 트리 인스턴스의 상태를 복원합니다.
        이 메서드는 기존 인스턴스의 내용을 변경합니다.
        """
        ...
    @classmethod
    def dict_to_tree(cls, data: Dict[str, Any], event_manager: Any = None) -> 'IMTTree':
        ...
    @classmethod
    def json_to_tree(cls, json_str: str, event_manager: Any = None) -> 'IMTTree':
        ...

class IMTTreeClonable(Protocol):
    """트리 복제 인터페이스"""
    def clone(self) -> "IMTTree":
        """트리의 복제본을 생성합니다."""
        ...

# 통합 트리 인터페이스
class IMTTree(
    IMTTreeReadable,
    IMTTreeModifiable,
    IMTTreeTraversable,
    IMTTreeSerializable,
    IMTTreeClonable,
    Protocol
):
    """
    트리의 모든 핵심 기능(읽기, 수정, 순회, 직렬화, 복제)을 통합한 인터페이스.
    실무/협업/확장성을 고려할 때, 이 통합 인터페이스를 사용하는 것이 가장 표준적이고 유지보수에 유리함.
    구현 클래스는 from_dict, from_json 클래스 메서드도 제공해야 함 (규약 사항).
    """
    pass

class IMTTreeCommon(ABC):
    """트리 객체의 공통/필수 기능 인터페이스"""
    @abstractmethod
    def clone(self) -> "IMTTree":
        """트리의 복제본을 생성합니다."""
        ...

    @abstractmethod
    def restore_state(self, data: Dict[str, Any]) -> None:
        """
        주어진 딕셔너리 데이터로부터 트리 인스턴스의 상태를 복원합니다.
        이 메서드는 기존 인스턴스의 내용을 변경합니다.
        """
        ...