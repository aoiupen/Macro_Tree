from typing import Protocol, List
from core.interfaces.base_tree import IMTTree, IMTItem

from core.interfaces.base_item_data import MTItemDomainDTO, MTItemDTO

class IMTTreeViewModelView(Protocol):
    def get_items(self) -> List[MTItemDTO]: ...
    def select_item(self, item_id: str, multi_select: bool = False) -> bool: ...
    def get_current_tree(self) -> IMTTree | None: ...
    def get_item_dto(self, item_id: str) -> MTItemDTO | None: ...
    def get_selected_items(self) -> list[str]: ...
    def get_item_children(self, parent_id: str | None = None) -> list[MTItemDTO]: ...
    def toggle_expanded(self, item_id: str, expanded: bool | None = None) -> bool: ...
    # 기타 view 기반 필수 메서드 