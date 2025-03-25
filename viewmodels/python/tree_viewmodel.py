"""트리 뷰모델 모듈

트리 구조의 데이터를 UI와 연결하는 뷰모델을 제공합니다.
"""
from typing import Dict, List, Optional, Any, Set, Tuple, Union
from PyQt6.QtCore import QObject, pyqtSignal, pyqtSlot, QModelIndex, Qt, QAbstractListModel
from core.tree_state import TreeState
from viewmodels.item_viewmodel import ItemViewModel
from viewmodels.interfaces.tree_interface import ITreeViewModel


class TreeViewModel(QAbstractListModel, ITreeViewModel):
    """트리 뷰모델 클래스
    
    트리 구조의 데이터를 UI와 연결합니다.
    QAbstractListModel을 상속하여 QML에서 더 쉽게 사용할 수 있게 합니다.
    """
    
    # 커스텀 롤 정의
    NameRole = Qt.ItemDataRole.UserRole + 1
    IdRole = Qt.ItemDataRole.UserRole + 2
    DepthRole = Qt.ItemDataRole.UserRole + 3
    HasChildrenRole = Qt.ItemDataRole.UserRole + 4
    IsExpandedRole = Qt.ItemDataRole.UserRole + 5
    IsSelectedRole = Qt.ItemDataRole.UserRole + 6
    InputTypeRole = Qt.ItemDataRole.UserRole + 7
    SubActionRole = Qt.ItemDataRole.UserRole + 8
    SubContentRole = Qt.ItemDataRole.UserRole + 9
    IndexRole = Qt.ItemDataRole.UserRole + 10
    
    stateChanged = pyqtSignal(TreeState)  # 상태 변경 시그널
    selectionChanged = pyqtSignal(list)  # 선택 변경 시그널
    
    def __init__(self, parent=None):
        """TreeViewModel 생성자"""
        super().__init__(parent)
        self._items: Dict[str, ItemViewModel] = {}
        self._structure: Dict[Optional[str], List[str]] = {}
        self._selected: Set[str] = set()
        self._expanded: Set[str] = set()
        self._flat_items: List[str] = []  # 평면화된 아이템 ID 목록
        
        # 역할 이름 매핑 등록
        self._roles = {
            self.NameRole: b'name',
            self.IdRole: b'id',
            self.DepthRole: b'depth',
            self.HasChildrenRole: b'hasChildren',
            self.IsExpandedRole: b'isExpanded',
            self.IsSelectedRole: b'isSelected',
            self.InputTypeRole: b'inputType',
            self.SubActionRole: b'subAction',
            self.SubContentRole: b'subContent',
            self.IndexRole: b'index'
        }
    
    def roleNames(self):
        """QML에서 사용할 역할 이름을 반환합니다."""
        return self._roles
    
    def rowCount(self, parent=QModelIndex()):
        """모델의 행 수를 반환합니다."""
        return len(self._flat_items)
    
    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        """지정된 인덱스와 역할에 해당하는 데이터를 반환합니다."""
        if not index.isValid() or index.row() >= len(self._flat_items):
            return None
        
        # 인덱스에 해당하는 아이템 ID 가져오기
        item_id = self._flat_items[index.row()]
        item = self._items.get(item_id)
        
        if not item:
            return None
        
        # 해당 역할에 맞는 데이터 반환
        if role == self.NameRole:
            return item.name
        elif role == self.IdRole:
            return item.id
        elif role == self.DepthRole:
            return self._get_item_depth(item_id)
        elif role == self.HasChildrenRole:
            return len(self._structure.get(item_id, [])) > 0
        elif role == self.IsExpandedRole:
            return item_id in self._expanded
        elif role == self.IsSelectedRole:
            return item_id in self._selected
        elif role == self.InputTypeRole:
            return item.inp
        elif role == self.SubActionRole:
            return item.sub
        elif role == self.SubContentRole:
            return item.sub_con
        elif role == self.IndexRole:
            return index.row()
        
        return None
    
    def _get_item_depth(self, item_id: str) -> int:
        """아이템의 깊이를 반환합니다."""
        depth = 0
        current_id = item_id
        
        # 부모를 찾아 깊이 계산
        while True:
            parent_id = None
            for parent, children in self._structure.items():
                if current_id in children:
                    parent_id = parent
                    break
            
            if parent_id is None or parent_id == "None":
                break
            
            depth += 1
            current_id = parent_id
        
        return depth
    
    def _rebuild_flat_items(self):
        """평면화된 아이템 목록을 다시 구성합니다."""
        self.beginResetModel()
        
        # 평면화된 아이템 목록 초기화
        self._flat_items = []
        
        # 루트 아이템부터 시작하여 트리 순회
        self._build_flat_list(None, 0)
        
        self.endResetModel()
    
    def _build_flat_list(self, parent_id, depth):
        """깊이 우선 탐색으로 평면화된 아이템 목록을 구성합니다."""
        children = self._structure.get(parent_id, [])
        
        for child_id in children:
            self._flat_items.append(child_id)
            
            # 확장된 경우에만 자식 추가
            if child_id in self._expanded:
                self._build_flat_list(child_id, depth + 1)
    
    def restore_state(self, tree_state: TreeState) -> None:
        """트리 상태를 복원합니다.
        
        Args:
            tree_state: 복원할 트리 상태
        """
        # 모델 리셋 시작
        self.beginResetModel()
        
        # 기존 데이터 초기화
        self._items.clear()
        self._selected.clear()
        self._expanded.clear()
        self._structure = tree_state.structure.copy()
        
        # 노드 데이터로 ItemViewModel 생성
        for node_id, node_data in tree_state.nodes.items():
            item = ItemViewModel.from_node_data(node_data)
            self._items[node_id] = item
            
            # 기본적으로 루트 노드는 확장
            if tree_state.structure.get(None, []) and node_id in tree_state.structure.get(None, []):
                self._expanded.add(node_id)
        
        # 평면화된 아이템 목록 다시 구성
        self._rebuild_flat_items()
        
        # 모델 리셋 완료
        self.endResetModel()
        
        # 상태 변경 시그널 발생
        self.stateChanged.emit(tree_state)
        
        # 디버그 정보
        print(f"TreeViewModel: 상태 복원 완료 - 노드 {len(self._items)}개, 표시 항목 {len(self._flat_items)}개")
    
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
            
            # 인덱스 찾기
            if item_id in self._flat_items:
                idx = self._flat_items.index(item_id)
                model_idx = self.index(idx, 0)
                
                # 적절한 역할 결정
                role = None
                if property_name == 'name':
                    role = self.NameRole
                elif property_name == 'inp':
                    role = self.InputTypeRole
                elif property_name == 'sub':
                    role = self.SubActionRole
                elif property_name == 'sub_con':
                    role = self.SubContentRole
                
                # 데이터 변경 알림
                if role:
                    self.dataChanged.emit(model_idx, model_idx, [role])
            
            # 상태 변경 시그널 발생
            self.stateChanged.emit(self.get_current_state())
    
    @pyqtSlot(str, result='QVariant')
    def get_item(self, item_id: str) -> Optional[ItemViewModel]:
        """아이템을 ID로 조회합니다.
        
        Args:
            item_id: 조회할 아이템 ID
            
        Returns:
            조회된 아이템 또는 None
        """
        return self._items.get(item_id)
    
    @pyqtSlot(result=int)
    def count(self) -> int:
        """아이템 수를 반환합니다."""
        return len(self._flat_items)
    
    @pyqtSlot(int, result='QVariant')
    def get(self, index: int) -> dict:
        """인덱스로 아이템을 조회합니다.
        
        Args:
            index: 조회할 인덱스
            
        Returns:
            아이템 데이터 딕셔너리
        """
        if 0 <= index < len(self._flat_items):
            item_id = self._flat_items[index]
            item = self._items.get(item_id)
            if item:
                return {
                    'id': item.id,
                    'name': item.name,
                    'inp': item.inp,
                    'sub': item.sub,
                    'sub_con': item.sub_con,
                    'depth': self._get_item_depth(item_id),
                    'hasChildren': len(self._structure.get(item_id, [])) > 0,
                    'isExpanded': item_id in self._expanded,
                    'isSelected': item_id in self._selected
                }
        return {}
    
    @pyqtSlot('QVariant', 'QVariant', result=bool)
    def add_item(self, item, parent_id: Optional[str] = None) -> bool:
        """아이템을 추가합니다.
        
        Args:
            item: 추가할 아이템
            parent_id: 부모 아이템 ID (선택적)
            
        Returns:
            추가 성공 여부
        """
        try:
            # 아이템 데이터 변환
            if isinstance(item, dict):
                item_data = item
            else:
                item_data = item.toDict()
            
            # 새 아이템 생성
            new_item = ItemViewModel.from_node_data(item_data)
            
            # 아이템 저장
            self._items[new_item.id] = new_item
            
            # 구조에 추가
            if parent_id not in self._structure:
                self._structure[parent_id] = []
            self._structure[parent_id].append(new_item.id)
            
            # 평면화된 목록 업데이트
            self._rebuild_flat_items()
            
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
            제거 성공 여부
        """
        try:
            # 아이템이 존재하는지 확인
            if item_id not in self._items:
                return False
            
            # 자식 아이템 재귀적으로 제거
            def remove_children(parent_id: str):
                children = self._structure.get(parent_id, [])
                for child_id in children:
                    remove_children(child_id)
                    if child_id in self._items:
                        del self._items[child_id]
                    if child_id in self._selected:
                        self._selected.remove(child_id)
                    if child_id in self._expanded:
                        self._expanded.remove(child_id)
            
            # 아이템과 자식 제거
            remove_children(item_id)
            
            # 부모의 자식 목록에서 제거
            for parent_id, children in self._structure.items():
                if item_id in children:
                    children.remove(item_id)
                    break
            
            # 구조에서 제거
            if item_id in self._structure:
                del self._structure[item_id]
            
            # 평면화된 목록 업데이트
            self._rebuild_flat_items()
            
            # 상태 변경 시그널 발생
            self.stateChanged.emit(self.get_current_state())
            
            return True
            
        except Exception as e:
            print(f"아이템 제거 오류: {e}")
            return False
    
    @pyqtSlot(str, str, result=bool)
    def move_item(self, item_id: str, new_parent_id: Optional[str]) -> bool:
        """아이템을 이동합니다.
        
        Args:
            item_id: 이동할 아이템 ID
            new_parent_id: 새로운 부모 아이템 ID
            
        Returns:
            이동 성공 여부
        """
        try:
            # 아이템이 존재하는지 확인
            if item_id not in self._items:
                return False
            
            # 현재 부모 찾기
            current_parent = None
            for parent_id, children in self._structure.items():
                if item_id in children:
                    current_parent = parent_id
                    break
            
            if current_parent is None:
                return False
            
            # 현재 부모의 자식 목록에서 제거
            self._structure[current_parent].remove(item_id)
            
            # 새 부모의 자식 목록에 추가
            if new_parent_id not in self._structure:
                self._structure[new_parent_id] = []
            self._structure[new_parent_id].append(item_id)
            
            # 아이템의 부모 ID 업데이트
            self._items[item_id]._data.parent_id = new_parent_id
            
            # 평면화된 목록 업데이트
            self._rebuild_flat_items()
            
            # 상태 변경 시그널 발생
            self.stateChanged.emit(self.get_current_state())
            
            return True
            
        except Exception as e:
            print(f"아이템 이동 오류: {e}")
            return False
    
    @pyqtSlot(result=list)
    def get_selected_items(self) -> List[str]:
        """선택된 아이템 ID 목록을 반환합니다."""
        return list(self._selected)
    
    @pyqtSlot(str)
    def select_item(self, item_id: str) -> None:
        """아이템을 선택합니다.
        
        Args:
            item_id: 선택할 아이템 ID
        """
        if item_id in self._items:
            self._selected.add(item_id)
            
            # 인덱스 찾기
            if item_id in self._flat_items:
                idx = self._flat_items.index(item_id)
                model_idx = self.index(idx, 0)
                
                # 데이터 변경 알림
                self.dataChanged.emit(model_idx, model_idx, [self.IsSelectedRole])
            
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
            
            # 인덱스 찾기
            if item_id in self._flat_items:
                idx = self._flat_items.index(item_id)
                model_idx = self.index(idx, 0)
                
                # 데이터 변경 알림
                self.dataChanged.emit(model_idx, model_idx, [self.IsSelectedRole])
            
            # 선택 변경 시그널 발생
            self.selectionChanged.emit(list(self._selected))
    
    @pyqtSlot(str)
    def toggle_expand(self, item_id: str) -> None:
        """아이템 확장을 토글합니다.
        
        Args:
            item_id: 토글할 아이템 ID
        """
        if item_id in self._items:
            if item_id in self._expanded:
                self._expanded.remove(item_id)
            else:
                self._expanded.add(item_id)
            
            # 인덱스 찾기
            if item_id in self._flat_items:
                idx = self._flat_items.index(item_id)
                model_idx = self.index(idx, 0)
                
                # 데이터 변경 알림
                self.dataChanged.emit(model_idx, model_idx, [self.IsExpandedRole])
            
            # 평면화된 목록 업데이트
            self._rebuild_flat_items()
    
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
        """새 그룹을 추가합니다.
        
        Returns:
            추가 성공 여부
        """
        return self.add_item(ItemViewModel.create_group("새 그룹"))
    
    @pyqtSlot(result=bool)
    def addInstance(self) -> bool:
        """새 인스턴스를 추가합니다.
        
        Returns:
            추가 성공 여부
        """
        return self.add_item(ItemViewModel.create_instance("새 인스턴스"))