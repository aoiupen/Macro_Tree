"""트리 위젯 모듈

트리 구조의 데이터를 표시하고 관리하는 위젯을 제공합니다.
"""
from typing import Dict, List, Optional, Any, Union, cast
from PyQt5.QtWidgets import (
    QTreeWidget, QTreeWidgetItem, QAbstractItemView,
    QHeaderView, QMainWindow
)
from PyQt5.QtCore import Qt, pyqtSignal
from models.tree_repository import TreeRepository
from core.tree_state_interface import ITreeStateManager
from core.tree_state_manager import TreeStateManager
from core.tree_state import TreeState
from view.item import Item
from view.tree_event_handler import TreeWidgetEventHandler
from viewmodels.tree_executor import TreeExecutor
from resources.resources import rsc
from viewmodels.item_viewmodel import ItemData, ItemViewModel


class TreeWidget(QTreeWidget):
    """트리 위젯 클래스
    
    트리 구조의 데이터를 표시하고 관리합니다.
    """
    
    stateChanged = pyqtSignal(TreeState)  # 상태 변경 시그널
    
    def __init__(self, parent=None, 
                 state_manager: Optional[ITreeStateManager] = None):
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
        self.executor = TreeExecutor(self)

        # 선택적 의존성 주입
        self._state_manager = state_manager or TreeStateManager()

        # 이벤트 핸들러 설정
        self.event_handler = TreeWidgetEventHandler(self)
        
        # 액션 아이템 딕셔너리 초기화
        self.act_items = {
            "M": ["click", "double"],
            "K": ["typing", "copy", "paste"]
        }
        
        # 아이템 변경 시그널 연결
        self.itemChanged.connect(self._on_item_changed)
        
        # 트리 로드
        self.load_tree()
    
    def _on_item_changed(self, item: QTreeWidgetItem, column: int) -> None:
        """아이템이 변경되었을 때 호출됩니다.
        
        Args:
            item: 변경된 아이템
            column: 변경된 열 인덱스
        """
        # 현재 상태를 저장하고 시그널 발생
        self.stateChanged.emit(self.get_current_state())
    
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
            if isinstance(item, Item):
                self._process_item(cast(Item, item), None, nodes, structure)
        
        return TreeState(nodes, structure)
    
    def _process_item(self, item: Item, parent_id: Optional[str], nodes: Dict[str, Dict[str, Any]], structure: Dict[str, List[str]]) -> None:
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
            if isinstance(child, Item):
                self._process_item(cast(Item, child), item_id, nodes, structure)
    
    def restore_state(self, tree_state: TreeState) -> None:
        """트리 상태를 UI에 적용합니다.
        
        Args:
            tree_state: UI에 적용할 트리 상태
        """
        # 기존 아이템 모두 제거
        self.clear()
        
        # 아이템 ID와 Item 객체 매핑
        item_map: Dict[str, Item] = {}
        
        # 루트 아이템 생성
        if None in tree_state.structure:
            for node_id in tree_state.structure[None]:
                node_data = tree_state.nodes[node_id]
                item = self._create_item_from_data(node_data)
                self.addTopLevelItem(item)
                item_map[node_id] = item
        
        # 자식 아이템 생성 (재귀적으로)
        self._apply_items_to_ui(tree_state, None, item_map)
    
    def _apply_items_to_ui(self, tree_state: TreeState, parent_id: Optional[str], item_map: Dict[str, Item]) -> None:
        """자식 아이템들을 UI에 재귀적으로 적용합니다.
        
        Args:
            tree_state: 적용할 트리 상태
            parent_id: 부모 노드 ID
            item_map: 노드 ID와 Item 객체 매핑
        """
        if parent_id not in tree_state.structure:
            return
        
        for node_id in tree_state.structure[parent_id]:
            if node_id not in item_map:
                continue
                
            parent_item = item_map.get(parent_id)
            item = item_map[node_id]
            
            # 자식 아이템 추가
            if parent_item:
                parent_item.addChild(item)
            
            # 재귀적으로 자식의 자식 처리
            self._apply_items_to_ui(tree_state, node_id, item_map)
    
    def _create_item_from_data(self, node_data: Dict[str, Any]) -> Item:
        """노드 데이터로부터 Item을 생성합니다.
        
        Args:
            node_data: 노드 데이터 딕셔너리
            
        Returns:
            생성된 Item 객체
        """
        # 딕셔너리에서 직접 ItemData 객체 생성
        item_data = ItemData(
            name=node_data.get('name', ''),
            inp=node_data.get('inp', 'M'),
            sub=node_data.get('sub', 'M_click'),
            sub_con=node_data.get('sub_con', '')
        )
        
        # ItemData 객체를 사용하여 ItemViewModel 생성
        view_model = ItemViewModel(data=item_data)
        
        # Item 생성 (ItemViewModel 직접 전달)
        item = Item(self, None, view_model=view_model)
        
        return item
    
    def add_group(self) -> None:
        """그룹 아이템을 추가합니다."""
        item = Item(self, None, ["G:New Group", "", "", ""])
        self.addTopLevelItem(item)
        self.setCurrentItem(item)
        self.editItem(item, 0)
        self.stateChanged.emit(self.get_current_state())
    
    def add_instance(self) -> None:
        """인스턴스 아이템을 추가합니다."""
        item = Item(self, None, ["I:New Instance", "M", "", "click"])
        self.addTopLevelItem(item)
        self.setCurrentItem(item)
        self.editItem(item, 0)
        self.stateChanged.emit(self.get_current_state())
    
    def add_action(self) -> None:
        """액션 아이템을 추가합니다."""
        item = Item(self, None, ["New Action", "M", "", "click"])
        
        # 선택된 아이템이 있으면 자식으로 추가
        selected = self.selectedItems()
        if selected and isinstance(selected[0], Item):
            parent = cast(Item, selected[0])
            parent.addChild(item)
            parent.setExpanded(True)
        else:
            self.addTopLevelItem(item)
        
        self.setCurrentItem(item)
        self.editItem(item, 0)
        self.stateChanged.emit(self.get_current_state())
    
    def execute_selected_items(self) -> None:
        """선택된 아이템들을 실행합니다."""
        selected = self.selectedItems()
        if not selected:
            return
        
        for item in selected:
            if isinstance(item, Item):
                self.executor.execute_item(cast(Item, item)) 