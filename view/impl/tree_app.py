import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from PyQt6.QtCore import Qt

from core.impl.tree import MTTree
from core.impl.item import MTTreeItem
from viewmodel.impl.tree_viewmodel import MTTreeViewModel
from view.impl.tree_view import TreeView
from model.state.impl.tree_state_mgr import MTTreeStateManager
from model.events.impl.tree_event_mgr import MTTreeEventManager
from model.events.interfaces.base_tree_event_mgr import MTTreeEvent
from core.interfaces.base_item_data import MTNodeType

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(" Tree ")
        
        # 모델 생성
        # RF : 구현체끼리 서로 import는 순환참조 문제 등으로 피하는 것이 좋다
        # RF : 하지만, 최상위(MainWindow/앱/엔트리포인트/main.py)에서는 구현체를 선택해서 인스턴스를 만들기 때문에 구현체 import가 허용됨 
        self.tree = MTTree(tree_id="root", name="Root Tree")
        
        # 샘플 데이터 추가
        root_item = MTTreeItem("root", {"name": "Root Item", "node_type": MTNodeType.GROUP})
        self.tree.add_item(root_item, None)
        
        # 첫 번째 그룹
        group1 = MTTreeItem("group1", {"name": "Group 1", "node_type": MTNodeType.GROUP})
        self.tree.add_item(group1, "root")
        
        # group1에 INSTRUCTION 3개 추가
        for i in range(3):
            instr = MTTreeItem(f"item-g1-{i}", {"name": f"Item {i} in Group 1", "node_type": MTNodeType.INSTRUCTION})
            self.tree.add_item(instr, "group1")
        
        # 두 번째 그룹
        group2 = MTTreeItem("group2", {"name": "Group 2", "node_type": MTNodeType.GROUP})
        self.tree.add_item(group2, "root")

        # group2의 하위 폴더(subgroup2) 추가
        subgroup2 = MTTreeItem("subgroup2", {"name": "Sub Group 2", "node_type": MTNodeType.GROUP})
        self.tree.add_item(subgroup2, "group2")

        # 그룹 2의 하위 항목 (INSTRUCTION 아래에는 자식 추가 X)
        group2_items = []
        for i in range(4):
            item = MTTreeItem(f"item-g2-{i}", {"name": f"Item {i} in Group 2", "node_type": MTNodeType.INSTRUCTION})
            group2_items.append(item)
        # 절반은 group2에, 절반은 subgroup2에 추가
        for i, item in enumerate(group2_items):
            if i < len(group2_items) // 2:
                self.tree.add_item(item, "group2")
            else:
                self.tree.add_item(item, "subgroup2")
        # 서브 아이템은 group2와 subgroup2에 각각 추가 (INSTRUCTION 아래 X)
        for i in range(2):
            sub_item = MTTreeItem(f"item-g2-{i}-sub", {"name": f"Sub-item of {i}", "node_type": MTNodeType.INSTRUCTION})
            self.tree.add_item(sub_item, "group2")
        for i in range(2, 4):
            sub_item = MTTreeItem(f"item-g2-{i}-sub", {"name": f"Sub-item of {i}", "node_type": MTNodeType.INSTRUCTION})
            self.tree.add_item(sub_item, "subgroup2")
        
        # 루트 항목 확장 상태로 설정
        root_item.set_property("expanded", True)
        
        # ViewModel 생성
        self.state_manager = MTTreeStateManager()
        self.event_manager = MTTreeEventManager()
        self.viewmodel = MTTreeViewModel(self.tree, None, self.state_manager, self.event_manager)
        
        # 트리 뷰 생성 및 설정
        self.tree_view = TreeView(self.viewmodel)
        
        # 레이아웃 구성
        central_widget = QWidget()
        layout = QVBoxLayout(central_widget)
        layout.addWidget(self.tree_view)
        self.setCentralWidget(central_widget)
        
        self.resize(400, 300)
        
        self.current_file_path = ""

        # 여기서 ViewModel에 View를 연결!
        self.viewmodel.set_view(self.tree_view)

        # 이벤트 매니저에 콜백 등록
        self.event_manager.subscribe(MTTreeEvent.ITEM_ADDED, self.viewmodel.on_tree_mod_event)
        self.event_manager.subscribe(MTTreeEvent.ITEM_REMOVED, self.viewmodel.on_tree_mod_event)
        self.event_manager.subscribe(MTTreeEvent.ITEM_MOVED, self.viewmodel.on_tree_mod_event)

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
