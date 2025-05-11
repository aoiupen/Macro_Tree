from typing import Protocol, TypeVar, runtime_checkable
from .base_item_data import MTTreeItemData

# -------------------
# TreeItemKeys 분리: 도메인 키와 UI/확장/부가 키를 별도 관리
# - 도메인 키: core/interfaces/base_item_data.py
# - UI/확장/부가 키: core/interfaces/base_item.py
# -------------------


# 타입 변수 정의
# RF : 호출 시점에 타입이 결정
@runtime_checkable
class IMTBaseItem(Protocol):
    """기본 아이템 인터페이스"""
    @property
    def id(self) -> str: ...
    
    @property
    def data(self) -> MTTreeItemData: ...

# 트리 아이템 인터페이스
@runtime_checkable
class IMTTreeItem(IMTBaseItem, Protocol):
    """매크로 트리 아이템 인터페이스
    
    트리에서 사용되는 개별 아이템의 인터페이스입니다.
    """
    # id와 data 프로퍼티는 IMTBaseItem에서 이미 정의됨
    
    def get_property(self, key: str, default: object = None) -> object:
        """아이템 속성을 가져옵니다."""
        ...
    
    def set_property(self, key: str, value: object) -> None:
        """아이템 속성을 설정합니다."""
        ...
    
    def clone(self) -> 'IMTTreeItem':
        """아이템의 복제본을 생성합니다."""
        ...


