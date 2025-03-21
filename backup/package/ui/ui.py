"""사용자 인터페이스 모듈

애플리케이션의 메인 UI를 구성하는 클래스를 제공합니다.
"""
from typing import List, Callable
from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QMainWindow, QMenuBar,
    QAction, QApplication
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import *
from package import tree_widget as tr
from enum import Enum
from package.resources.resources import *

class UI:
    """사용자 인터페이스 클래스
    
    애플리케이션의 메인 UI를 구성하고 관리합니다.
    """

    def __init__(self, window: QMainWindow, app: QApplication) -> None:
        """UI 생성자
        
        Args:
            window: 메인 윈도우 인스턴스
            app: QApplication 인스턴스
        """
        super().__init__()
        self.column_count = 5
        self.column_width = 10

        self.setup_window(window, app)
        self.setup_tree()
        self.setup_menubar(self.tree_widget)
        self.tree_widget.load_from_db()
        
    def setup_window(self, window: QMainWindow, app: QApplication) -> None:
        """메인 윈도우를 설정합니다.
        
        Args:
            window: 메인 윈도우 인스턴스
            app: QApplication 인스턴스
        """
        self.app = app
        self.window = window
        self.window.setWindowTitle("Macro")
        self.window.setGeometry(*rsc["win_geo"])
        self.central_widget = QWidget()
        self.central_layout = QHBoxLayout(self.central_widget)
        self.window.setCentralWidget(self.central_widget)

    def setup_tree(self) -> None:
        """트리 위젯을 설정합니다."""
        self.tree_widget = tr.TreeWidget(self)
        self.tree_widget.setColumnCount(self.column_count)
        self.tree_widget.setHeaderLabels(rsc["header"])
        self.tree_widget.setColumnWidth(1, self.column_width)
        self.central_layout.addWidget(self.tree_widget)

    def setup_menubar(self, tree_widget: tr.TreeWidget) -> None:
        """메뉴바를 설정합니다.
        
        Args:
            tree_widget: 트리 위젯 인스턴스
        """
        # 메뉴바 생성
        self.menubar = self.window.menuBar()
        self.menubar.setNativeMenuBar(False)
        
        # 파일 메뉴 설정
        self.menubar_file = self.menubar.addMenu('&File')
        menu_items = [
            ("Save", 'Ctrl+S', tree_widget.save_to_db),
            ("Load", 'Ctrl+L', tree_widget.load_from_db),
            ("Execute", 'Ctrl+E', tree_widget.exec_inst),
            ("Exit", 'Ctrl+Q', QApplication.quit)
        ]
        
        for name, shortcut, func in menu_items:
            action = QAction(name, self.window)
            action.setShortcut(shortcut)
            action.triggered.connect(func)
            self.menubar_file.addAction(action)