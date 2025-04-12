import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from PyQt5.QtCore import Qt

from ...model.implementations.simple_tree import SimpleTree
from ...model.implementations.simple_tree_item import SimpleTreeItem
from ...viewmodel.implementations.simple_tree_viewmodel import SimpleTreeViewModel
from .simple_tree_view import SimpleTreeView

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Simple Tree Demo")
        
        # 모델 생성
        self.tree = SimpleTree()
        
        # 샘플 데이터 추가
        root_item = SimpleTreeItem("root", "Root Item")
        self.tree.add_item(root_item)
        
        # 첫 번째 그룹
        group1 = SimpleTreeItem("group1", "Group 1")
        self.tree.add_item(group1, "root")
        
        # 두 번째 그룹
        group2 = SimpleTreeItem("group2", "Group 2")
        self.tree.add_item(group2, "root")
        
        # 그룹 1의 하위 항목
        for i in range(3):
            item = SimpleTreeItem(f"item-g1-{i}", f"Item {i} in Group 1")
            self.tree.add_item(item, "group1")
        
        # 그룹 2의 하위 항목
        for i in range(2):
            item = SimpleTreeItem(f"item-g2-{i}", f"Item {i} in Group 2")
            self.tree.add_item(item, "group2")
            
            # 서브 아이템 추가
            sub_item = SimpleTreeItem(f"item-g2-{i}-sub", f"Sub-item of {i}")
            self.tree.add_item(sub_item, f"item-g2-{i}")
        
        # 루트 항목 확장 상태로 설정
        root_item.set_property("expanded", True)
        
        # ViewModel 생성
        self.viewmodel = SimpleTreeViewModel(self.tree)
        
        # 트리 뷰 생성 및 설정
        self.tree_view = SimpleTreeView(self.viewmodel)
        
        # 레이아웃 구성
        central_widget = QWidget()
        layout = QVBoxLayout(central_widget)
        layout.addWidget(self.tree_view)
        self.setCentralWidget(central_widget)
        
        self.resize(400, 300)

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
