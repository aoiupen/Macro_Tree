from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from package.db.tree_db_dao import TreeDbDao
from package.db.tree_db import TreeDB, TreeState
from package.tree_widget_item import TreeWidgetItem
from package.db.tree_snapshot_manager import TreeSnapshotManager
from package.ui.tree_widget_event_handler import TreeWidgetEventHandler
from package.logic.tree_undo_redo_manager import TreeUndoRedoManager
from package.logic.tree_item_executor import TreeItemExecutor
from package.resources.resources import rsc  # rsc 임포트

class TreeWidget(QTreeWidget):
    def __init__(self, parent):
        super().__init__()
        self.win = parent
        self.db_dao = TreeDbDao()
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
        """트리 상태를 기반으로 트리 UI 구성"""
        self.clear()
        for node_id, node_data in self.tree_state.nodes.items():
            if node_data.get('parent_id') is None and node_data.get('name') == 'top':
                for child_id in self.tree_state.structure.get(node_id, []):
                    child_data = self.tree_state.nodes[child_id]
                    self.create_top_level_item(child_id, child_data) # top 노드의 자식 노드를 최상위 노드로 추가
                break # top 노드는 하나만 존재하므로 루프 종료
            elif node_data.get('parent_id') is None and node_data.get('name') != 'top':
                self.create_top_level_item(node_id, node_data)
            elif node_data.get('parent_id') in self.tree_state.nodes:
                parent_id = node_data.get('parent_id')
                parent_item = self.find_item_by_node_id(parent_id)
                if parent_item:
                    self.create_tree_item(parent_item, node_id, node_data)

    def find_item_by_node_id(self, node_id):
        """node_id로 TreeWidgetItem 찾기"""
        items = self.findItems("", Qt.MatchContains | Qt.MatchRecursive, 0)
        for item in items:
            if hasattr(item, 'node_id') and item.node_id == node_id:
                return item
        return None
    
    def create_top_level_item(self, node_id, node_data):
        """최상위 TreeWidgetItem 생성 및 자식 노드 재귀적 생성"""
        row = [
            node_data.get('parent_id', 'top'),
            node_data['name'],
            node_data.get('inp', ''),
            node_data.get('sub_con', ''),
            node_data.get('sub', ''),
            ''
        ]
        item = TreeWidgetItem(self, None, row)  # 부모 아이템 없음
        item.node_id = node_id
        self.addTopLevelItem(item)  # QTreeWidget에 직접 추가

        for child_id in self.tree_state.structure.get(node_id, []):
            child_data = self.tree_state.nodes[child_id]
            self.create_tree_item(item, child_id, child_data)

        return item
    
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

        # QTreeWidget에 아이템 추가
        if parent is None:
            self.addTopLevelItem(item)
        else:
            parent.addChild(item)

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
        super().mousePressEvent(event) # 기본 동작을 수행
    
    def mouseReleaseEvent(self, event):
        super().mouseReleaseEvent(event) # 기본 동작을 수행

    def contextMenuEvent(self, event):
        super().contextMenuEvent(event) # 기본 동작을 수행

    def exec_inst(self):
        self.item_executor.execute_selected_items()