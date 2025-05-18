import sys
import os
from dotenv import load_dotenv
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QSplitter, QPushButton, QTreeWidget, QTreeWidgetItem
from PyQt6.QtGui import QAction, QKeySequence, QIcon
from PyQt6.QtCore import Qt

from core.impl.tree import MTTree
from core.impl.item import MTTreeItem
from viewmodel.impl.tree_viewmodel import MTTreeViewModel
from view.impl.tree_view import TreeView
from model.state.impl.tree_state_mgr import MTTreeStateManager
from model.events.impl.tree_event_mgr import MTTreeEventManager
from core.interfaces.base_item_data import MTNodeType
from model.events.interfaces.base_tree_event_mgr import MTTreeUIEvent   

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
                
        # 샘플 데이터: 그룹 1개와 그 하위에 INSTRUCTION 1개만 추가
        group = MTTreeItem("group-1", {"name": "Group 1", "node_type": MTNodeType.GROUP})
        self.tree.add_item(group, None)
        instr = MTTreeItem("item-1", {"name": "Instruction 1", "node_type": MTNodeType.INSTRUCTION})
        self.tree.add_item(instr, "group-1")

        # ViewModel 생성 (parent=self 추가)
        self.state_manager = MTTreeStateManager(tree=self.tree) 

        self.viewmodel = MTTreeViewModel(
            tree=self.tree, 
            repository=None, # 필요에 따라 
            state_manager=self.state_manager, 
            event_manager=self.event_manager, 
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

        self.viewmodel.item_added.connect(self.tree_view.on_viewmodel_signal)
        self.viewmodel.item_removed.connect(self.tree_view.on_viewmodel_signal)
        self.viewmodel.item_moved.connect(self.tree_view.on_viewmodel_signal)
        self.viewmodel.tree_reset.connect(self.tree_view.on_viewmodel_signal)
        self.viewmodel.item_modified.connect(self.tree_view.on_viewmodel_signal)
        self.viewmodel.tree_undo.connect(self.tree_view.on_tree_undoredo_signal)
        self.viewmodel.tree_redo.connect(self.tree_view.on_tree_undoredo_signal)

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

        # 선택: 메뉴에도 추가 (예시)
        # edit_menu = self.menuBar().addMenu("&Edit")
        # edit_menu.addAction(undo_action)
        # edit_menu.addAction(redo_action)

    def on_viewmodel_item_changed(self, data: dict):
        item_id = data.get("id")
        new_name = data.get("name")
        print(f"MainWindow: Received item_modified signal for {item_id} to {new_name if new_name else '(name not in data)'}")
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
