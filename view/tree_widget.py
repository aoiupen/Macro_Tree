"""트리 위젯 모듈

트리 구조의 데이터를 표시하고 관리하는 위젯을 제공합니다.
"""
from typing import Dict, List, Optional, Any, Union
from PyQt5.QtWidgets import (
    QTreeWidget, QTreeWidgetItem, QAbstractItemView,
    QHeaderView, QMainWindow
)
from PyQt5.QtCore import Qt
from models.tree_repository import TreeRepository
from core.tree_state import TreeState
from view.tree_widget_item import TreeWidgetItem
from viewmodels.snapshot_manager import TreeSnapshotManager
from view.tree_widget_event_handler import TreeWidgetEventHandler
from viewmodels.tree_undo_redo import TreeUndoRedoManager
from viewmodels.tree_executor import TreeExecutor
from resources.resources import rsc
from viewmodels.tree_widget_item_logic import TreeItemData, TreeWidgetItemViewModel


class TreeWidget(QTreeWidget):
    """트리 위젯 클래스
    
    트리 구조의 데이터를 표시하고 관리합니다.
    """
    
    def __init__(self, parent: QMainWindow) -> None:
        """TreeWidget 생성자
        
        Args:
            parent: 부모 위젯
        """
        super().__init__(parent)
        
        # 트리 위젯 설정
        self.setColumnCount(5)
        self.setHeaderLabels(rsc["header"])
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.setDropIndicatorShown(True)
        self.setDragDropMode(QAbstractItemView.InternalMove)
        
        # 헤더 설정
        header = self.header()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        
        # 데이터 관리 객체 초기화
        self.tree_repository = TreeRepository()
        self.snapshot_manager = TreeSnapshotManager()
        self.undo_redo_manager = TreeUndoRedoManager(self)
        self.executor = TreeExecutor(self)
        
        # 이벤트 핸들러 설정
        self.event_handler = TreeWidgetEventHandler(self)
        
        # 액션 아이템 딕셔너리 초기화
        self.act_items = {
            "M": ["click", "double"],
            "K": ["typing", "copy", "paste"]
        }
        
        # 트리 로드
        self.load_tree()
    
    def load_tree(self) -> None:
        """DB에서 트리를 로드합니다."""
        try:
            # 트리 상태 로드
            tree_state = self.tree_repository.load_tree()
            
            # UI에 트리 상태 적용
            self.restore_state(tree_state)
            
        except Exception as e:
            print(f"트리 로드 오류: {e}")
    
    def save_tree(self) -> None:
        """현재 트리 상태를 DB에 저장합니다."""
        try:
            # 현재 트리 상태 가져오기
            tree_state = self.get_current_state()
            
            # DB에 저장
            self.tree_repository.save_tree(tree_state)
            
            print("트리가 성공적으로 저장되었습니다.")
            
        except Exception as e:
            print(f"트리 저장 오류: {e}")
    
    def get_current_state(self) -> TreeState:
        """현재 트리 위젯의 상태를 TreeState 객체로 반환합니다.
        
        Returns:
            현재 트리 상태
        """
        nodes = {}
        structure = {}
        
        # 루트 아이템 처리
        root_count = self.topLevelItemCount()
        for i in range(root_count):
            item = self.topLevelItem(i)
            self._process_item(item, None, nodes, structure)
        
        return TreeState(nodes, structure)
    
    def _process_item(self, item: TreeWidgetItem, parent_id: Optional[str], nodes: Dict[str, Dict[str, Any]], structure: Dict[str, List[str]]) -> None:
        """트리 아이템을 처리하여 노드와 구조 정보를 구성합니다.
        
        Args:
            item: 처리할 트리 위젯 아이템
            parent_id: 부모 노드 ID
            nodes: 노드 정보 딕셔너리
            structure: 구조 정보 딕셔너리
        """
        # 아이템 ID 생성
        item_id = str(id(item))
        
        # 노드 정보 저장
        nodes[item_id] = {
            'name': item.text(0),
            'inp': item.logic.inp,
            'sub_con': item.logic.sub_con,
            'sub': item.logic.sub,
            'parent_id': parent_id
        }
        
        # 구조 정보 저장
        if parent_id not in structure:
            structure[parent_id] = []
        structure[parent_id].append(item_id)
        
        # 자식 아이템 처리
        for i in range(item.childCount()):
            child = item.child(i)
            self._process_item(child, item_id, nodes, structure)
    
    def restore_state(self, tree_state: TreeState) -> None:
        """트리 상태를 복원합니다.
        
        Args:
            tree_state: 복원할 트리 상태
        """
        # 기존 아이템 모두 제거
        self.clear()
        
        # 아이템 ID와 TreeWidgetItem 객체 매핑
        item_map = {}
        
        # 루트 아이템 생성
        if None in tree_state.structure:
            for node_id in tree_state.structure[None]:
                node_data = tree_state.nodes[node_id]
                item = self._create_item_from_data(node_data)
                self.addTopLevelItem(item)
                item_map[node_id] = item
        
        # 자식 아이템 생성 (재귀적으로)
        self._restore_children(tree_state, None, item_map)
    
    def _restore_children(self, tree_state: TreeState, parent_id: Optional[str], item_map: Dict[str, TreeWidgetItem]) -> None:
        """자식 아이템들을 재귀적으로 복원합니다.
        
        Args:
            tree_state: 복원할 트리 상태
            parent_id: 부모 노드 ID
            item_map: 노드 ID와 TreeWidgetItem 객체 매핑
        """
        if parent_id not in tree_state.structure:
            return
        
        for node_id in tree_state.structure[parent_id]:
            if node_id not in item_map:
                continue
                
            parent_item = item_map[parent_id] if parent_id else None
            item = item_map[node_id]
            
            # 자식 아이템 추가
            if parent_item:
                parent_item.addChild(item)
            
            # 재귀적으로 자식의 자식 처리
            self._restore_children(tree_state, node_id, item_map)
    
    def _create_item_from_data(self, node_data: Dict[str, Any]) -> TreeWidgetItem:
        """노드 데이터로부터 TreeWidgetItem을 생성합니다.
        
        Args:
            node_data: 노드 데이터 딕셔너리
            
        Returns:
            생성된 TreeWidgetItem 객체
        """
        # 방법 1: 기존 방식 (리스트 사용)
        # row = [
        #     node_data['name'],
        #     node_data['inp'],
        #     node_data['sub_con'],
        #     node_data['sub']
        # ]
        # item = TreeWidgetItem(self, None, row)
        
        # 방법 2: 개선된 방식 (TreeItemData 직접 사용)
        
        # 딕셔너리에서 직접 TreeItemData 객체 생성
        tree_item_data = TreeItemData(
            name=node_data.get('name', ''),
            inp=node_data.get('inp', 'M'),
            sub=node_data.get('sub', 'M_click'),
            sub_con=node_data.get('sub_con', '')
        )
        
        # TreeItemData 객체를 사용하여 TreeWidgetItemViewModel 생성
        view_model = TreeWidgetItemViewModel(data=tree_item_data)
        
        # TreeWidgetItem 생성 (TreeWidgetItemViewModel 직접 전달)
        item = TreeWidgetItem(self, None, view_model=view_model)
        
        return item
    
    def add_group(self) -> None:
        """그룹 아이템을 추가합니다."""
        item = TreeWidgetItem(self, None, ["G:New Group", "", "", ""])
        self.addTopLevelItem(item)
        self.setCurrentItem(item)
        self.editItem(item, 0)
    
    def add_instance(self) -> None:
        """인스턴스 아이템을 추가합니다."""
        item = TreeWidgetItem(self, None, ["I:New Instance", "M", "", "click"])
        self.addTopLevelItem(item)
        self.setCurrentItem(item)
        self.editItem(item, 0)
    
    def add_action(self) -> None:
        """액션 아이템을 추가합니다."""
        item = TreeWidgetItem(self, None, ["New Action", "M", "", "click"])
        
        # 선택된 아이템이 있으면 자식으로 추가
        selected = self.selectedItems()
        if selected:
            parent = selected[0]
            parent.addChild(item)
            parent.setExpanded(True)
        else:
            self.addTopLevelItem(item)
            
        self.setCurrentItem(item)
        self.editItem(item, 0)
    
    def delete_selected_items(self) -> None:
        """선택된 아이템들을 삭제합니다."""
        selected = self.selectedItems()
        for item in selected:
            parent = item.parent()
            if parent:
                parent.removeChild(item)
            else:
                index = self.indexOfTopLevelItem(item)
                self.takeTopLevelItem(index)
    
    def execute_selected_items(self) -> None:
        """선택된 아이템들을 실행합니다."""
        self.executor.execute_selected_items() 