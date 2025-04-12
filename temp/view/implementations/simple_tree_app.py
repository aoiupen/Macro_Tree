import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QTreeWidget, QTreeWidgetItem, QVBoxLayout, QWidget
from PyQt5.QtCore import Qt

from ...model.implementations.simple_tree import SimpleTree
from ...model.implementations.simple_tree_item import SimpleTreeItem
from ...viewmodel.implementations.simple_tree_viewmodel import SimpleTreeViewModel

class SimpleTreeView(QTreeWidget):
    def __init__(self, viewmodel: SimpleTreeViewModel, parent=None):
        super().__init__(parent)
        self._viewmodel = viewmodel
        self.itemClicked.connect(self._on_item_clicked)
        self.setHeaderLabel("트리 아이템")
        self._update_display()
    
    def _update_display(self):
        self.clear()
        items = self._viewmodel.get_items_for_display()
        for item_data in items:
            tree_item = QTreeWidgetItem()
            tree_item.setText(0, item_data["name"])
            tree_item.setData(0, Qt.UserRole, item_data["id"])
            if item_data.get("selected", False):
                tree_item.setSelected(True)
            self.addTopLevelItem(tree_item)
    
    def _on_item_clicked(self, item, column):
        item_id = item.data(0, Qt.UserRole)
        self._viewmodel.select_item(item_id)
        self._update_display()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Simple Tree Demo")
        
        # 모델 생성
        self.tree = SimpleTree()
        
        # 샘플 데이터 추가
        for i in range(7):
            item = SimpleTreeItem(f"item-{i}", f"Items {i}")
            self.tree.add_item(item)
        
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
