from viewmodel.impl.tree_viewmodel_core import MTTreeViewModelCore
from viewmodel.impl.tree_viewmodel_model import MTTreeViewModelModel
from viewmodel.impl.tree_viewmodel_view import MTTreeViewModelView
from core.interfaces.base_tree import IMTTree
from model.events.interfaces.base_tree_event_mgr import MTTreeEvent
from model.events.interfaces.base_tree_event_mgr import IMTTreeEventManager

"""
이 ViewModel은 Adapter 계층을 통해
프레임워크별 UI 이벤트를 공통 이벤트 Enum(MTTreeUIEvent)으로 전달받아 처리합니다.
"""
class MTTreeViewModel:
    def __init__(self, tree: IMTTree, repository=None, state_manager=None, event_manager:IMTTreeEventManager | None=None):
        self._tree = tree
        self._core: MTTreeViewModelCore = MTTreeViewModelCore(self._tree)
        self._model: MTTreeViewModelModel = MTTreeViewModelModel()
        self._view: MTTreeViewModelView = MTTreeViewModelView(self._tree)
        self._event_manager = event_manager  # 이벤트 매니저 인스턴스 저장
        self._ui_view = None

        # 트리 이벤트 구독
        if self._event_manager:
            for event_type in MTTreeEvent:
                self._event_manager.subscribe(event_type, self.on_tree_mod_event)

    # RF : 느슨하게 결합
    def set_view(self, ui_view):
        self._ui_view = ui_view

    def on_tree_mod_event(self, event_type, data):
        # 트리 이벤트에 따라 내부 상태 갱신 및 View에 신호 전달
        if self._ui_view:
            if event_type == 'ITEM_ADDED' or (hasattr(event_type, 'name') and event_type.name == 'ITEM_ADDED'):
                self._ui_view.on_viewmodel_signal('item_added', data)
            elif event_type == 'ITEM_REMOVED' or (hasattr(event_type, 'name') and event_type.name == 'ITEM_REMOVED'):
                self._ui_view.on_viewmodel_signal('item_removed', data)
            elif event_type == 'ITEM_MOVED' or (hasattr(event_type, 'name') and event_type.name == 'ITEM_MOVED'):
                self._ui_view.on_viewmodel_signal('item_moved', data)
            elif event_type == 'TREE_RESET' or (hasattr(event_type, 'name') and event_type.name == 'TREE_RESET'):
                self._ui_view.on_viewmodel_signal('tree_reset', data)
            elif event_type == 'ITEM_MODIFIED' or (hasattr(event_type, 'name') and event_type.name == 'ITEM_MODIFIED'):
                self._ui_view.on_viewmodel_signal('item_modified', data)

    # RF : 만들었으나 pyqtboundsignal이 이미 있으므로 사용하지는 않음. 추후 크로스플랫폼 확장 시 사용 고려
    def on_tree_ui_event(self, event_type, data):
        if self._ui_view:
            if event_type == 'ITEM_SELECTED' or (hasattr(event_type, 'name') and event_type.name == 'ITEM_SELECTED'):
                self._ui_view.on_viewmodel_signal('item_selected', data)
            elif event_type == 'ITEM_EXPANDED' or (hasattr(event_type, 'name') and event_type.name == 'ITEM_EXPANDED'):
                self._ui_view.on_viewmodel_signal('item_expanded', data)
            elif event_type == 'ITEM_COLLAPSED' or (hasattr(event_type, 'name') and event_type.name == 'ITEM_COLLAPSED'):
                self._ui_view.on_viewmodel_signal('item_collapsed', data)
            # 기타 이벤트 분기 추가 가능

    # 1. Core wrapper (비즈니스 로직/데이터 접근)
    def add_item(self, name: str, parent_id: str | None = None, node_type: str = "INSTRUCTION") -> str | None:
        result = self._core.add_item(name, parent_id, node_type)
        if result and self._event_manager:
            self._event_manager.notify(MTTreeEvent.ITEM_ADDED, {"item_id": result, "name": name, "parent_id": parent_id})
        return result
    def update_item(self, item_id: str, name: str | None = None, parent_id: str | None = None) -> bool:
        result = self._core.update_item(item_id, name, parent_id)
        if result and self._event_manager:
            self._event_manager.notify(MTTreeEvent.ITEM_MODIFIED, {"item_id": item_id, "name": name, "parent_id": parent_id})
        return result
    def remove_item(self, item_id: str) -> bool:
        result = self._core.remove_item(item_id)
        if result and self._event_manager:
            self._event_manager.notify(MTTreeEvent.ITEM_REMOVED, {"item_id": item_id})
        return result
    def move_item(self, item_id: str, new_parent_id: str | None = None) -> bool:
        result = self._core.move_item(item_id, new_parent_id)
        if result and self._event_manager:
            self._event_manager.notify(MTTreeEvent.ITEM_MOVED, {"item_id": item_id, "new_parent_id": new_parent_id})
        return result
    def reset_tree(self):
        self._core.reset_tree()
        if self._event_manager:
            self._event_manager.notify(MTTreeEvent.TREE_RESET, {"tree": self._tree})
            
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
