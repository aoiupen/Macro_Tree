"""메인 윈도우 모듈

애플리케이션의 메인 윈도우를 정의합니다.
"""
from typing import List, Callable
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QMenuBar, QAction, QApplication
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import *
from typing import Optional
from view.tree import TreeWidget
from core.tree_state_interface import ITreeStateManager
from core.tree_state_manager import TreeStateManager
from core.tree_state import TreeState
from resources.resources import rsc


class MainWindow(QMainWindow):
    """메인 윈도우 클래스
    
    애플리케이션의 주 윈도우를 구성합니다.
    """

    def __init__(self, app: QApplication = None, 
                 state_manager: Optional[ITreeStateManager] = None):
        """MainWindow 생성자
        
        Args:
            app: 애플리케이션 인스턴스 (선택적)
        """
        super().__init__()
        self.app = app

        # 상태 관리자 생성 : 선택적 의존성 주입
        self._state_manager = state_manager or TreeStateManager()

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
    
    def setup_window(self):
        """윈도우를 설정합니다."""
        # 윈도우 제목 설정
        self.setWindowTitle("Macro Tree")
        
        # 윈도우 크기 및 위치 설정
        if "win_geo" in rsc:
            x, y, width, height = rsc["win_geo"]
            self.setGeometry(x, y, width, height)
        else:
            self.resize(800, 600)
    
    def setup_tree(self):
        """트리 위젯을 설정합니다."""
        # 트리 위젯 생성
        self._tree_widget = TreeWidget(self, state_manager=self._state_manager)
        
        # 레이아웃에 트리 위젯 추가
        self.layout.addWidget(self._tree_widget)
        
        # 상태 변경 시그널 연결
        self._tree_widget.stateChanged.connect(self._on_tree_state_changed)
        self._state_manager.stateChanged.connect(self._on_state_manager_changed)
    
    def setup_menubar(self):
        """메뉴바를 설정합니다."""
        menubar = self.menuBar()
        
        # 파일 메뉴
        file_menu = menubar.addMenu("파일")
        
        # 저장 액션
        save_action = QAction("저장", self)
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self._tree_widget.save_tree)
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
    
    def _on_tree_state_changed(self, tree_state: TreeState):
        """트리 상태가 변경되었을 때 호출됩니다.
        
        Args:
            tree_state: 변경된 트리 상태
        """
        self._state_manager.save_state(tree_state)
        self._update_action_states()
    
    def _on_state_manager_changed(self):
        """상태 관리자의 상태가 변경되었을 때 호출됩니다."""
        self._update_action_states()
    
    def _update_action_states(self):
        """Undo/Redo 액션의 활성화 상태를 업데이트합니다."""
        self._undo_action.setEnabled(self._state_manager.can_undo())
        self._redo_action.setEnabled(self._state_manager.can_redo())
    
    def _undo(self):
        """이전 상태로 되돌립니다."""
        if state := self._state_manager.undo():
            self._tree_widget.restore_state(state)
    
    def _redo(self):
        """다음 상태로 복원합니다."""
        if state := self._state_manager.redo():
            self._tree_widget.restore_state(state) 