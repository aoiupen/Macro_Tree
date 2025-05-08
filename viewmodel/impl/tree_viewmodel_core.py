from viewmodel.interfaces.base_tree_viewmodel_core import IMTTreeViewModelCore
from core.interfaces.base_item_data import MTTreeItemData
from core.interfaces.base_tree import IMTTreeItem
from core.impl.utils import to_tree_item_data
from typing import List

class MTTreeViewModelCore(IMTTreeViewModelCore):
    def get_items(self) -> list[MTTreeItemData]:
        """UI에 표시할 아이템 목록을 반환합니다."""
        tree = self.get_current_tree()
        if not tree:
            return []
        result = []
        def visitor(item: IMTTreeItem) -> None:
            parent_id = None
            for pid, children in tree._children_map.items():
                if item.id in children:
                    parent_id = pid
                    break
            
            result.append(
                to_tree_item_data(
                    item,
                    parent_id,
                    selected=(item.id in self._selected_items)
                )
            )
        
        tree.traverse(visitor)

        return result
    def select_item(self, item_id: str, multi_select: bool = False) -> bool:
        """아이템을 선택합니다.
        
        Args:
            item_id: 선택할 아이템 ID
            multi_select: 다중 선택 모드
            
        Returns:
            성공 여부
        """
        tree = self.get_current_tree()
        if not tree or not tree.get_item(item_id):
            return False
        
        # 다중 선택이 아니면 기존 선택 초기화
        if not multi_select:
            self._selected_items.clear()
        
        # 선택 토글
        if item_id in self._selected_items:
            self._selected_items.remove(item_id)
        else:
            self._selected_items.add(item_id)
        
        self._notify_change()
        return True