import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from PyQt6.QtCore import Qt

from core.impl.tree import MTTree
from core.impl.item import MTTreeItem
from viewmodel.impl.tree_viewmodel import TreeViewModel
from view.impl.tree_view import TreeView
from model.services.state.impl.tree_state_mgr import MTTreeStateManager

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(" Tree ")
        
        # 모델 생성
        # RF : 구현체끼리 서로 import는 순환참조 문제 등으로 피하는 것이 좋다
        # RF : 하지만, 최상위(MainWindow/앱/엔트리포인트/main.py)에서는 구현체를 선택해서 인스턴스를 만들기 때문에 구현체 import가 허용됨 
        self.tree = MTTree(tree_id="root", name="Root Tree")
        
        # 샘플 데이터 추가
        root_item = MTTreeItem("root", {"name": "Root Item"})
        self.tree.add_item(root_item)
        
        # 첫 번째 그룹
        group1 = MTTreeItem("group1", {"name": "Group 1"})
        self.tree.add_item(group1, "root")
        
        # 두 번째 그룹
        group2 = MTTreeItem("group2", {"name": "Group 2"})
        self.tree.add_item(group2, "root")
        
        # 그룹 1의 하위 항목
        for i in range(3):
            item = MTTreeItem(f"item-g1-{i}", {"name": f"Item {i} in Group 1"})
            self.tree.add_item(item, "group1")
        
        # 그룹 2의 하위 항목
        for i in range(2):
            item = MTTreeItem(f"item-g2-{i}", {"name": f"Item {i} in Group 2"})
            self.tree.add_item(item, "group2")
            
            # 서브 아이템 추가
            sub_item = MTTreeItem(f"item-g2-{i}-sub", {"name": f"Sub-item of {i}"})
            self.tree.add_item(sub_item, f"item-g2-{i}")
        
        # 루트 항목 확장 상태로 설정
        root_item.set_property("expanded", True)
        
        # ViewModel 생성
        self.state_manager = MTTreeStateManager()
        self.viewmodel = TreeViewModel(self.tree, self.state_manager)
        
        # 트리 뷰 생성 및 설정
        self.tree_view = TreeView(self.viewmodel)
        
        # 레이아웃 구성
        central_widget = QWidget()
        layout = QVBoxLayout(central_widget)
        layout.addWidget(self.tree_view)
        self.setCentralWidget(central_widget)
        
        self.resize(400, 300)
        
        self.current_file_path = ""


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
