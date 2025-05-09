from viewmodel.interfaces.base_tree_viewmodel_core import IMTTreeViewModelCore
from core.interfaces.base_item_data import MTTreeItemData
from core.interfaces.base_tree import IMTTreeItem
from core.impl.utils import to_tree_item_data
from typing import List

class MTTreeViewModelCore(IMTTreeViewModelCore):
    def get_items(self) -> list[MTTreeItemData]:
        """UI에 표시할 아이템 목록을 반환합니다. (DFS 순회)"""
        tree = self.get_current_tree()
        if not tree:
            return []
        result = []
        # DFS(깊이 우선 탐색) 순회로 트리 아이템을 방문
        def dfs(item: IMTTreeItem):
            parent_id = item.get_property("parent_id")
            result.append(
                to_tree_item_data(
                    item,
                    parent_id,
                    selected=(item.id in self._selected_items)
                )
            )
            # 자식 아이템들을 재귀적으로 방문
            for child in tree.get_children(item.id):
                dfs(child)
        # 루트 아이템부터 DFS 시작
        root_id = tree.root_id
        if root_id:
            root_item = tree.get_item(root_id)
            if root_item:
                dfs(root_item)
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