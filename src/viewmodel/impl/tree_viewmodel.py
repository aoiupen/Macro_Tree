from viewmodel.impl.tree_viewmodel_core import MTTreeViewModelCore
from viewmodel.impl.tree_viewmodel_model import MTTreeViewModelModel
from viewmodel.impl.tree_viewmodel_view import MTTreeViewModelView
from core.interfaces.base_tree import IMTTree
from model.events.interfaces.base_tree_event_mgr import MTTreeEvent
from model.events.interfaces.base_tree_event_mgr import IMTTreeEventManager
from core.interfaces.base_item_data import MTNodeType
from core.impl.tree import MTTree # MTTree 클래스 임포트
from PyQt6.QtCore import pyqtSignal, QObject # pyqtSignal 임포트, QObject 임포트
import copy # deepcopy를 위해 추가

"""
이 ViewModel은 Adapter 계층을 통해
프레임워크별 UI 이벤트를 공통 이벤트 Enum(MTTreeUIEvent)으로 전달받아 처리합니다.
"""
class MTTreeViewModel(QObject): # QObject 상속
    # ViewModel to View signals
    tree_structure_changed = pyqtSignal() # 전체 트리 구조 변경 시 (아이템 추가, 삭제, 이동)
    item_modified = pyqtSignal(dict) # 특정 아이템 내용 변경 시 (예: 이름 변경)
    item_properties_updated_signal = pyqtSignal(str, dict) # 특정 아이템 내용 변경 시 (아이템 ID, 변경된 속성 dict)
    selection_changed_signal = pyqtSignal(list) # 선택된 아이템 변경 시 (선택된 아이템 ID 목록)
    error_occurred = pyqtSignal(str) # 오류 발생 시
    view_changed = pyqtSignal() # 전체 뷰 업데이트가 필요할 때 사용할 시그널

    def __init__(self, tree: IMTTree, repository=None, state_manager=None, event_manager:IMTTreeEventManager | None=None, parent=None): # parent 인자 추가
        super().__init__(parent) # QObject 생성자 호출
        self._tree = tree
        self._state_mgr = state_manager # StateManager 인스턴스 저장
        self._event_manager = event_manager
        self._core: MTTreeViewModelCore = MTTreeViewModelCore(self._tree)
        self._model: MTTreeViewModelModel = MTTreeViewModelModel(self._tree)
        self._view: MTTreeViewModelView = MTTreeViewModelView(self._tree)
        self._ui_view = None

        if self._event_manager:
            print("[VM INIT DEBUG] ViewModel subscribing to core tree events.")
            events_to_subscribe = [
                MTTreeEvent.ITEM_ADDED,
                MTTreeEvent.ITEM_REMOVED,
                MTTreeEvent.ITEM_MOVED,
                MTTreeEvent.ITEM_MODIFIED,
                MTTreeEvent.TREE_RESET
            ]
            for event_type in events_to_subscribe:
                self._event_manager.subscribe(event_type, self.on_tree_mod_event)
        else:
            print("[VM INIT WARNING] Event manager not provided to ViewModel. Core events will not be handled.")

    # RF : 느슨하게 결합
    def set_view(self, ui_view):
        self._ui_view = ui_view

    def on_tree_mod_event(self, event_type, data):
        print(f"[VM EVENT DEBUG] on_tree_mod_event received: EventType={event_type}, Data={data}")
        # 트리 이벤트에 따라 내부 상태 갱신 및 View에 신호 전달
        if event_type == MTTreeEvent.ITEM_MODIFIED:
            self.item_properties_updated_signal.emit(data['item_id'], data) # ITEM_MODIFIED 이벤트 시 item_properties_updated_signal 시그널 발생
            # 기존 _ui_view 호출 로직은 유지하거나, 시그널 방식으로 통일할지 결정 필요
            # 여기서는 우선 시그널 발생만 추가하고, _ui_view.on_viewmodel_signal 호출은 그대로 둠

        if self._ui_view:
            print(f"[VM EVENT DEBUG] Forwarding event to _ui_view.on_viewmodel_signal: EventType={event_type}")
            if event_type == MTTreeEvent.ITEM_ADDED:
                self._ui_view.on_viewmodel_signal('item_added', data)
            elif event_type == MTTreeEvent.ITEM_REMOVED:
                self._ui_view.on_viewmodel_signal('item_removed', data)
            elif event_type == MTTreeEvent.ITEM_MOVED:
                self._ui_view.on_viewmodel_signal('item_moved', data)
            elif event_type == MTTreeEvent.TREE_RESET:
                self._ui_view.on_viewmodel_signal('tree_reset', data)
            elif event_type == MTTreeEvent.ITEM_MODIFIED: # 이 부분은 위에서 시그널로 처리했으므로 중복될 수 있음
                self._ui_view.on_viewmodel_signal('item_modified', data)

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
        if self._state_mgr and hasattr(self._tree, 'to_dict'): # MTTree에 to_dict() 메서드가 있다고 가정
            current_snapshot = copy.deepcopy(self._tree.to_dict()) # 상태 저장 전 스냅샷
            self._state_mgr.save_state(current_snapshot)
            
        actual_parent_id_for_core, insert_index = self._determine_parent_and_index_for_add(selected_potential_parent_id, new_item_node_type)

        result_id = self._core.add_item(name=name,
                                        parent_id=actual_parent_id_for_core,
                                        node_type=new_item_node_type,
                                        index=insert_index) # MTTreeViewModelCore.add_item에 index 파라미터 추가 필요 가정
        return result_id

    def update_item(self, item_id: str, name: str | None = None, parent_id: str | None = None) -> bool:
        if self._state_mgr and hasattr(self._tree, 'to_dict'):
            current_snapshot = copy.deepcopy(self._tree.to_dict())
            self._state_mgr.save_state(current_snapshot)
        result = self._core.update_item(item_id, name, parent_id)
        return result

    def remove_item(self, item_id: str) -> bool:
        if self._state_mgr and hasattr(self._tree, 'to_dict'):
            current_snapshot = copy.deepcopy(self._tree.to_dict())
            self._state_mgr.save_state(current_snapshot)
        result = self._core.remove_item(item_id)
        return result

    def move_item(self, item_id: str, new_parent_id: str | None = None, new_index: int = -1) -> bool: # index 추가
        if self._state_mgr and hasattr(self._tree, 'to_dict'):
            current_snapshot = copy.deepcopy(self._tree.to_dict())
            self._state_mgr.save_state(current_snapshot)
        # MTTreeViewModelCore.move_item에 index 파라미터 추가 필요 가정
        result = self._core.move_item(item_id, new_parent_id, new_index)
        return result

    def reset_tree(self):
        self._core.reset_tree()
            
    def get_tree_items(self):
        return self._core.get_tree_items()

    # 2. Model wrapper (상태/이벤트/저장/복원)
    def subscribe(self, callback):
        return self._model.subscribe(callback)
    def unsubscribe(self, callback):
        return self._model.unsubscribe(callback)
    def undo(self) -> bool:
        if self._state_mgr and self._state_mgr.can_undo():
            # 현재 상태를 Redo 스택에 저장하기 위해 현재 상태를 가져와야 함 (StateManager가 내부적으로 처리할 수도 있음)
            # 여기서는 StateManager가 undo 호출 시 현재 상태를 내부 Redo 스택에 넣는다고 가정.
            # 또는, undo 직전에 현재 상태를 save_state_for_redo 등으로 StateManager에 전달할 수도 있음.
            # 가장 간단하게는, StateManager.undo()가 (이전상태, 현재상태)를 반환하거나,
            # 이전 상태만 반환하고 StateManager가 알아서 현재 상태를 redo 스택에 넣는 것.

            # MTTreeStateManager.undo()가 복원할 스냅샷(딕셔너리)을 반환한다고 가정
            previous_snapshot = self._state_mgr.undo()
            if previous_snapshot:
                if hasattr(self._core, 'restore_tree_from_snapshot'): # MTTreeViewModelCore에 복원 메서드 필요
                    self._core.restore_tree_from_snapshot(previous_snapshot)
                    self.view_changed.emit() # View에 전체 변경 알림
                    # 또는 self._event_manager.publish(MTTreeEvent.TREE_RESET, previous_snapshot) 등
                    return True
                else:
                    print("Error: MTTreeViewModelCore.restore_tree_from_snapshot method not found.")
                    # 스냅샷은 가져왔으나 복원 실패 시, undo를 다시 취소해야 할 수도 있음 (복잡)
                    # 여기서는 일단 실패로 간주하고 False 반환
                    return False
        return False

    def redo(self) -> bool:
        if self._state_mgr and self._state_mgr.can_redo():
            # MTTreeStateManager.redo()가 복원할 스냅샷(딕셔너리)을 반환한다고 가정
            next_snapshot = self._state_mgr.redo()
            if next_snapshot:
                if hasattr(self._core, 'restore_tree_from_snapshot'): # MTTreeViewModelCore에 복원 메서드 필요
                    self._core.restore_tree_from_snapshot(next_snapshot)
                    self.view_changed.emit() # View에 전체 변경 알림
                    return True
                else:
                    print("Error: MTTreeViewModelCore.restore_tree_from_snapshot method not found.")
                    return False
        return False

    def can_undo(self) -> bool:
        return self._state_mgr.can_undo() if self._state_mgr else False

    def can_redo(self) -> bool:
        return self._state_mgr.can_redo() if self._state_mgr else False

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

    # _determine_parent_and_index_for_add와 같은 헬퍼 메서드는 내부적으로 사용되므로 여기에 정의
    def _determine_parent_and_index_for_add(self, selected_potential_parent_id: str | None, new_item_node_type: MTNodeType):
        actual_parent_id_for_core = None
        insert_index = -1 

        if not selected_potential_parent_id:
            actual_parent_id_for_core = self.get_dummy_root_id()
        else:
            selected_item_node_type = self.get_node_type(selected_potential_parent_id)
            if selected_item_node_type == MTNodeType.GROUP:
                actual_parent_id_for_core = selected_potential_parent_id
            elif selected_item_node_type == MTNodeType.INSTRUCTION:
                if self._core and hasattr(self._core, 'get_item_parent_id'):
                    grandparent_id = self._core.get_item_parent_id(selected_potential_parent_id)
                    actual_parent_id_for_core = grandparent_id
                    if actual_parent_id_for_core is not None and hasattr(self._core, 'get_children_ids'):
                        siblings = self._core.get_children_ids(actual_parent_id_for_core)
                        if selected_potential_parent_id in siblings:
                            try:
                                current_index = siblings.index(selected_potential_parent_id)
                                insert_index = current_index + 1
                            except ValueError:
                                insert_index = -1 
                        else:
                            insert_index = -1 
                    else:
                        insert_index = -1
                else:
                    actual_parent_id_for_core = selected_potential_parent_id # Fallback
            else:
                actual_parent_id_for_core = selected_potential_parent_id # Fallback
        return actual_parent_id_for_core, insert_index
