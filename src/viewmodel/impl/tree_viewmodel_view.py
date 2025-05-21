from typing import Callable, List, Set

from core.interfaces.base_item_data import MTItemDomainDTO, MTItemUIStateDTO
from core.interfaces.base_tree import IMTTree, IMTTreeItem
from core.impl.utils import to_tree_item_data
from viewmodel.interfaces.base_tree_viewmodel_view import IMTTreeViewModelView

class MTTreeViewModelView(IMTTreeViewModelView):
    def __init__(self, tree=None, selected_items=None, notify_change: Callable[[], None] | None = None):
        self._tree:IMTTree | None = tree
        self._selected_items = selected_items if selected_items is not None else set()
        self._notify_change = notify_change if notify_change is not None else lambda: None

    def get_items(self) -> list[MTItemDomainDTO]:
        """UI에 표시할 아이템 목록을 반환합니다. (DFS 순회)"""
        tree = self.get_current_tree()
        if not tree:
            return []
        result = []
        # DFS(깊이 우선 탐색) 순회로 트리 아이템을 방문
        # RF : nested func. 여기서만 공유. Result 확인 용이. 깔끔한 코드
        def dfs(item: IMTTreeItem):
            parent_id = item.get_property("parent_id")
            if not (isinstance(parent_id, str) or parent_id is None):
                parent_id = None
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
        return True

    def get_current_tree(self) -> IMTTree | None:
        return self._tree

    def get_item(self, item_id: str) -> IMTTreeItem | None:
        tree = self.get_current_tree()
        if tree:
            return tree.get_item(item_id)
        return None

    def get_selected_items(self) -> list[str]:
        return list(self._selected_items)

    def get_item_children(self, parent_id: str | None = None) -> list[MTItemDomainDTO]:
        tree = self.get_current_tree()
        if not tree:
            return []
        result = []
        for child in tree.get_children(parent_id):
            result.append(
                to_tree_item_data(
                    child,
                    parent_id,
                    selected=(child.id in self._selected_items)
                )
            )
        return result

    def toggle_expanded(self, item_id: str, expanded: bool | None = None) -> bool:
        tree = self.get_current_tree()
        if not tree:
            return False
        item = tree.get_item(item_id)
        if not item:
            return False
        current = item.get_property("expanded", False)
        new_state = not current if expanded is None else expanded
        item.set_property("expanded", new_state)
        return True

    def clear_selection_state(self):
        """선택 상태를 초기화합니다."""
        if not self._selected_items:
            return # 변경 없으면 아무것도 안 함

        self._selected_items.clear()
        print("ViewModelView: Selection cleared.")