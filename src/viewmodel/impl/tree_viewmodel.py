from viewmodel.impl.tree_viewmodel_core import MTTreeViewModelCore
from viewmodel.impl.tree_viewmodel_model import MTTreeViewModelModel
from viewmodel.impl.tree_viewmodel_view import MTTreeViewModelView
from core.interfaces.base_tree import IMTTree
from core.interfaces.base_tree import IMTItem
from core.interfaces.base_item_data import MTItemDomainDTO, MTNodeType, MTItemDTO
from model.state.interfaces.base_tree_state_mgr import IMTTreeStateManager
from model.events.interfaces.base_tree_event_mgr import MTTreeEvent
from model.events.interfaces.base_tree_event_mgr import IMTTreeEventManager
from model.store.repo.interfaces.base_tree_repo import IMTStore
from core.impl.tree import MTTree # MTTree 클래스 임포트
from PyQt6.QtCore import pyqtSignal, QObject # pyqtSignal 임포트, QObject 임포트
from typing import Any
import dataclasses

"""
트리 구조의 ViewModel 계층을 담당하는 클래스입니다.
Adapter 계층을 통해 프레임워크별 UI 이벤트를 공통 이벤트 Enum(MTTreeUIEvent)으로 전달받아 처리합니다.
트리의 상태 관리, 이벤트 처리, UI와의 데이터 바인딩을 담당합니다.
"""
class MTTreeViewModel(QObject): # QObject 상속
    # (멤버 변수) pyqtsignal은 항상 클래스 변수(속성)으로 선언한다
    item_added = pyqtSignal(MTTreeEvent, dict)
    item_moved = pyqtSignal(MTTreeEvent, dict)
    item_removed = pyqtSignal(MTTreeEvent, dict)
    tree_reset = pyqtSignal(MTTreeEvent, dict)
    item_modified = pyqtSignal(MTTreeEvent, dict) 
    tree_state_changed = pyqtSignal(MTTreeEvent, dict) 
    tree_undo = pyqtSignal(MTTreeEvent, dict)
    tree_redo = pyqtSignal(MTTreeEvent, dict)

    def __init__(self, tree: IMTTree, state_manager: IMTTreeStateManager, event_manager: IMTTreeEventManager, store_manager:IMTStore, repository: IMTStore, parent=None):
        """
        ViewModel을 초기화합니다.
        Args:
            tree (IMTTree): 트리 인스턴스
            state_manager (IMTTreeStateManager): 상태 관리자
            event_manager (IMTTreeEventManager): 이벤트 관리자
            repository: 저장소(선택)
            parent: 부모 QObject(선택)
        """
        # (멤버 변수) 인스턴스 변수 선언
        super().__init__(parent) # QObject 생성자 호출
        self._tree = tree
        self._repository = repository
        self._state_manager = state_manager
        self._event_manager = event_manager
        self._store_manager = store_manager
        self._core: MTTreeViewModelCore = MTTreeViewModelCore(self._tree)
        self._model: MTTreeViewModelModel = MTTreeViewModelModel(self._tree, self._state_manager, self._store_manager)
        self._view: MTTreeViewModelView = MTTreeViewModelView(self._tree)

        events_to_subscribe = [
            MTTreeEvent.ITEM_ADDED,
            MTTreeEvent.ITEM_REMOVED,
            MTTreeEvent.ITEM_MOVED,
            MTTreeEvent.ITEM_MODIFIED,
            MTTreeEvent.TREE_RESET
        ]

        for event_type in events_to_subscribe:
            self.subscribe(event_type, self.on_tree_mod, source='event')
        self.subscribe(MTTreeEvent.TREE_CRUD, self.on_tree_crud, source='event')

        if self._state_manager:
            self.subscribe(MTTreeEvent.TREE_UNDO, self.on_tree_undoredo, source='state')
            self.subscribe(MTTreeEvent.TREE_REDO, self.on_tree_undoredo, source='state')

    def on_tree_undoredo(self, event_type: MTTreeEvent, data: dict[str, Any]):
        """
        Undo/Redo 이벤트를 처리합니다.
        Args:
            event_type (MTTreeEvent): 이벤트 타입
            data (dict): 이벤트 데이터
        """
        if event_type == MTTreeEvent.TREE_UNDO:
            self.tree_undo.emit(event_type,data)
        elif event_type == MTTreeEvent.TREE_REDO:
            self.tree_redo.emit(event_type,data)
        if data:
            if hasattr(self, '_core') and self._core:
                self._core.restore_tree_from_snapshot(data)

    def on_tree_crud(self, event_type: MTTreeEvent, data: dict[str, Any]):
        """
        트리 CRUD 이벤트를 처리합니다. (주로 StateManager의 new_undo 호출 후 발생)
        이 이벤트는 트리에 변경이 있었고, 해당 변경이 undo 스택에 기록되었음을 의미합니다.
        ViewModel은 이 변경을 View에 알려 UI를 갱신해야 합니다.
        Args:
            event_type (MTTreeEvent): 이벤트 타입
            data (dict): 이벤트 데이터 (변경된 트리 상태 딕셔너리)
        """
        if event_type == MTTreeEvent.TREE_CRUD:
            self.tree_state_changed.emit(MTTreeEvent.TREE_CRUD, data)

    def on_tree_mod(self, event_type: MTTreeEvent, data: dict[str, Any]):
        """
        트리 구조 변경(추가/삭제/이동/수정/리셋) 이벤트를 처리합니다.
        Args:
            event_type (MTTreeEvent): 이벤트 타입
            data (dict): 이벤트 데이터
        """
        if event_type == MTTreeEvent.ITEM_ADDED:
            self.item_added.emit(event_type,data)
        elif event_type == MTTreeEvent.ITEM_REMOVED:
            self.item_removed.emit(event_type,data)
        elif event_type == MTTreeEvent.ITEM_MOVED:
            self.item_moved.emit(event_type,data)
        elif event_type == MTTreeEvent.TREE_RESET:
            self.tree_reset.emit(event_type,data)
        elif event_type == MTTreeEvent.ITEM_MODIFIED:
            self.item_modified.emit(event_type,data)

    # --- Core 위임 (비즈니스 로직/데이터 접근) ---
    def get_node_type(self, item_id: str) -> MTNodeType | None:
        """
        지정된 아이템의 노드 타입을 반환합니다.
        Args:
            item_id (str): 아이템 ID
        Returns:
            MTNodeType | None: 노드 타입 또는 None
        """
        if self._core and hasattr(self._core, 'get_item_node_type'):
            return self._core.get_item_node_type(item_id)
        return None

    def add_item(self, item_dto: MTItemDTO, selected_potential_parent_id: str | None = None) -> str | None:
        """
        새 트리 아이템을 추가합니다.
        Args:
            item_dto (MTItemDTO): 추가할 아이템 DTO
            selected_potential_parent_id (str | None): 부모 후보 아이디(선택)
        Returns:
            str | None: 추가된 아이템의 ID 또는 None
        """
        def get_parent_id_and_index(selected_id: str | None) -> tuple[str | None, int]:
            if not selected_id:
                return self.get_dummy_root_id(), -1
            
            core_item = self._core.get_item(selected_id)
            if not core_item:
                return self.get_dummy_root_id(), -1

            node_type = core_item.get_property("node_type")

            if node_type == MTNodeType.GROUP:
                return selected_id, -1
            
            if node_type == MTNodeType.INSTRUCTION:
                parent_id_of_selected = core_item.get_property("parent_id") 
                
                if parent_id_of_selected: 
                    parent_of_selected_item = self._core.get_item(parent_id_of_selected)
                    if parent_of_selected_item:
                        siblings_ids = parent_of_selected_item.get_property("children_ids", [])
                        try:
                            idx = siblings_ids.index(selected_id) + 1
                        except ValueError:
                            idx = -1
                        return parent_id_of_selected, idx
                return parent_id_of_selected, -1
            
            return self.get_dummy_root_id(), -1

        actual_parent_id, insert_index = get_parent_id_and_index(selected_potential_parent_id)
        
        if item_dto.domain_data.parent_id != actual_parent_id:
            new_domain_data = dataclasses.replace(item_dto.domain_data, parent_id=actual_parent_id)
            item_dto_with_parent = dataclasses.replace(item_dto, domain_data=new_domain_data)
        else:
            item_dto_with_parent = item_dto
            
        return self._core.add_item(item_dto=item_dto_with_parent, index=insert_index)

    def update_item(self, item_id: str, item_dto: MTItemDTO) -> bool:
        """
        아이템의 데이터를 수정합니다.
        Args:
            item_id (str): 아이템 ID
            item_dto (MTItemDTO): 새로운 데이터
        Returns:
            bool: 성공 여부
        """
        return self._core.update_item(item_id, item_dto)

    def remove_item(self, item_id: str) -> bool:
        """
        아이템을 트리에서 제거합니다.
        Args:
            item_id (str): 제거할 아이템 ID
        Returns:
            bool: 성공 여부
        """
        result = self._core.remove_item(item_id)
        return result

    def move_item(self, item_id: str, new_parent_id: str | None = None) -> bool:
        """
        아이템을 새 부모로 이동합니다.
        Args:
            item_id (str): 이동할 아이템 ID
            new_parent_id (str | None): 새 부모 ID(선택)
        Returns:
            bool: 성공 여부
        """
        result = self._core.move_item(item_id, new_parent_id)
        return result

    def reset_tree(self):
        """
        트리를 초기 상태로 리셋합니다.
        """
        tree = self._core._get_tree()
        if tree:
            tree.reset_tree()
            self.tree_reset.emit(MTTreeEvent.TREE_RESET, {})

    def get_tree_items(self) -> dict[str, IMTItem]:
        """
        트리의 모든 아이템을 딕셔너리로 반환합니다.
        Returns:
            dict[str, IMTItem]: 아이템 딕셔너리
        """
        return self._core.get_tree_items()

    # --- StateManager 위임 (상태/이벤트/저장/복원) ---
    def subscribe(self, event_type, callback, source='state'):
        """
        이벤트 또는 상태 변경을 구독합니다.
        Args:
            event_type: 이벤트 타입
            callback: 콜백 함수
            source (str): 'state' 또는 'event'
        Returns:
            구독 결과
        """
        if source == 'state':
            return self._state_manager.subscribe(event_type, callback)
        elif source == 'event':
            return self._event_manager.subscribe(event_type, callback)
        else:
            raise ValueError(f"Unknown event source: {source}")

    def unsubscribe(self, event_type, callback, source='state'):
        """
        이벤트 또는 상태 변경 구독을 해제합니다.
        Args:
            event_type: 이벤트 타입
            callback: 콜백 함수
            source (str): 'state' 또는 'event'
        Returns:
            구독 해제 결과
        """
        if source == 'state':
            return self._state_manager.unsubscribe(event_type, callback)
        elif source == 'event':
            return self._event_manager.unsubscribe(event_type, callback)
        else:
            raise ValueError(f"Unknown event source: {source}")

    def new_undo(self, tree: IMTTree) -> dict[str, Any]:
        """
        새 undo 스테이지를 추가합니다.
        Args:
            tree (IMTTree): 트리 인스턴스
        Returns:
            dict[str, Any]: 새 undo 스테이지 데이터
        """
        return self._state_manager.new_undo(tree)
    def undo(self, tree: IMTTree) -> dict[str, Any] | None:
        """
        undo(실행 취소)를 수행합니다.
        Args:
            tree (IMTTree): 트리 인스턴스
        Returns:
            dict[str, Any] | None: 이전 상태 데이터 또는 None
        """
        return self._state_manager.undo()
    def redo(self, tree: IMTTree) -> dict[str, Any] | None:
        """
        redo(다시 실행)을 수행합니다.
        Args:
            tree (IMTTree): 트리 인스턴스
        Returns:
            dict[str, Any] | None: 다음 상태 데이터 또는 None
        """
        return self._state_manager.redo()
    def can_undo(self) -> bool:
        """
        undo(실행 취소) 가능 여부를 반환합니다.
        Returns:
            bool: 가능 여부
        """
        return self._state_manager.can_undo()
    def can_redo(self) -> bool:
        """
        redo(다시 실행) 가능 여부를 반환합니다.
        Returns:
            bool: 가능 여부
        """
        return self._state_manager.can_redo()

    # --- View 위임 (UI/조회/상태) ---
    def get_items(self) -> list[MTItemDTO]:
        """View로부터 아이템 DTO 목록을 가져옵니다."""
        return self._view.get_items()

    def select_item(self, item_id: str, multi_select: bool = False) -> bool:
        """
        아이템을 선택하고, 변경 사항을 Undo/Redo 스택에 기록합니다.
        Args:
            item_id (str): 선택할 아이템의 ID
            multi_select (bool): 다중 선택 여부 (현재는 단일 선택만 완전 지원)
        Returns:
            bool: 성공 여부
        """
        succeeded = False
        item_to_select = self._core.get_item(item_id) 

        if not item_to_select:
            return False

        state_changed = False
        all_item_ids = list(self._core.get_all_item_dtos().keys())

        if not multi_select:
            for item_id_to_check in all_item_ids:
                if item_id_to_check == item_id:
                    continue 
                
                item_to_deselect = self._core.get_item(item_id_to_check)
                if item_to_deselect:
                    current_ui_state = item_to_deselect.ui_state 
                    if current_ui_state.is_selected:
                        current_ui_state.is_selected = False
                        item_to_deselect.ui_state = current_ui_state 
                        state_changed = True
        
        current_ui_state_selected_item = item_to_select.ui_state 
        if not current_ui_state_selected_item.is_selected:
            current_ui_state_selected_item.is_selected = True
            item_to_select.ui_state = current_ui_state_selected_item 
            state_changed = True
            succeeded = True
        elif multi_select: 
            current_ui_state_selected_item.is_selected = False
            item_to_select.ui_state = current_ui_state_selected_item 
            state_changed = True 
            succeeded = True 
        else: 
            succeeded = True

        if state_changed:
            tree_state_dict = self._core.to_dict()
            if tree_state_dict:
                self._state_manager.new_undo(tree_state_dict)
            else:
                print(f"Warning: Could not get tree state dict for undo in select_item for item {item_id}")
                succeeded = False 
        
        return succeeded

    def get_current_tree(self) -> IMTTree | None:
        """
        현재 트리 인스턴스를 반환합니다.
        Returns:
            IMTTree | None: 트리 인스턴스 또는 None
        """
        return self._view.get_current_tree()

    def get_item(self, item_id: str) -> MTItemDTO | None:
        """
        지정된 ID의 아이템 DTO를 반환합니다. (View 인터페이스 따름)
        Args:
            item_id (str): 아이템 ID
        Returns:
            MTItemDTO | None: 아이템 DTO 또는 None
        """
        return self._view.get_item_dto(item_id)

    def get_selected_items(self) -> list[str]:
        """
        현재 선택된 아이템들의 ID 리스트를 반환합니다.
        Returns:
            list[str]: 선택된 아이템 ID 리스트
        """
        return self._view.get_selected_items()

    def get_item_children(self, parent_id: str | None = None) -> list[MTItemDTO]:
        """
        지정된 부모 ID의 자식 아이템 데이터 MTItemDTO 리스트를 반환합니다.
        Args:
            parent_id (str | None): 부모 아이디(선택)
        Returns:
            list[MTItemDTO]: 자식 아이템 DTO 리스트
        """
        return self._view.get_item_children(parent_id)

    def get_item_dto(self, item_id: str) -> MTItemDTO | None:
        """지정된 ID의 아이템을 MTItemDTO로 반환합니다."""
        item: IMTItem | None = self._core.get_item(item_id)
        if item:
            return item.to_dto()
        return None

    def toggle_expanded(self, item_id: str, expanded: bool | None = None) -> bool:
        """
        아이템의 확장 상태를 토글하거나 지정된 상태로 설정하고, 변경 사항을 Undo/Redo 스택에 기록합니다.
        View에서 이 메서드를 호출하여 Core 상태를 변경합니다.
        Args:
            item_id (str): 상태를 변경할 아이템의 ID
            expanded (bool | None): 새로운 확장 상태. None이면 현재 상태를 반전.
        Returns:
            bool: 작업 성공 여부 (실제 상태 변경이 있었는지 여부와 다를 수 있음, 여기서는 Core 작업 성공 여부)
        """
        core_item = self._core.get_item(item_id) 
        if not core_item:
            return False

        current_ui_state = core_item.ui_state 
        
        new_expanded_state: bool
        if expanded is None: # 토글 동작
            new_expanded_state = not current_ui_state.is_expanded
        else: # 지정된 상태로 설정
            new_expanded_state = expanded
            
        if current_ui_state.is_expanded != new_expanded_state:
            current_ui_state.is_expanded = new_expanded_state
            core_item.ui_state = current_ui_state 
            
            tree_state_dict = self._core.to_dict()
            if tree_state_dict:
                self._state_manager.new_undo(tree_state_dict)
            else:
                print(f"Warning: Could not get tree state dict for undo in toggle_expanded for item {item_id}")
                return False # Undo 기록 실패 시 작업 실패로 간주 가능
            return True # 상태 변경 및 Undo 기록 성공
        return True # 상태 변경이 없었지만, 요청은 성공적으로 처리됨으로 간주

    def clear_selection_state(self) -> None:
        """
        선택 상태를 초기화합니다.
        """
        self._view.clear_selection_state()

    def get_dummy_root_id(self) -> str | None:
        """
        더미 루트 아이템의 ID를 반환합니다.
        Returns:
            str | None: 더미 루트 ID 또는 None
        """
        if self._core and hasattr(self._core, '_tree') and hasattr(self._core._tree, 'DUMMY_ROOT_ID'):
             return self._core._tree.DUMMY_ROOT_ID
        return None

    def save_tree(self, tree_id: str | None = None) -> str:
        """
        현재 트리 상태를 저장합니다.
        Args:
            tree_id (str | None): 저장할 트리의 ID(선택)
        Returns:
            str: 저장된 트리의 ID
        """
        current_tree_object = self._core._get_tree()
        if not current_tree_object:
            raise ValueError("현재 트리 객체를 가져올 수 없습니다.")
        return self._repository.save(current_tree_object, tree_id)

    def load_tree(self, tree_id: str) -> bool:
        """
        저장소에서 트리 데이터를 불러와 현재 트리 상태를 복원합니다.
        Args:
            tree_id (str): 불러올 트리의 ID (파일명)
        Returns:
            bool: 성공 여부
        """
        loaded_tree = self._repository.load(tree_id)
        if loaded_tree:
            if self._state_manager:
                self._state_manager.set_initial_state(loaded_tree)
            
            if self._event_manager:
                self._event_manager.notify(MTTreeEvent.TREE_RESET, {"tree_data": loaded_tree.to_dict()})
            return True
        return False

    def toggle_expanded_state(self, item_id: str, is_expanded: bool) -> None:
        """
        Core 아이템의 확장 상태를 변경하고, 변경 사항을 Undo/Redo 스택에 기록합니다.
        Args:
            item_id (str): 상태를 변경할 아이템의 ID
            is_expanded (bool): 새로운 확장 상태
        """
        core_item = self._core.get_item(item_id) 
        if core_item:
            current_ui_state = core_item.ui_state # MTItemUIStateDTO (deepcopy)
            if current_ui_state.is_expanded != is_expanded:
                current_ui_state.is_expanded = is_expanded
                core_item.ui_state = current_ui_state # setter (deepcopy)
                
                # 변경된 전체 트리 상태를 Undo 스택에 저장
                current_tree_snapshot = self._core.to_dict() # MTTreeViewModelCore의 to_dict() 사용
                if current_tree_snapshot:
                    self._state_manager.new_undo(current_tree_snapshot)
                else:
                    print(f"Warning: Could not get tree snapshot for undo in toggle_expanded_state for item {item_id}")

    def get_all_item_dtos(self) -> dict[str, MTItemDTO]:
        """
        트리의 모든 아이템 DTO를 딕셔너리로 반환합니다.
        Returns:
            dict[str, MTItemDTO]: 아이템 DTO 딕셔너리
        """
        return self._core.get_all_item_dtos()
