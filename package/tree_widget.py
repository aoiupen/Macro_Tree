from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from package.tree_db import TreeDB, TreeState
from package.tree_widget_item import TreeWidgetItem
from package.tree_db_dao import TreeDbDao
from package.tree_snapshot_manager import TreeSnapshotManager
from package.tree_widget_event_handler import TreeWidgetEventHandler
from package.tree_undo_redo_manager import TreeUndoRedoManager
from package.tree_item_executor import TreeItemExecutor
from resources import rsc  # rsc 임포트

class TreeWidget(QTreeWidget):
    def __init__(self, parent):
        super().__init__()
        self.win = parent
        self.db_dao = TreeDbDao("dbname=mydb user=myuser password=mypass")
        self.snapshot_manager = TreeSnapshotManager()
        self.event_handler = TreeWidgetEventHandler(self)
        self.undo_redo_manager = TreeUndoRedoManager(self)
        self.item_executor = TreeItemExecutor(self)
        self.tree_state = None

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

        # 초기 데이터 로드
        self.load_from_db()

    def load_from_db(self):
        """DB에서 트리 로드"""
        self.tree_state = self.db_dao.load_tree()
        self.snapshot_manager.take_snapshot(self.tree_state)
        self.clear()
        self.build_tree_from_state()

    def save_to_db(self):
        """현재 트리 상태를 DB에 저장"""
        self.update_tree_state()
        self.db_dao.save_tree(self.tree_state)

    def build_tree_from_state(self):
        """tree_state를 사용하여 트리 UI 구성"""
        for node_id in self.tree_state.structure.get(None, []):
            node_data = self.tree_state.nodes[node_id]
            self.create_tree_item(None, node_id, node_data)

    def create_tree_item(self, parent, node_id, node_data):
        """TreeWidgetItem 생성 및 자식 노드 재귀적 생성"""
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

        for child_id in self.tree_state.structure.get(node_id, []):
            child_data = self.tree_state.nodes[child_id]
            self.create_tree_item(item, child_id, child_data)

        return item

    def update_tree_state(self):
        """현재 UI 상태를 tree_state에 반영"""
        nodes = {}
        structure = {}

        def process_item(item, parent_id=None):
            node_id = getattr(item, 'node_id', None)
            if node_id is None:
                return

            nodes[node_id] = {
                'name': item.name,
                'inp': item.inp,
                'sub_con': item.sub_con,
                'sub': item.sub,
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

    def restore_state(self, state):
        """상태 복원 (undo/redo용)"""
        self.tree_state = state
        self.clear()
        self.build_tree_from_state()

    def create_tree_item_with_id(self, parent, row):
        """새로운 TreeWidgetItem을 생성하고 node_id 할당"""
        item = TreeWidgetItem(self, parent, row)
        # item.node_id = self.db.get_next_node_id()  # DB에서 새로운 ID 발급
        return item
    
    def keyPressEvent(self, event):
        self.event_handler.key_press_event(event)
    
    def mousePressEvent(self, event):
        self.event_handler.mouse_press_event(event)
    
    def mouseReleaseEvent(self, event):
        self.event_handler.mouse_release_event(event)

    def contextMenuEvent(self, event):
        self.event_handler.context_menu_event(event)

    def exec_inst(self):
        self.item_executor.execute_selected_items()