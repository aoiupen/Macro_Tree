from typing import Protocol
from platforms.interfaces.ui_element import IMTUIElement
from core.interfaces.base_tree import IMTTreeItem

class IMTTreeItemView(IMTUIElement, Protocol):
    def bind_tree_item(self, item: IMTTreeItem) -> None: ...
    def set_indentation_level(self, level: int) -> None: ...
