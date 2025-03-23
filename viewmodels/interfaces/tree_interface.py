from typing import Protocol, runtime_checkable, Optional, List
from viewmodels.interfaces.item_interface import IItemViewModel

@runtime_checkable
class ITreeViewModel(Protocol):
    """트리 상태 관리 인터페이스
    
    트리 구조와 아이템 관리 작업을 정의합니다.
    """
    selected_items: List[str]
    
    def get_item(self, id: str) -> Optional[IItemViewModel]: ...
    def add_item(self, parent_id: str) -> str: ...
    def remove_item(self, id: str) -> bool: ...
    def get_children_ids(self, item_id: str) -> List[str]: ...
    # 기타 필요한 메서드...
