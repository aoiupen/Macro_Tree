"""트리 뷰모델 모듈

트리 구조의 데이터를 UI와 연결하는 뷰모델을 제공합니다.
"""
from typing import Dict, List, Optional, Any, Set, Tuple, Union
from PyQt6.QtCore import QObject, pyqtSignal, pyqtSlot
from core.tree_state import TreeState
from viewmodels.item_viewmodel import ItemViewModel


class TreeViewModel(QObject):
    """트리 뷰모델 클래스
    
    트리 구조의 데이터를 UI와 연결합니다.
    """
    
    stateChanged = pyqtSignal(TreeState)  # 상태 변경 시그널
    selectionChanged = pyqtSignal(list)  # 선택 변경 시그널
    
    def __init__(self):
        """TreeViewModel 생성자"""
        super().__init__()
        self._items: Dict[str, ItemViewModel] = {}
        self._structure: Dict[Optional[str], List[str]] = {}
        self._selected: Set[str] = set()
        self._expanded: Set[str] = set()
    
    def restore_state(self, tree_state: TreeState) -> None:
        """트리 상태를 복원합니다.
        
        Args:
            tree_state: 복원할 트리 상태
        """
        # 기존 데이터 초기화
        self._items.clear()
        self._structure = tree_state.structure.copy()
        
        # 노드 데이터로 ItemViewModel 생성
        for node_id, node_data in tree_state.nodes.items():
            item = ItemViewModel.from_node_data(node_data)
            self._items[node_id] = item
        
        # 상태 변경 시그널 발생
        self.stateChanged.emit(tree_state)
    
    @pyqtSlot(result=TreeState)
    def get_current_state(self) -> TreeState:
        """현재 트리 상태를 반환합니다.
        
        Returns:
            현재 트리 상태
        """
        nodes = {}
        
        # 각 아이템의 데이터를 노드로 변환
        for item_id, item in self._items.items():
            parent_id = None
            
            # 부모 찾기
            for parent, children in self._structure.items():
                if item_id in children:
                    parent_id = parent
                    break
            
            # 노드 데이터 구성
            nodes[item_id] = {
                'name': item.name,
                'inp': item.inp,
                'sub_con': item.sub_con,
                'sub': item.sub,
                'parent_id': parent_id
            }
        
        # 상태 객체 생성
        tree_state = TreeState(nodes, self._structure)
        
        return tree_state
    
    @pyqtSlot(str, str)
    def update_item(self, item_id: str, property_name: str, value: Any) -> None:
        """아이템 속성을 업데이트합니다.
        
        Args:
            item_id: 업데이트할 아이템 ID
            property_name: 업데이트할 속성 이름
            value: 새 값
        """
        if item_id in self._items:
            item = self._items[item_id]
            setattr(item, property_name, value)
            
            # 상태 변경 시그널 발생
            self.stateChanged.emit(self.get_current_state())
    
    @pyqtSlot(str, result=object)
    def get_item(self, item_id: str) -> Optional[ItemViewModel]:
        """ID로 아이템을 가져옵니다.
        
        Args:
            item_id: 가져올 아이템의 ID
            
        Returns:
            아이템 또는 None
        """
        return self._items.get(item_id)
    
    @pyqtSlot(object, result=bool)
    def add_item(self, item: ItemViewModel, parent_id: Optional[str] = None) -> bool:
        """아이템을 추가합니다.
        
        Args:
            item: 추가할 아이템
            parent_id: 부모 아이템 ID (선택적)
            
        Returns:
            성공 여부
        """
        try:
            # 새 아이템 ID 생성
            item_id = str(id(item))
            
            # 아이템 저장
            self._items[item_id] = item
            
            # 구조 업데이트
            if parent_id not in self._structure:
                self._structure[parent_id] = []
            self._structure[parent_id].append(item_id)
            
            # 빈 자식 목록 초기화
            if item_id not in self._structure:
                self._structure[item_id] = []
            
            # 상태 변경 시그널 발생
            self.stateChanged.emit(self.get_current_state())
            
            return True
        except Exception as e:
            print(f"아이템 추가 오류: {e}")
            return False
    
    @pyqtSlot(str, result=bool)
    def remove_item(self, item_id: str) -> bool:
        """아이템을 제거합니다.
        
        Args:
            item_id: 제거할 아이템 ID
            
        Returns:
            성공 여부
        """
        try:
            # 아이템 존재 확인
            if item_id not in self._items:
                return False
            
            # 자식 목록 가져오기
            children = self._structure.get(item_id, []).copy()
            
            # 재귀적으로 자식 제거
            for child_id in children:
                self.remove_item(child_id)
            
            # 구조에서 아이템 제거
            for parent_id, items in self._structure.items():
                if item_id in items:
                    items.remove(item_id)
            
            # 구조에서 자식 목록 제거
            if item_id in self._structure:
                del self._structure[item_id]
            
            # 아이템 제거
            del self._items[item_id]
            
            # 상태 변경 시그널 발생
            self.stateChanged.emit(self.get_current_state())
            
            return True
        except Exception as e:
            print(f"아이템 제거 오류: {e}")
            return False
    
    @pyqtSlot(str, str, result=bool)
    def move_item(self, item_id: str, new_parent_id: Optional[str]) -> bool:
        """아이템을 다른 부모로 이동합니다.
        
        Args:
            item_id: 이동할 아이템 ID
            new_parent_id: 새 부모 아이템 ID
            
        Returns:
            성공 여부
        """
        try:
            # 아이템 존재 확인
            if item_id not in self._items:
                return False
            
            # 자기 자신이 부모가 되지 않도록 방지
            if item_id == new_parent_id:
                return False
            
            # 기존 부모에서 제거
            old_parent_id = None
            for parent_id, children in self._structure.items():
                if item_id in children:
                    old_parent_id = parent_id
                    children.remove(item_id)
                    break
            
            # 새 부모에 추가
            if new_parent_id not in self._structure:
                self._structure[new_parent_id] = []
            self._structure[new_parent_id].append(item_id)
            
            # 상태 변경 시그널 발생
            self.stateChanged.emit(self.get_current_state())
            
            return True
        except Exception as e:
            print(f"아이템 이동 오류: {e}")
            return False
    
    @pyqtSlot(result=list)
    def get_selected_items(self) -> List[str]:
        """선택된 아이템 ID 목록을 반환합니다.
        
        Returns:
            선택된 아이템 ID 목록
        """
        return list(self._selected)
    
    @pyqtSlot(str)
    def select_item(self, item_id: str) -> None:
        """아이템을 선택합니다.
        
        Args:
            item_id: 선택할 아이템 ID
        """
        if item_id in self._items:
            # 기존 선택 초기화
            self._selected.clear()
            
            # 새 선택 설정
            
            self._selected.add(item_id)
            # 선택 변경 시그널 발생
            self.selectionChanged.emit(list(self._selected))
    
    @pyqtSlot(str)
    def toggle_select_item(self, item_id: str) -> None:
        """아이템 선택을 토글합니다.
        
        Args:
            item_id: 토글할 아이템 ID
        """
        if item_id in self._items:
            if item_id in self._selected:
                self._selected.remove(item_id)
            else:
                self._selected.add(item_id)
            
            # 선택 변경 시그널 발생
            self.selectionChanged.emit(list(self._selected))
    
    @pyqtSlot(str)
    def toggle_expand(self, item_id: str) -> None:
        """아이템 확장 상태를 토글합니다.
        
        Args:
            item_id: 토글할 아이템 ID
        """
        if item_id in self._items:
            if item_id in self._expanded:
                self._expanded.remove(item_id)
            else:
                self._expanded.add(item_id)
    
    @pyqtSlot(str, result=bool)
    def is_expanded(self, item_id: str) -> bool:
        """아이템이 확장되었는지 확인합니다.
        
        Args:
            item_id: 확인할 아이템 ID
            
        Returns:
            확장 여부
        """
        return item_id in self._expanded
    
    @pyqtSlot(result=bool)
    def addGroup(self) -> bool:
        """그룹 아이템을 추가합니다."""
        new_group = ItemViewModel.create_group("새 그룹")
        return self.add_item(new_group)
    
    @pyqtSlot(result=bool)
    def addInstance(self) -> bool:
        """인스턴스 아이템을 추가합니다."""
        new_instance = ItemViewModel.create_instance("새 인스턴스")
        return self.add_item(new_instance)