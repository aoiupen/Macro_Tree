from typing import Protocol, List
from core.interfaces.base_item_data import MTTreeItemData

class IMTTreeViewModelCore(Protocol):
    def get_items(self) -> List[MTTreeItemData]: ...
    def select_item(self, item_id: str, multi_select: bool = False) -> bool: ...
    # 기타 core 기반 필수 메서드 