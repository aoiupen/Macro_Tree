"""트리 위젯 모듈

트리 구조의 데이터를 표시하고 관리하는 위젯을 제공합니다.
"""
from typing import Dict, List, Optional, Any, Union
from PyQt5.QtWidgets import (
    QTreeWidget, QTreeWidgetItem, QAbstractItemView,
    QHeaderView, QMainWindow
)
from PyQt5.QtCore import Qt
from package.db.tree_db_dao import TreeDbDao
from package.db.tree_data import TreeState
from package.tree_widget_item import TreeWidgetItem
from package.db.tree_snapshot_manager import TreeSnapshotManager
from package.ui.tree_widget_event_handler import TreeWidgetEventHandler
from package.logic.tree_undo_redo_manager import TreeUndoRedoManager
from package.logic.tree_item_executor import TreeItemExecutor
from package.resources.resources import rsc


class TreeWidget(QTreeWidget):
    """트리 위젯 클래스
    
    트리 구조의 데이터를 표시하고 관리하는 위젯입니다.
    """

    def __init__(self, parent: QMainWindow) -> None:
        """TreeWidget 생성자
        
        Args:
            parent: 부모 윈도우
        """
        super().__init__()
        self.window = parent
        self.db_dao = TreeDbDao()
        self.snapshot_manager = TreeSnapshotManager()
        self.event_handler = TreeWidgetEventHandler(self)
        self.undo_redo_manager = TreeUndoRedoManager(self)
        self.item_executor = TreeItemExecutor(self)
        self.tree_state: Optional[TreeState] = None
        self.selected_node_items: List[TreeWidgetItem] = []

        # UI 설정
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.setEditTriggers(QAbstractItemView.DoubleClicked)
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.dropEvent = self.event_handler.tree_drop_event
        self.header().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.header().setCascadingSectionResizes(True)
        self.customContextMenuRequested.connect(self.event_handler.context_menu)
        self.itemClicked.connect(self.event_handler.on_item_clicked)

    def load_from_db(self) -> None:
        """DB에서 트리를 로드합니다."""
        self.tree_state = self.db_dao.load_tree()
        self.snapshot_manager.take_snapshot(self.tree_state)
        self.clear()
        self.build_tree_from_state()

    def save_to_db(self) -> None:
        """현재 트리 상태를 DB에 저장합니다."""
        self.update_tree_state()
        self.db_dao.save_tree(self.tree_state)

    def build_tree_from_state(self) -> None:
        """트리 상태를 기반으로 트리 UI를 구성합니다."""
        self.clear()
        if not self.tree_state:
            return

        for node_id, node_data in self.tree_state.nodes.items():
            if node_data.get('parent_id') is None and node_data.get('name') == 'top':
                for child_id in self.tree_state.structure.get(node_id, []):
                    child_data = self.tree_state.nodes[child_id]
                    self.create_top_level_item(child_id, child_data)
                break
            elif node_data.get('parent_id') is None and node_data.get('name') != 'top':
                self.create_top_level_item(node_id, node_data)
            elif node_data.get('parent_id') in self.tree_state.nodes:
                parent_id = node_data.get('parent_id')
                parent_item = self.find_item_by_node_id(parent_id)
                if parent_item:
                    self.create_tree_item(parent_item, node_id, node_data)

    def find_item_by_node_id(self, node_id: str) -> Optional[TreeWidgetItem]:
        """node_id로 TreeWidgetItem을 찾습니다.
        
        Args:
            node_id: 찾을 노드의 ID
            
        Returns:
            찾은 TreeWidgetItem 또는 None
        """
        items = self.findItems("", Qt.MatchContains | Qt.MatchRecursive, 0)
        for item in items:
            if hasattr(item, 'node_id') and item.node_id == node_id:
                return item
        return None
    
    def create_top_level_item(self, node_id: str, node_data: Dict[str, Any]) -> TreeWidgetItem:
        """최상위 TreeWidgetItem을 생성하고 자식 노드를 재귀적으로 생성합니다.
        
        Args:
            node_id: 노드 ID
            node_data: 노드 데이터
            
        Returns:
            생성된 TreeWidgetItem
        """
        row = [
            node_data.get('parent_id', 'top'),
            node_data['name'],
            node_data.get('inp', ''),
            node_data.get('sub_con', ''),
            node_data.get('sub', ''),
            ''
        ]
        item = TreeWidgetItem(self, None, row)
        item.node_id = node_id
        self.addTopLevelItem(item)

        for child_id in self.tree_state.structure.get(node_id, []):
            child_data = self.tree_state.nodes[child_id]
            self.create_tree_item(item, child_id, child_data)

        return item
    
    def create_tree_item(self, parent: Optional[TreeWidgetItem], node_id: str,
                        node_data: Dict[str, Any]) -> TreeWidgetItem:
        """TreeWidgetItem을 생성하고 자식 노드를 재귀적으로 생성합니다.
        
        Args:
            parent: 부모 TreeWidgetItem
            node_id: 노드 ID
            node_data: 노드 데이터
            
        Returns:
            생성된 TreeWidgetItem
        """
        row = [
            node_data.get('parent_id', 'top'),
            node_data['name'],
            node_data.get('inp', ''),
            node_data.get('sub_con', ''),
            node_data.get('sub', ''),
            ''
        ]
        item = TreeWidgetItem(self, parent, row)
        item.node_id = node_id

        if parent is None:
            self.addTopLevelItem(item)
        else:
            parent.addChild(item)

        for child_id in self.tree_state.structure.get(node_id, []):
            child_data = self.tree_state.nodes[child_id]
            self.create_tree_item(item, child_id, child_data)

        return item

    def update_tree_state(self) -> None:
        """현재 UI 상태를 tree_state에 반영합니다."""
        nodes: Dict[str, Dict[str, Any]] = {}
        structure: Dict[str, List[str]] = {}

        def process_item(item: TreeWidgetItem, parent_id: Optional[str] = None) -> None:
            """아이템을 처리하고 상태를 업데이트합니다.
            
            Args:
                item: 처리할 TreeWidgetItem
                parent_id: 부모 노드 ID
            """
            node_id = getattr(item, 'node_id', None)
            if node_id is None:
                return

            nodes[node_id] = {
                'name': item.logic.name,
                'inp': item.logic.inp,
                'sub_con': item.logic.sub_con,
                'sub': item.logic.sub,
                'parent_id': parent_id
            }

            if parent_id not in structure:
                structure[parent_id] = []
            structure[parent_id].append(node_id)

            for i in range(item.childCount()):
                process_item(item.child(i), node_id)

        for i in range(self.topLevelItemCount()):
            process_item(self.topLevelItem(i))

        self.tree_state = TreeState(nodes, structure)

    def restore_state(self, state: TreeState) -> None:
        """상태를 복원합니다 (undo/redo용).
        
        Args:
            state: 복원할 TreeState
        """
        self.tree_state = state
        self.clear()
        self.build_tree_from_state()

    def create_tree_item_with_id(self, parent: Optional[TreeWidgetItem],
                                row: List[str]) -> TreeWidgetItem:
        """새로운 TreeWidgetItem을 생성하고 node_id를 할당합니다.
        
        Args:
            parent: 부모 TreeWidgetItem
            row: 아이템 데이터 리스트
            
        Returns:
            생성된 TreeWidgetItem
        """
        item = TreeWidgetItem(self, parent, row)
        return item

    def keyPressEvent(self, event: QKeyEvent) -> None:
        """키 입력 이벤트를 처리합니다.
        
        Args:
            event: 키 이벤트 객체
        """
        self.event_handler.key_press_event(event)

    def mousePressEvent(self, event: QMouseEvent) -> None:
        """마우스 클릭 이벤트를 처리합니다.
        
        Args:
            event: 마우스 이벤트 객체
        """
        if event.modifiers() != Qt.ControlModifier:
            super().mousePressEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        """마우스 버튼 해제 이벤트를 처리합니다.
        
        Args:
            event: 마우스 이벤트 객체
        """
        if event.modifiers() == Qt.ControlModifier:
            super().mousePressEvent(event)
            items = self.currentItem()
            if items:
                self.setCurrentItem(items)
        super().mouseReleaseEvent(event)

    def contextMenuEvent(self, event: QContextMenuEvent) -> None:
        """컨텍스트 메뉴 이벤트를 처리합니다.
        
        Args:
            event: 컨텍스트 메뉴 이벤트 객체
        """
        self.event_handler.context_menu_event(event)
    
    def exec_inst(self) -> None:
        """선택된 아이템들을 실행합니다."""
        self.item_executor.execute_selected_items()