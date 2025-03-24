"""아이템 뷰모델 모듈

트리 아이템의 데이터와 상태를 관리하는 클래스를 제공합니다.
"""
from typing import List, Union, TypeVar, Generic, Optional, Any, Dict
from dataclasses import dataclass
from PyQt6.QtCore import QObject, pyqtProperty, pyqtSignal, pyqtSlot

# 순환 리스트 클래스 정의
T = TypeVar('T')

class CyclicList(Generic[T]):
    """순환 리스트 클래스
    
    리스트의 요소를 순환적으로 접근할 수 있는 기능을 제공합니다.
    이 클래스는 여러 값을 순차적으로 순환해야 하는 경우 코드를 간결하게 유지하는 데 도움이 됩니다.
    
    빌더 패턴이나 복잡한 상태 관리 대신, 단일 책임 원칙에 따라 순환 기능만 담당하는 
    가벼운 유틸리티 클래스로 설계되었습니다.
    """
    
    def __init__(self, items: List[T]):
        """CyclicList 생성자
        
        Args:
            items: 순환할 아이템 목록
        """
        self.items = items
    
    def next(self, current: T) -> T:
        """현재 아이템의 다음 아이템을 반환합니다.
        
        Args:
            current: 현재 아이템
            
        Returns:
            다음 아이템. 현재 아이템이 목록에 없으면 첫 번째 아이템 반환
        """
        try:
            idx = self.items.index(current)
            return self.items[(idx + 1) % len(self.items)]
        except ValueError:
            return self.items[0] if self.items else current


@dataclass
class ItemData:
    """아이템 데이터 클래스"""
    id: str = ""
    name: str = ""
    inp: str = ""
    sub_con: str = ""
    sub: str = ""
    expanded: bool = False
    parent_id: Optional[str] = None
    children_ids: List[str] = None
    
    def __post_init__(self):
        if self.children_ids is None:
            self.children_ids = []


class ItemViewModel(QObject):
    """아이템 뷰모델 클래스
    
    트리 아이템의 데이터와 상태를 관리합니다.
    """
    
    # 상수 정의
    _M_ACTIONS = ["mouse", "key"]
    _KEY_ACTIONS = ["down", "up", "press"]
    _SUB_ACTIONS = {
        "mouse": ["click", "double", "move", "drag", "right"],
        "key": ["down", "up", "press"]
    }
    
    # 시그널 정의
    nameChanged = pyqtSignal()
    inpChanged = pyqtSignal()
    subConChanged = pyqtSignal()
    subChanged = pyqtSignal()
    expandedChanged = pyqtSignal()
    childrenChanged = pyqtSignal()
    
    def __init__(self, parent: Optional[QObject] = None, data: Optional[ItemData] = None):
        """ItemViewModel 생성자
        
        Args:
            parent: 부모 객체 (선택적)
            data: 아이템 데이터 (선택적)
        """
        super().__init__(parent)
        self._data = data or ItemData()
        self._input_cycler = CyclicList(["M", "K"])
    
    @classmethod
    def from_node_data(cls, node_data: Dict[str, Any]) -> 'ItemViewModel':
        """노드 데이터로부터 ItemViewModel 객체를 생성합니다.
        
        Args:
            node_data: 노드 데이터 딕셔너리
            
        Returns:
            생성된 ItemViewModel 인스턴스
        """
        data = ItemData(
            name=node_data.get('name', ''),
            inp=node_data.get('inp', 'M'),
            sub_con=node_data.get('sub_con', ''),
            sub=node_data.get('sub', 'click'),
            parent_id=node_data.get('parent_id')
        )
        return cls(data=data)
    
    @classmethod
    def create_group(cls, name: str) -> 'ItemViewModel':
        """그룹 아이템을 생성합니다.
        
        Args:
            name: 그룹 이름
            
        Returns:
            생성된 그룹 아이템
        """
        data = ItemData(
            name=f"G:{name}",
            inp="",
            sub_con="",
            sub=""
        )
        return cls(data=data)
    
    @classmethod
    def create_instance(cls, name: str) -> 'ItemViewModel':
        """인스턴스 아이템을 생성합니다.
        
        Args:
            name: 인스턴스 이름
            
        Returns:
            생성된 인스턴스 아이템
        """
        data = ItemData(
            name=f"I:{name}",
            inp="M",
            sub_con="",
            sub="click"
        )
        return cls(data=data)
    
    @pyqtProperty(str, notify=nameChanged)
    def name(self) -> str:
        """아이템 이름"""
        return self._data.name
    
    @name.setter
    def name(self, value: str) -> None:
        if self._data.name != value:
            self._data.name = value
            self.nameChanged.emit()
    
    @pyqtProperty(str, notify=inpChanged)
    def inp(self) -> str:
        """입력 타입"""
        return self._data.inp
    
    @inp.setter
    def inp(self, value: str) -> None:
        if self._data.inp != value:
            self._data.inp = value
            self.inpChanged.emit()
    
    @pyqtProperty(str, notify=subConChanged)
    def sub_con(self) -> str:
        """하위 연결"""
        return self._data.sub_con
    
    @sub_con.setter
    def sub_con(self, value: str) -> None:
        if self._data.sub_con != value:
            self._data.sub_con = value
            self.subConChanged.emit()
    
    @pyqtProperty(str, notify=subChanged)
    def sub(self) -> str:
        """하위 액션"""
        return self._data.sub
    
    @sub.setter
    def sub(self, value: str) -> None:
        if self._data.sub != value:
            self._data.sub = value
            self.subChanged.emit()
    
    @pyqtProperty(bool, notify=expandedChanged)
    def expanded(self) -> bool:
        """확장 상태"""
        return self._data.expanded
    
    @expanded.setter
    def expanded(self, value: bool) -> None:
        if self._data.expanded != value:
            self._data.expanded = value
            self.expandedChanged.emit()
    
    @pyqtProperty(str)
    def id(self) -> str:
        """아이템 ID"""
        return self._data.id
    
    @pyqtProperty(str)
    def parentId(self) -> str:
        """부모 아이템 ID"""
        return self._data.parent_id or ""
    
    @pyqtProperty('QVariantList', notify=childrenChanged)
    def childrenIds(self) -> List[str]:
        """자식 아이템 ID 목록"""
        return self._data.children_ids
    
    @pyqtSlot(result=str)
    def getNextInputType(self) -> str:
        """다음 입력 타입을 반환합니다."""
        return self._input_cycler.next(self._data.inp)
    
    @pyqtSlot(str, result='QVariantList')
    def getSubActions(self, input_type: str) -> List[str]:
        """입력 타입에 따른 하위 액션 목록을 반환합니다."""
        return self._SUB_ACTIONS.get(input_type, [])
    
    @pyqtSlot(result=bool)
    def toggleInputType(self) -> bool:
        """입력 타입을 토글합니다."""
        try:
            next_inp = self._input_cycler.next(self.inp)
            self.inp = next_inp
            return True
        except Exception as e:
            print(f"입력 타입 토글 오류: {e}")
            return False
    
    @pyqtSlot(dict)
    def updateFromDict(self, data_dict: Dict[str, Any]) -> None:
        """딕셔너리로부터 데이터를 업데이트합니다."""
        if 'name' in data_dict and data_dict['name'] != self.name:
            self.name = data_dict['name']
            
        if 'inp' in data_dict and data_dict['inp'] != self.inp:
            self.inp = data_dict['inp']
            
        if 'sub_con' in data_dict and data_dict['sub_con'] != self.sub_con:
            self.sub_con = data_dict['sub_con']
            
        if 'sub' in data_dict and data_dict['sub'] != self.sub:
            self.sub = data_dict['sub']
            
        if 'expanded' in data_dict and data_dict['expanded'] != self.expanded:
            self.expanded = data_dict['expanded']
            
        if 'children_ids' in data_dict:
            self._data.children_ids = data_dict['children_ids']
            self.childrenChanged.emit()
            
        if 'parent_id' in data_dict:
            self._data.parent_id = data_dict['parent_id']
    
    @pyqtSlot(result=dict)
    def toDict(self) -> Dict[str, Any]:
        """객체를 딕셔너리로 변환합니다."""
        return {
            'id': self.id,
            'name': self.name,
            'inp': self.inp,
            'sub_con': self.sub_con,
            'sub': self.sub,
            'expanded': self.expanded,
            'parent_id': self.parentId,
            'children_ids': self.childrenIds
        }
    
    def is_group(self) -> bool:
        """그룹 아이템인지 확인합니다."""
        return self.name.startswith("G:")
    
    def is_inst(self) -> bool:
        """인스턴스 아이템인지 확인합니다."""
        return self.name.startswith("I:")