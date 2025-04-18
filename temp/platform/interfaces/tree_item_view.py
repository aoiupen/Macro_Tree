from typing import Protocol
from temp.platform.interfaces.ui_element import IMTUIElement
from temp.model.tree_item import IMTTreeItem

class IMTTreeItemView(IMTUIElement, Protocol):
    def bind_tree_item(self, item: IMTTreeItem) -> None: ...
    def set_indentation_level(self, level: int) -> None: ...
