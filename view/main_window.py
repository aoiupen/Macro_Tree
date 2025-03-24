"""메인 윈도우 모듈

애플리케이션의 메인 윈도우를 정의합니다.
"""
from typing import List, Callable, Optional
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QMenuBar, QApplication
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction
from view.tree import TreeWidget
from core.tree_state import TreeState
from viewmodels.tree_data_repository_viewmodel import TreeDataRepositoryViewModel
from viewmodels.interfaces.repository_viewmodel_interface import IRepositoryViewModel
from resources.resources import rsc


class MainWindow(QMainWindow):
    """메인 윈도우 클래스
    
    애플리케이션의 주 윈도우를 구성합니다.
    """

    def __init__(self, app: QApplication = None, 
                 repository_viewmodel: Optional[IRepositoryViewModel] = None):
        """MainWindow 생성자
        
        Args:
            app: 애플리케이션 인스턴스 (선택적)
            repository_viewmodel: 저장소 뷰모델 (선택적)
        """
        super().__init__()
        self.app = app

        # 저장소 뷰모델 생성 또는 사용
        self._repository_viewmodel = repository_viewmodel or TreeDataRepositoryViewModel()

        # 윈도우 설정
        self.setup_window()
        
        # 중앙 위젯 설정
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        self.layout = QHBoxLayout(central_widget)
        
        # 트리 위젯 설정
        self.setup_tree()
        
        # 메뉴바 설정
        self.setup_menubar()
        
        # 단축키 설정
        self.setup_shortcuts()
        
        # 뷰모델 이벤트 연결
        self._repository_viewmodel.stateChanged.connect(self._on_tree_state_changed)
    
    def setup_window(self):
        """윈도우를 설정합니다."""
        # 윈도우 제목 설정
        self.setWindowTitle("Macro Tree")
        
        # 윈도우 크기 및 위치 설정
        self.resize(800, 600)
        self.setMinimumSize(640, 480)
        self.center_on_screen()
    
    def center_on_screen(self):
        """윈도우를 화면 중앙에 배치합니다."""
        available_geometry = self.screen().availableGeometry()
        self.move(
            (available_geometry.width() - self.width()) // 2,
            (available_geometry.height() - self.height()) // 2
        )
    
    def setup_tree(self):
        """트리 위젯을 설정합니다."""
        # 트리 위젯 초기화
        self._tree_widget = TreeWidget(self, repository_viewmodel=self._repository_viewmodel)
        
        # 레이아웃에 추가
        self.layout.addWidget(self._tree_widget)
        
        # 트리 상태 변경 시그널 연결
        self._tree_widget.stateChanged.connect(self._on_tree_state_changed)
    
    def setup_menubar(self):
        """메뉴바를 설정합니다."""
        menubar = self.menuBar()
        
        # 파일 메뉴
        file_menu = menubar.addMenu("파일")
        
        # 새로 만들기 액션
        new_action = QAction("새로 만들기", self)
        new_action.setShortcut("Ctrl+N")
        new_action.triggered.connect(self._new_tree)
        file_menu.addAction(new_action)
        
        # 불러오기 액션
        load_action = QAction("불러오기", self)
        load_action.setShortcut("Ctrl+O")
        load_action.triggered.connect(self._load_tree)
        file_menu.addAction(load_action)
        
        # 구분선
        file_menu.addSeparator()
        
        # 저장 액션
        save_action = QAction("저장", self)
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self._save_tree)
        file_menu.addAction(save_action)
        
        # 실행 메뉴
        exec_menu = menubar.addMenu("실행")
        
        # 실행 액션
        exec_action = QAction("실행", self)
        exec_action.setShortcut("F5")
        exec_action.triggered.connect(self._tree_widget.execute_selected_items)
        exec_menu.addAction(exec_action)
    
    def setup_shortcuts(self):
        """단축키를 설정합니다."""
        # Undo (Ctrl+Z)
        self._undo_action = self.addAction("Undo")
        self._undo_action.setShortcut(Qt.CTRL + Qt.Key_Z)
        self._undo_action.triggered.connect(self._undo)
        
        # Redo (Ctrl+Y)
        self._redo_action = self.addAction("Redo")
        self._redo_action.setShortcut(Qt.CTRL + Qt.Key_Y)
        self._redo_action.triggered.connect(self._redo)
        
        # 단축키 상태 초기화
        self._update_action_states()
    
    def _new_tree(self):
        """새 트리를 생성합니다."""
        if self._repository_viewmodel.create_new_tree():
            current_state = self._repository_viewmodel.get_current_state()
            if current_state:
                self._tree_widget.restore_state(current_state)
                print("새 트리가 생성되었습니다.")
    
    def _load_tree(self):
        """데이터베이스에서 트리를 로드합니다."""
        if self._repository_viewmodel.load_tree_from_db():
            current_state = self._repository_viewmodel.get_current_state()
            if current_state:
                self._tree_widget.restore_state(current_state)
                print("트리를 성공적으로 로드했습니다.")
        else:
            print("트리를 로드할 수 없습니다.")
    
    def _save_tree(self):
        """현재 트리 상태를 저장합니다."""
        if self._repository_viewmodel.save_current_tree():
            print("트리가 성공적으로 저장되었습니다.")
        else:
            print("트리를 저장하는데 실패했습니다.")
    
    def _on_tree_state_changed(self, tree_state: TreeState):
        """트리 상태가 변경되었을 때 호출됩니다.
        
        Args:
            tree_state: 변경된 트리 상태
        """
        self._repository_viewmodel.save_state(tree_state)
        self._update_action_states()
    
    def _update_action_states(self):
        """Undo/Redo 액션의 활성화 상태를 업데이트합니다."""
        self._undo_action.setEnabled(self._repository_viewmodel.can_undo())
        self._redo_action.setEnabled(self._repository_viewmodel.can_redo())
    
    def _undo(self):
        """이전 상태로 되돌립니다."""
        if self._repository_viewmodel.undo():
            current_state = self._repository_viewmodel.get_current_state()
            if current_state:
                self._tree_widget.restore_state(current_state)
    
    def _redo(self):
        """다음 상태로 복원합니다."""
        if self._repository_viewmodel.redo():
            current_state = self._repository_viewmodel.get_current_state()
            if current_state:
                self._tree_widget.restore_state(current_state) 