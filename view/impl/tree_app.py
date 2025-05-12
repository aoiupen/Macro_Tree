import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from PyQt6.QtCore import Qt, QTimer

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
        self.state_manager = MTTreeStateManager()
        self.event_manager = MTTreeEventManager()
        self.tree = MTTree(tree_id="root", name="Root Tree", event_manager=self.event_manager)
        
        # 샘플 데이터: 그룹 1개와 그 하위에 INSTRUCTION 1개만 추가
        group = MTTreeItem("group-1", {"name": "Group 1", "node_type": MTNodeType.GROUP})
        self.tree.add_item(group, None)
        instr = MTTreeItem("item-1", {"name": "Instruction 1", "node_type": MTNodeType.INSTRUCTION})
        self.tree.add_item(instr, "group-1")

        # ViewModel 생성
        self.viewmodel = MTTreeViewModel(self.tree, None, self.state_manager, self.event_manager)
        
        # 트리 뷰 생성 및 설정
        self.tree_view = TreeView(self.viewmodel)
        
        # 레이아웃 구성
        central_widget = QWidget()
        layout = QVBoxLayout(central_widget)
        layout.addWidget(self.tree_view)
        self.setCentralWidget(central_widget)
        
        self.resize(400, 300)
        
        # 여기서 ViewModel에 View를 연결!
        self.viewmodel.set_view(self.tree_view)

        # 이벤트 매니저에 콜백 등록
        self.event_manager.subscribe(MTTreeEvent.ITEM_ADDED, self.viewmodel.on_tree_mod_event)
        self.event_manager.subscribe(MTTreeEvent.ITEM_REMOVED, self.viewmodel.on_tree_mod_event)
        self.event_manager.subscribe(MTTreeEvent.ITEM_MOVED, self.viewmodel.on_tree_mod_event)

        # 트리 위젯 상태를 UI가 완전히 그려진 뒤 한 번만 출력

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
