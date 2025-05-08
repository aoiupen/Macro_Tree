from viewmodel.interfaces.base_tree_viewmodel_core import IMTTreeViewModelCore
from core.interfaces.base_item_data import MTTreeItemData
from typing import List

class MTTreeViewModelCore(IMTTreeViewModelCore):
    def get_items(self) -> List[MTTreeItemData]:
        # 예시: 트리의 모든 아이템을 반환
        return []

    def select_item(self, item_id: str, multi_select: bool = False) -> bool:
        # 예시: 아이템 선택
        return False 