from typing import List, Protocol

from core.interfaces.base_item import IMTItem
from core.interfaces.base_item_data import MTNodeType, MTItemDTO, MTItemDomainDTO, MTItemUIStateDTO

class IMTTreeViewModelCore(Protocol):
    """트리 뷰모델 인터페이스 - 플랫폼 독립적 (Core)"""
    
    def __init__(self, tree):
        """ViewModel 초기화"""
        ...

    # 1. 데이터 접근/조회
    def get_all_item_dtos(self) -> dict[str, MTItemDTO]: ...

    # 2. CRUD/비즈니스 로직
    def add_item(self, item_dto: MTItemDTO, index: int = -1) -> str | None: ...
    def update_item(self, item_id: str, item_dto: MTItemDTO) -> bool: ...
    def remove_item(self, item_id: str) -> bool: ...
    def move_item(self, item_id: str, new_parent_id: str | None = None) -> bool: ...
