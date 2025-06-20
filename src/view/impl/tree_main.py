import sys
import os
from dotenv import load_dotenv
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QSplitter, QPushButton, QTreeWidget, QTreeWidgetItem
from PyQt6.QtGui import QAction, QKeySequence, QIcon
from PyQt6.QtCore import Qt

from core.impl.tree import MTTree
from core.impl.item import MTItem
from viewmodel.impl.tree_viewmodel import MTTreeViewModel
from view.impl.tree_view import TreeView
from model.state.impl.tree_state_mgr import MTTreeStateManager
from model.events.impl.tree_event_mgr import MTTreeEventManager
from core.interfaces.base_item_data import MTNodeType, MTItemDomainDTO, MTItemUIStateDTO, MTItemDTO
from model.events.interfaces.base_tree_event_mgr import MTTreeUIEvent   
from model.store.file.impl.file_tree_repo import MTFileTreeRepository
from model.store.store_manager import StoreManager

# MACRO_TREE_DEBUG 환경 변수 확인
load_dotenv() # .env 파일 로드, os.environ 접근 전에 호출
IS_DEBUG_MODE = os.environ.get('MACRO_TREE_DEBUG') == 'False'
print(f"IS_DEBUG_MODE: {IS_DEBUG_MODE}")
DEBUG_IMPORTS_SUCCESSFUL = False # 초기값
DebugManager = None # 초기값

if IS_DEBUG_MODE:
    try:
        from debug.debug_manager import DebugManager # 새로운 매니저 클래스
        DEBUG_IMPORTS_SUCCESSFUL = False
    except ImportError:
        print("디버그 매니저 로드 실패. 디버그 기능이 비활성화됩니다.")
        # DebugManager가 None으로 유지되므로, 이후 로직에서 이를 확인하여 처리합니다.

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Tree Application with Debug Viewers")
        self.event_manager = MTTreeEventManager()
        self.tree = MTTree(tree_id="root", name="Root Tree", event_manager=self.event_manager)
        self.repository = MTFileTreeRepository()
        self.store_manager = StoreManager(repository=self.repository) # MTFileTreeRepository 인스턴스(self.repository)를 직접 주입

        # 샘플 데이터: 그룹 1개와 그 하위에 INSTRUCTION 1개만 추가
        # group = MTItem("group-1", {"name": "Group 1", "node_type": MTNodeType.GROUP})
        # self.tree.add_item(group, None)
        # instr = MTItem("item-1", {"name": "Instruction 1", "node_type": MTNodeType.INSTRUCTION})
        # self.tree.add_item(instr, "group-1")

        # MTItemDomainDTO 및 MTItemUIStateDTO를 사용하여 아이템 추가
        # parent_id는 MTItemDomainDTO 내에 설정
        group_domain_data = MTItemDomainDTO(name="Group 1", node_type=MTNodeType.GROUP, parent_id=None, action_data=None) 
        group_ui_state_data = MTItemUIStateDTO(is_expanded=False, is_selected=False)
        group_item_dto = MTItemDTO(
            item_id="group-1",  # id -> item_id, 명시적 ID 사용
            domain_data=group_domain_data,
            ui_state_data=group_ui_state_data
        )
        # MTTree.add_item은 parent_id 인자를 받지 않음. item_dto에 parent_id가 설정되어야 함.
        group_id_added = self.tree.add_item(
            item_dto=group_item_dto 
        )

        # MTItemDomainDTO 및 MTItemUIStateDTO를 사용하여 아이템 추가 (자식 아이템)
        # instr_domain_data의 parent_id는 실제 부모의 ID (group_id_added)로 설정
        instr_domain_data = MTItemDomainDTO(name="Instruction 1", node_type=MTNodeType.INSTRUCTION, parent_id=group_id_added, action_data=None)
        instr_ui_state_data = MTItemUIStateDTO(is_expanded=False, is_selected=False)
        instr_item_dto = MTItemDTO(
            item_id="instr-1",  # id -> item_id, 명시적 ID 사용
            domain_data=instr_domain_data,
            ui_state_data=instr_ui_state_data
        )
        if group_id_added: 
            self.tree.add_item(
                item_dto=instr_item_dto
            )
        else:
            print("Error: Could not create group item, so instruction item will not be added.") 

        # ViewModel 생성 (parent=self 추가)
        self.state_manager = MTTreeStateManager(tree=self.tree) 


        self.viewmodel = MTTreeViewModel(
            tree=self.tree, 
            state_manager=self.state_manager, 
            event_manager=self.event_manager, 
            store_manager=self.store_manager,
            repository=self.repository, # 이 부분은 ViewModel 내부 로직에 따라 유지 또는 제거 가능 (StoreManager를 통해 접근한다면 제거 가능)
            parent=self
        )
        
        # ==== UI 구성 변경 시작 ====
        # 메인 트리 뷰 생성
        self.tree_view = TreeView(self.viewmodel)

        self.debug_manager_instance: 'DebugManager' | None = None # 타입 힌트

        if IS_DEBUG_MODE and DEBUG_IMPORTS_SUCCESSFUL and DebugManager is not None:
            self.debug_manager_instance = DebugManager(
                main_window=self,
                event_manager=self.event_manager,
                tree_model=self.tree,
                tree_view_widget=self.tree_view # MTTreeWidget이 아니라 TreeView를 전달 (get_id_to_widget_map 접근 위함)
            )
            
            # 레이아웃 설정
            # DebugManager가 QSplitter를 반환하도록 하고, 이를 중앙 위젯으로 설정
            central_splitter_widget = self.debug_manager_instance.setup_layout(self.tree_view)
            # QWidget으로 감싸야 setCentralWidget 가능
            container_widget = QWidget()
            layout = QVBoxLayout(container_widget)
            layout.addWidget(central_splitter_widget)
            layout.setContentsMargins(0,0,0,0)
            self.setCentralWidget(container_widget)
            
            self.resize(1200, 700)
            self.debug_manager_instance.update_all_viewers()
        else:
            # 디버깅 뷰어 없이 tree_view만 중앙 위젯으로 설정 (기존 로직)
            central_widget = QWidget()
            layout = QVBoxLayout(central_widget)
            layout.addWidget(self.tree_view)
            self.setCentralWidget(central_widget)

        self._setup_undo_redo_actions() # Undo/Redo 액션 설정 메서드 호출

        self.viewmodel.item_added.connect(self.tree_view.on_item_crud_slot)
        self.viewmodel.item_removed.connect(self.tree_view.on_item_crud_slot)
        self.viewmodel.item_moved.connect(self.tree_view.on_item_crud_slot)
        self.viewmodel.tree_reset.connect(self.tree_view.on_item_crud_slot)
        self.viewmodel.item_modified.connect(self.tree_view.on_item_crud_slot) 
        self.viewmodel.tree_state_changed.connect(self.tree_view.on_item_crud_slot) 
        self.viewmodel.tree_undo.connect(self.tree_view.on_tree_undoredo_slot)
        self.viewmodel.tree_redo.connect(self.tree_view.on_tree_undoredo_slot)

    def _setup_undo_redo_actions(self):
        undo_action = QAction("Undo", self)
        undo_action.setShortcut(QKeySequence("Ctrl+Z"))
        # ViewModel에 undo 메서드가 있다고 가정, 없다면 ViewModel에 추가 필요
        if hasattr(self.viewmodel, 'undo') and callable(self.viewmodel.undo):
            undo_action.triggered.connect(self.viewmodel.undo)
        else:
            print("Warning: MTTreeViewModel does not have an 'undo' method or it is not callable.")
            undo_action.setEnabled(False)
        self.addAction(undo_action)

        redo_action = QAction("Redo", self)
        redo_action.setShortcut(QKeySequence("Ctrl+Y"))
        # ViewModel에 redo 메서드가 있다고 가정, 없다면 ViewModel에 추가 필요
        if hasattr(self.viewmodel, 'redo') and callable(self.viewmodel.redo):
            redo_action.triggered.connect(self.viewmodel.redo)
        else:
            print("Warning: MTTreeViewModel does not have a 'redo' method or it is not callable.")
            redo_action.setEnabled(False)
        self.addAction(redo_action)

    def on_viewmodel_item_changed(self, data: dict):
        item_id_val = data.get("item_id") # id -> item_id
        new_name = data.get("name")
        print(f"MainWindow: Received item_modified signal for {item_id_val if item_id_val else '(item_id not in data)'} to {new_name if new_name else '(name not in data)'}")
        if self.debug_manager_instance:
            self.debug_manager_instance.update_on_item_changed()

    def closeEvent(self, event):
        if self.debug_manager_instance:
            self.debug_manager_instance.disconnect_events()
        if hasattr(self.viewmodel, 'item_modified'):
            try:
                self.viewmodel.item_modified.disconnect(self.on_viewmodel_item_changed)
            except TypeError:
                pass # RF: 의도된 동작일 수 있으므로 유지
        super().closeEvent(event)

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
