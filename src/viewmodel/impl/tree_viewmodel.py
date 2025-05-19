from viewmodel.impl.tree_viewmodel_core import MTTreeViewModelCore
from viewmodel.impl.tree_viewmodel_model import MTTreeViewModelModel
from viewmodel.impl.tree_viewmodel_view import MTTreeViewModelView
from core.interfaces.base_tree import IMTTree
from model.state.interfaces.base_tree_state_mgr import IMTTreeStateManager
from model.events.interfaces.base_tree_event_mgr import MTTreeEvent
from model.events.interfaces.base_tree_event_mgr import IMTTreeEventManager
from core.interfaces.base_item_data import MTNodeType
from core.impl.tree import MTTree # MTTree 클래스 임포트
from PyQt6.QtCore import pyqtSignal, QObject # pyqtSignal 임포트, QObject 임포트
from typing import Any
from model.state.impl.tree_state_mgr import _format_tree_for_comprehension

"""
이 ViewModel은 Adapter 계층을 통해
프레임워크별 UI 이벤트를 공통 이벤트 Enum(MTTreeUIEvent)으로 전달받아 처리합니다.
"""
class MTTreeViewModel(QObject): # QObject 상속
    # (멤버 변수) pyqtsignal은 항상 클래스 변수(속성)으로 선언한다
    item_added = pyqtSignal(MTTreeEvent, dict)
    item_moved = pyqtSignal(MTTreeEvent, dict)
    item_removed = pyqtSignal(MTTreeEvent, dict)
    tree_reset = pyqtSignal(MTTreeEvent, dict)
    item_modified = pyqtSignal(MTTreeEvent, dict)
    tree_undo = pyqtSignal(MTTreeEvent, dict)
    tree_redo = pyqtSignal(MTTreeEvent, dict)

    def __init__(self, tree: IMTTree, state_manager: IMTTreeStateManager, event_manager: IMTTreeEventManager, repository=None, parent=None):
        # (멤버 변수) 인스턴스 변수 선언
        super().__init__(parent) # QObject 생성자 호출
        self._tree = tree
        self._core: MTTreeViewModelCore = MTTreeViewModelCore(self._tree)
        self._model: MTTreeViewModelModel = MTTreeViewModelModel(self._tree, state_manager=state_manager)
        self._view: MTTreeViewModelView = MTTreeViewModelView(self._tree)
        self._event_manager = event_manager

        events_to_subscribe = [
            MTTreeEvent.ITEM_ADDED,
            MTTreeEvent.ITEM_REMOVED,
            MTTreeEvent.ITEM_MOVED,
            MTTreeEvent.ITEM_MODIFIED,
            MTTreeEvent.TREE_RESET
        ]

        for event_type in events_to_subscribe:
            self._event_manager.subscribe(event_type, self.on_tree_mod_event)
            
        self._event_manager.subscribe(MTTreeEvent.TREE_CRUD, self.on_tree_crud_event)

        if self._model._state_mgr:
            self._model._state_mgr.subscribe(MTTreeEvent.TREE_UNDO, self.on_tree_undoredo_event)
            self._model._state_mgr.subscribe(MTTreeEvent.TREE_REDO, self.on_tree_undoredo_event)

    def on_tree_undoredo_event(self, event_type: MTTreeEvent, data: dict[str, Any]):
        if event_type == MTTreeEvent.TREE_UNDO:
            self.tree_undo.emit(event_type,data) # TREE_UNDO 이벤트 시 tree_undo 시그널 발생
        elif event_type == MTTreeEvent.TREE_REDO:
            self.tree_redo.emit(event_type,data) # TREE_REDO 이벤트 시 tree_redo 시그널 발생
            
        # data_from_state_manager는 StateManager로부터 받은 복원된 트리 스냅샷 (dict)
        if data:
            # MTTreeViewModelCore 인스턴스 (self._core)를 통해 restore_tree_from_snapshot 호출
            if hasattr(self, '_core') and self._core: # self._core가 MTTreeViewModelCore 인스턴스라고 가정
                self._core.restore_tree_from_snapshot(data) # data를 트리로 복원

    def on_tree_crud_event(self, event_type: MTTreeEvent, data: dict[str, Any]):
        if event_type == MTTreeEvent.TREE_CRUD:
            if hasattr(self._model, '_state_mgr') and self._model._state_mgr:
                new_stage = data.get("tree_data")
                if new_stage:
                    self._model._state_mgr.new_undo(new_stage)

    def on_tree_mod_event(self, event_type: MTTreeEvent, data: dict[str, Any]):
        # 트리 이벤트에 따라 내부 상태 갱신 및 View에 신호 전달
        if event_type == MTTreeEvent.ITEM_ADDED:
            self.item_added.emit(event_type,data) # ITEM_ADDED 이벤트 시 item_added 시그널 발생
        elif event_type == MTTreeEvent.ITEM_REMOVED:
            self.item_removed.emit(event_type,data) # ITEM_REMOVED 이벤트 시 item_removed 시그널 발생
        elif event_type == MTTreeEvent.ITEM_MOVED:
            self.item_moved.emit(event_type,data) # ITEM_MOVED 이벤트 시 item_moved 시그널 발생
        elif event_type == MTTreeEvent.TREE_RESET:
            self.tree_reset.emit(event_type,data) # TREE_RESET 이벤트 시 tree_reset 시그널 발생
        elif event_type == MTTreeEvent.ITEM_MODIFIED:
            self.item_modified.emit(event_type,data) # ITEM_MODIFIED 이벤트 시 item_modified 시그널 발생

    # 1. Core wrapper (비즈니스 로직/데이터 접근)
    def get_node_type(self, item_id: str) -> MTNodeType | None:
        # Core를 통해 아이템의 노드 타입을 가져옵니다.
        # 실제 구현은 MTTreeViewModelCore에 위임합니다.
        if self._core and hasattr(self._core, 'get_item_node_type'):
            return self._core.get_item_node_type(item_id)
        # 코어에 해당 메서드가 없다면 임시로 None 반환 또는 에러 처리
        print(f"Warning: MTTreeViewModelCore.get_item_node_type method not found.")
        return None

    def add_item(self, name: str, 
                 new_item_node_type: MTNodeType, # 새로 추가될 아이템의 타입
                 selected_potential_parent_id: str | None = None) -> str | None: # 선택된 아이템 ID
        actual_parent_id_for_core = None
        insert_index = -1 # -1은 보통 맨 뒤를 의미
        
        # print(f"[VM DEBUG] add_item called with: name='{name}', new_type='{new_item_node_type}', selected_id='{selected_potential_parent_id}'")

        if not selected_potential_parent_id:
            # 선택된 아이템이 없으면 최상위에 추가 (더미 루트의 자식으로)
            actual_parent_id_for_core = self.get_dummy_root_id() # Core의 더미 루트 ID를 사용해야 함
            # print(f"[VM DEBUG] No selected item. Adding to dummy root: {actual_parent_id_for_core}")
        else:
            # 선택된 아이템이 있으면, 해당 아이템의 타입을 가져온다.
            selected_item_node_type = self.get_node_type(selected_potential_parent_id)
            # print(f"[VM DEBUG] Selected item ID: {selected_potential_parent_id}, its type: {selected_item_node_type}")

            if selected_item_node_type == MTNodeType.GROUP:
                # 선택된 아이템이 그룹이면, 그 그룹의 자식으로 추가 (맨 뒤)
                actual_parent_id_for_core = selected_potential_parent_id
                # print(f"[VM DEBUG] Selected is GROUP. Adding as child to: {actual_parent_id_for_core}")
            elif selected_item_node_type == MTNodeType.INSTRUCTION:
                # 선택된 아이템이 인스트럭션이면, 그 아이템과 같은 레벨(형제)로, 바로 다음에 추가
                if self._core and hasattr(self._core, 'get_item_parent_id'):
                    grandparent_id = self._core.get_item_parent_id(selected_potential_parent_id)
                    actual_parent_id_for_core = grandparent_id # 실제 부모는 선택된 아이템의 부모
                    # print(f"[VM DEBUG] Selected is INSTRUCTION. Grandparent ID: {grandparent_id}")
                    
                    if actual_parent_id_for_core is not None and hasattr(self._core, 'get_children_ids'):
                        siblings = self._core.get_children_ids(actual_parent_id_for_core)
                        if selected_potential_parent_id in siblings:
                            try:
                                current_index = siblings.index(selected_potential_parent_id)
                                insert_index = current_index + 1
                                # print(f"[VM DEBUG] Found sibling at index {current_index}, inserting at {insert_index}")
                            except ValueError:
                                # print(f"[VM DEBUG] Warning: Could not find {selected_potential_parent_id} in siblings of {actual_parent_id_for_core}. Adding to end.")
                                insert_index = -1 
                        else:
                            # print(f"[VM DEBUG] Error: {selected_potential_parent_id} not found among siblings of {actual_parent_id_for_core}. Adding to end.")
                            insert_index = -1 
                    else:
                        # print(f"[VM DEBUG] Could not get siblings for {selected_potential_parent_id}. Adding to end of parent {actual_parent_id_for_core}.")
                        insert_index = -1
                else:
                    # print(f"[VM DEBUG] Warning: Necessary methods in MTTreeViewModelCore not found for sibling insertion. Adding as child to selected item.")
                    actual_parent_id_for_core = selected_potential_parent_id # 폴백: 선택된 아이템의 자식으로
            else:
                # print(f"[VM DEBUG] Warning: selected_item_node_type ('{selected_item_node_type}') is unexpected or None. Adding as child to {selected_potential_parent_id}.")
                # 알 수 없는 타입이거나, 타입 조회를 실패한 경우, 일단 선택된 아이템의 자식으로 추가 시도
                actual_parent_id_for_core = selected_potential_parent_id

        # Core 모델에 아이템 추가 요청
        # Core의 add_item은 (id, name, data, parent_id, index) 등을 받을 수 있어야 함.
        # 현재 MTTree.add_item은 MTTreeItem 객체와 parent_id, index를 받음.
        # 따라서 ViewModel에서 MTTreeItem 객체를 생성해야 함.
        new_item_data = {"name": name, "node_type": new_item_node_type} # Core에 전달할 데이터
        # print(f"[VM DEBUG] Preparing to call core.add_item with name='{name}', data='{new_item_data}', parent='{actual_parent_id_for_core}', index='{insert_index}'")

        if hasattr(self._core, 'add_item'): 
            # Core의 add_item이 (item_name, item_data, parent_id, index) 형태로 호출된다고 가정
            # 또는 (MTTreeItem 객체, parent_id, index)
            # 현재 self._core는 MTTreeViewModelCore의 인스턴스임.
            # MTTreeViewModelCore.add_item을 호출해야 함.
            # 이 메서드는 내부적으로 MTTreeItem을 생성하고 self._tree.add_item을 호출할 것.
            
            # MTTreeViewModelCore.add_item 실제 시그니처: (name: str, parent_id: str | None = None, node_type_to_add: MTNodeType | None = None)
            # index 파라미터는 현재 MTTreeViewModelCore.add_item에 없음.
            # MTTree.add_item은 index를 지원하므로, MTTreeViewModelCore를 수정하여 index를 전달할 수 있음.
            # 우선은 index 없이 호출 (맨 뒤에 추가됨)
            result_id = self._core.add_item(name=name, 
                                            parent_id=actual_parent_id_for_core, 
                                            index=insert_index,
                                            node_type=new_item_node_type)
        else:
            # print(f"[VM DEBUG] Error: MTTreeViewModelCore does not have a suitable add_item method.")
            result_id = None

        # print(f"[VM DEBUG] core.add_item returned: {result_id}")
        return result_id
        
    def update_item(self, item_id: str, name: str | None = None, parent_id: str | None = None) -> bool:
        result = self._core.update_item(item_id, name, parent_id)
        return result
    def remove_item(self, item_id: str) -> bool:
        result = self._core.remove_item(item_id)
        return result
    def move_item(self, item_id: str, new_parent_id: str | None = None) -> bool:
        result = self._core.move_item(item_id, new_parent_id)
        return result
    def reset_tree(self):
        self._core.reset_tree()
            
    def get_tree_items(self):
        return self._core.get_tree_items()

    # 2. Model wrapper (상태/이벤트/저장/복원)
    def subscribe(self, event_type, callback, source='model'):
        if source == 'model':
            return self._model.subscribe(event_type, callback)
        elif source == 'event':
            return self._event_manager.subscribe(event_type, callback)
        else:
            raise ValueError(f"Unknown event source: {source}")

    def unsubscribe(self, event_type, callback, source='model'):
        if source == 'model':
            return self._model.unsubscribe(event_type, callback)
        elif source == 'event':
            return self._event_manager.unsubscribe(event_type, callback)
        else:
            raise ValueError(f"Unknown event source: {source}")

    def new_undo(self, tree: IMTTree) -> bool:
        return self._model.new_undo(tree)
    def undo(self, tree: IMTTree) -> bool:
        return self._model.undo(tree)
    def redo(self, tree: IMTTree) -> bool:
        return self._model.redo(tree)
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
    def get_selected_items(self) -> list[str]:
        return self._view.get_selected_items()
    def get_item_children(self, parent_id: str | None = None):
        return self._view.get_item_children(parent_id)
    def toggle_expanded(self, item_id: str, expanded: bool | None = None) -> bool:
        return self._view.toggle_expanded(item_id, expanded)
    def clear_selection_state(self):
        self._view.clear_selection_state()

    def get_dummy_root_id(self) -> str | None:
        # MTTree에 접근하여 DUMMY_ROOT_ID를 반환하거나,
        # ViewModel이 생성될 때 Core로부터 DUMMY_ROOT_ID를 받아 저장해둘 수도 있음
        if self._core and hasattr(self._core, '_tree') and hasattr(self._core._tree, 'DUMMY_ROOT_ID'):
             return self._core._tree.DUMMY_ROOT_ID
        # 또는 직접 MTTree.DUMMY_ROOT_ID를 반환 (덜 유연한 방식)
        # return MTTree.DUMMY_ROOT_ID
        return None # 적절한 방법으로 ID를 가져와야 함
