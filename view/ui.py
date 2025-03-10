"""사용자 인터페이스 모듈

애플리케이션의 메인 UI를 구성하는 클래스를 제공합니다.
"""
from typing import List, Callable
from PyQt5.QtWidgets import (
    QWidget, QHBoxLayout, QMainWindow, QMenuBar,
    QAction, QApplication
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import *
from view.tree_widget import TreeWidget
from enum import Enum
from resources.resources import *

class UI:
    """사용자 인터페이스 클래스
    
    애플리케이션의 메인 UI를 구성하고 관리합니다.
    """
    
    def __init__(self, window: QMainWindow, app: QApplication) -> None:
        """UI 생성자
        
        Args:
            window: 메인 윈도우 인스턴스
            app: 애플리케이션 인스턴스
        """
        self.window = window
        self.app = app
        self.setup_window(window, app)
        
        # 트리 위젯 설정
        self.tree_widget = None
        self.setup_tree()
        
        # 메뉴바 설정
        self.setup_menubar(self.tree_widget)
    
    def setup_window(self, window: QMainWindow, app: QApplication) -> None:
        """윈도우를 설정합니다.
        
        Args:
            window: 메인 윈도우 인스턴스
            app: 애플리케이션 인스턴스
        """
        # 윈도우 제목 설정
        window.setWindowTitle("Macro Tree")
        
        # 윈도우 크기 및 위치 설정
        x, y, width, height = rsc["win_geo"]
        window.setGeometry(x, y, width, height)
        
        # 중앙 위젯 설정
        central_widget = QWidget()
        window.setCentralWidget(central_widget)
        
        # 레이아웃 설정
        self.layout = QHBoxLayout(central_widget)
    
    def setup_tree(self) -> None:
        """트리 위젯을 설정합니다."""
        # 트리 위젯 생성
        self.tree_widget = TreeWidget(self.window)
        
        # 레이아웃에 트리 위젯 추가
        self.layout.addWidget(self.tree_widget)
    
    def setup_menubar(self, tree_widget: TreeWidget) -> None:
        """메뉴바를 설정합니다.
        
        Args:
            tree_widget: 트리 위젯 인스턴스
        """
        menubar = self.window.menuBar()
        
        # 파일 메뉴
        file_menu = menubar.addMenu("파일")
        
        # 저장 액션
        save_action = QAction("저장", self.window)
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(tree_widget.save_tree)
        file_menu.addAction(save_action)
        
        # 실행 메뉴
        exec_menu = menubar.addMenu("실행")
        
        # 실행 액션
        exec_action = QAction("실행", self.window)
        exec_action.setShortcut("F5")
        exec_action.triggered.connect(tree_widget.execute_selected_items)
        exec_menu.addAction(exec_action) 