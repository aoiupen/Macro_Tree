from typing import List, Protocol

from model.tree_item import IMTTreeItem
from platform.interfaces.collection_view import IMTCollectionView


class IMTTreeView(IMTCollectionView, Protocol):
    def expand_item(self, item_id: str) -> None: ...
    def collapse_item(self, item_id: str) -> None: ...
    def set_tree_data(self, items: List[IMTTreeItem]) -> None: ...
