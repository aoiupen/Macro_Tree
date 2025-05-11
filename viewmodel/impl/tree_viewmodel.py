from viewmodel.impl.tree_viewmodel_core import MTTreeViewModelCore
from viewmodel.impl.tree_viewmodel_model import MTTreeViewModelModel
from viewmodel.impl.tree_viewmodel_view import MTTreeViewModelView
from core.interfaces.base_tree import IMTTreeItem

class MTTreeViewModel:
    def __init__(self, tree, repository=None, state_manager=None):
        self._core: MTTreeViewModelCore = MTTreeViewModelCore(tree, repository, state_manager)
        self._model: MTTreeViewModelModel = MTTreeViewModelModel()
        self._view: MTTreeViewModelView = MTTreeViewModelView()
        self._ui_view = None  # 실제 View 인스턴스 (TreeView 등) 할당용

    def set_view(self, ui_view):
        self._ui_view = ui_view

    def on_tree_event(self, event_type, data):
        # 트리 이벤트에 따라 내부 상태 갱신 및 View에 신호 전달
        if self._ui_view:
            if event_type == 'ITEM_ADDED' or (hasattr(event_type, 'name') and event_type.name == 'ITEM_ADDED'):
                self._ui_view.on_viewmodel_signal('item_added', data)
            elif event_type == 'ITEM_REMOVED' or (hasattr(event_type, 'name') and event_type.name == 'ITEM_REMOVED'):
                self._ui_view.on_viewmodel_signal('item_removed', data)
            elif event_type == 'ITEM_MOVED' or (hasattr(event_type, 'name') and event_type.name == 'ITEM_MOVED'):
                self._ui_view.on_viewmodel_signal('item_moved', data)
            # 기타 이벤트 분기 추가 가능

    # 1. Core wrapper (비즈니스 로직/데이터 접근)
    def add_item(self, name: str, parent_id: str | None = None) -> str | None:
        return self._core.add_item(name, parent_id)
    def update_item(self, item_id: str, name: str | None = None, parent_id: str | None = None) -> bool:
        return self._core.update_item(item_id, name, parent_id)
    def remove_item(self, item_id: str) -> bool:
        return self._core.remove_item(item_id)
    def move_item(self, item_id: str, new_parent_id: str | None = None) -> bool:
        return self._core.move_item(item_id, new_parent_id)
    def get_tree_items(self):
        return self._core.get_tree_items()

    # 2. Model wrapper (상태/이벤트/저장/복원)
    def subscribe(self, callback):
        return self._model.subscribe(callback)
    def unsubscribe(self, callback):
        return self._model.unsubscribe(callback)
    def undo(self) -> bool:
        return self._model.undo()
    def redo(self) -> bool:
        return self._model.redo()
    def save_tree(self, tree_id: str | None = None) -> str | None:
        return self._model.save_tree(tree_id)
    def load_tree(self, tree_id: str) -> bool:
        return self._model.load_tree(tree_id)
    def can_undo(self) -> bool:
        return self._model.can_undo()
    def can_redo(self) -> bool:
        return self._model.can_redo()

    # 3. View wrapper (UI/조회/상태)
    def get_items(self) -> list:
        return self._view.get_items()
    def select_item(self, item_id: str, multi_select: bool = False) -> bool:
        return self._view.select_item(item_id, multi_select)
    def get_current_tree(self):
        return self._view.get_current_tree()
    def get_item(self, item_id: str):
        return self._view.get_item(item_id)
    def get_selected_items(self) -> list:
        return self._view.get_selected_items()
    def get_item_children(self, parent_id: str | None = None):
        return self._view.get_item_children(parent_id)
    def toggle_expanded(self, item_id: str, expanded: bool | None = None) -> bool:
        return self._view.toggle_expanded(item_id, expanded)
