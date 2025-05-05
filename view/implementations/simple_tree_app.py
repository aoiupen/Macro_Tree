import sys
import os
from pyqt6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QWidget, 
                          QFileDialog, QMessageBox, QAction, QMenuBar)
from pyqt6.QtCore import Qt

from ...model.impl.demo_tree import DemoTree
from ...model.impl.demo_tree_item import DemoTreeItem
from ...viewmodel.impl.demo_tree_viewmodel import DemoTreeViewModel
from .demo_tree_view import DemoTreeView

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Demo Tree Demo")
        
        # 모델 생성
        self.tree = DemoTree()
        
        # 샘플 데이터 추가
        root_item = DemoTreeItem("root", "Root Item")
        self.tree.add_item(root_item)
        
        # 첫 번째 그룹
        group1 = DemoTreeItem("group1", "Group 1")
        self.tree.add_item(group1, "root")
        
        # 두 번째 그룹
        group2 = DemoTreeItem("group2", "Group 2")
        self.tree.add_item(group2, "root")
        
        # 그룹 1의 하위 항목
        for i in range(3):
            item = DemoTreeItem(f"item-g1-{i}", f"Item {i} in Group 1")
            self.tree.add_item(item, "group1")
        
        # 그룹 2의 하위 항목
        for i in range(2):
            item = DemoTreeItem(f"item-g2-{i}", f"Item {i} in Group 2")
            self.tree.add_item(item, "group2")
            
            # 서브 아이템 추가
            sub_item = DemoTreeItem(f"item-g2-{i}-sub", f"Sub-item of {i}")
            self.tree.add_item(sub_item, f"item-g2-{i}")
        
        # 루트 항목 확장 상태로 설정
        root_item.set_property("expanded", True)
        
        # ViewModel 생성
        self.viewmodel = DemoTreeViewModel(self.tree)
        
        # 메뉴바 생성
        self._create_menus()
        
        # 트리 뷰 생성 및 설정
        self.tree_view = DemoTreeView(self.viewmodel)
        
        # 레이아웃 구성
        central_widget = QWidget()
        layout = QVBoxLayout(central_widget)
        layout.addWidget(self.tree_view)
        self.setCentralWidget(central_widget)
        
        self.resize(400, 300)
        
        self.current_file_path = ""
    
    def _create_menus(self):
        """메뉴바 생성"""
        menubar = self.menuBar()
        
        # 파일 메뉴
        file_menu = menubar.addMenu("파일")
        
        # 새 트리
        new_action = QAction("새로 만들기", self)
        new_action.setShortcut("Ctrl+N")
        new_action.triggered.connect(self._new_tree)
        file_menu.addAction(new_action)
        
        # 불러오기
        open_action = QAction("열기", self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self._open_file)
        file_menu.addAction(open_action)
        
        # 저장
        save_action = QAction("저장", self)
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self._save_file)
        file_menu.addAction(save_action)
        
        # 다른 이름으로 저장
        save_as_action = QAction("다른 이름으로 저장", self)
        save_as_action.setShortcut("Ctrl+Shift+S")
        save_as_action.triggered.connect(self._save_file_as)
        file_menu.addAction(save_as_action)
        
        file_menu.addSeparator()
        
        # 종료
        exit_action = QAction("종료", self)
        exit_action.setShortcut("Alt+F4")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
    
    def _new_tree(self):
        """새 트리 생성"""
        self.tree = DemoTree()
        self.viewmodel = DemoTreeViewModel(self.tree)
        self.tree_view.set_viewmodel(self.viewmodel)
        self.current_file_path = ""
        self.setWindowTitle("Demo Tree Demo")
    
    def _open_file(self):
        """파일 열기"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "트리 파일 열기", "", "JSON 파일 (*.json);;모든 파일 (*.*)"
        )
        
        if file_path:
            if self.viewmodel.load_tree(file_path):
                self.current_file_path = file_path
                self.setWindowTitle(f"Demo Tree Demo - {os.path.basename(file_path)}")
                self.tree_view.update_tree_items()
            else:
                QMessageBox.critical(self, "오류", "파일을 불러올 수 없습니다.")
    
    def _save_file(self):
        """현재 파일 저장"""
        if not self.current_file_path:
            self._save_file_as()
        else:
            self._save_to_path(self.current_file_path)
    
    def _save_file_as(self):
        """다른 이름으로 저장"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "트리 파일 저장", "", "JSON 파일 (*.json);;모든 파일 (*.*)"
        )
        
        if file_path:
            self._save_to_path(file_path)
    
    def _save_to_path(self, file_path):
        """지정된 경로에 저장"""
        if self.viewmodel.save_tree(file_path):
            self.current_file_path = file_path
            self.setWindowTitle(f"Demo Tree Demo - {os.path.basename(file_path)}")
        else:
            QMessageBox.critical(self, "오류", "파일을 저장할 수 없습니다.")

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
