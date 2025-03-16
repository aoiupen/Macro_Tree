"""아이템 위젯 모듈

트리의 개별 아이템을 관리하는 클래스를 제공합니다.
"""
from typing import Optional, List, Dict, Any
from PyQt5.QtWidgets import QTreeWidgetItem
from viewmodels.item_viewmodel import ItemViewModel
from core.tree_state import TreeState


class Item(QTreeWidgetItem):
    """아이템 클래스
    
    트리의 개별 아이템을 관리합니다.
    """
    
    def __init__(
        self, 
        tree_widget, 
        parent: Optional['Item'], 
        row: List[str] = None, 
        view_model: Optional[ItemViewModel] = None
    ) -> None:
        """Item 생성자
        
        Args:
            tree_widget: 부모 트리 위젯
            parent: 부모 아이템
            row: 아이템 데이터 리스트 (view_model이 None인 경우에만 사용)
            view_model: ItemViewModel 인스턴스 (우선적으로 사용)
        """
        super().__init__(parent)
        
        if view_model is not None:
            self.logic = view_model
        else:
            self.logic = ItemViewModel(row or [])
        
        self.update_ui()
    
    def update_ui(self) -> None:
        """UI 상태를 업데이트합니다."""
        self.setText(0, self.logic.name)
        self.setText(1, self.logic.inp)
        self.setText(2, self.logic.sub_con)
        self.setText(3, self.logic.sub)
    
    def get_data(self) -> Dict[str, Any]:
        """아이템 데이터를 딕셔너리로 반환합니다."""
        return {
            'name': self.logic.name,
            'inp': self.logic.inp,
            'sub_con': self.logic.sub_con,
            'sub': self.logic.sub,
        }
    
    def serialize_to_json(self) -> str:
        """아이템 상태를 JSON 문자열로 직렬화합니다."""
        item_id = str(id(self))
        nodes = {item_id: self.get_data()}
        structure = {}
        
        tree_state = TreeState(nodes, structure)
        return tree_state.serialize_to_json()
    
    @classmethod
    def deserialize_from_json(cls, json_str: str, tree_widget, parent: Optional['Item'] = None) -> 'Item':
        """JSON 문자열에서 아이템 상태를 복원합니다."""
        tree_state = TreeState.deserialize_from_json(json_str)
        
        if not tree_state.nodes:
            return None
            
        # 첫 번째 노드 데이터 사용
        node_id = next(iter(tree_state.nodes))
        node_data = tree_state.nodes[node_id]
        
        # ItemViewModel 생성
        item_data = ItemViewModel(data=node_data)
        
        # Item 생성 및 반환
        return cls(tree_widget, parent, view_model=item_data)

    def save_state_to_file(self, filename: str) -> None:
        """아이템 상태를 파일에 저장합니다."""
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(self.serialize_to_json())
    
    @classmethod
    def load_state_from_file(cls, filename: str, tree_widget, parent: Optional['Item'] = None) -> 'Item':
        """파일에서 아이템 상태를 로드합니다."""
        with open(filename, 'r', encoding='utf-8') as f:
            return cls.deserialize_from_json(f.read(), tree_widget, parent)
    
    def export_state_to_json(self) -> str:
        """아이템 데이터를 JSON 형식으로 내보냅니다."""
        return self.serialize_to_json()
    
    @classmethod
    def import_state_from_json(cls, data_str: str, tree_widget, parent: Optional['Item'] = None) -> 'Item':
        """JSON 문자열에서 아이템 데이터를 가져옵니다."""
        return cls.deserialize_from_json(data_str, tree_widget, parent) 