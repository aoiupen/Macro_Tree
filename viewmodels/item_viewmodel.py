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
        except (ValueError, IndexError):
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
    
    def __init__(self, parent: Optional[QObject] = None):
        """ItemViewModel 생성자
        
        Args:
            parent: 부모 객체
        """
        super().__init__(parent)
        
        # 데이터 초기화
        self._data = ItemData()
        
        # 액션 타입 순환 리스트
        self._m_actions_cyclic = CyclicList(self._M_ACTIONS)
    
    # QML 프로퍼티 정의
    @pyqtProperty(str, notify=nameChanged)
    def name(self) -> str:
        """아이템 이름 프로퍼티"""
        return self._data.name
    
    @name.setter
    def name(self, value: str) -> None:
        if self._data.name != value:
            self._data.name = value
            self.nameChanged.emit()
    
    @pyqtProperty(str, notify=inpChanged)
    def inp(self) -> str:
        """입력 타입 프로퍼티"""
        return self._data.inp
    
    @inp.setter
    def inp(self, value: str) -> None:
        if self._data.inp != value:
            self._data.inp = value
            self.inpChanged.emit()
    
    @pyqtProperty(str, notify=subConChanged)
    def subCon(self) -> str:
        """서브 컨디션 프로퍼티"""
        return self._data.sub_con
    
    @subCon.setter
    def subCon(self, value: str) -> None:
        if self._data.sub_con != value:
            self._data.sub_con = value
            self.subConChanged.emit()
    
    @pyqtProperty(str, notify=subChanged)
    def sub(self) -> str:
        """서브 프로퍼티"""
        return self._data.sub
    
    @sub.setter
    def sub(self, value: str) -> None:
        if self._data.sub != value:
            self._data.sub = value
            self.subChanged.emit()
    
    @pyqtProperty(bool, notify=expandedChanged)
    def expanded(self) -> bool:
        """확장 상태 프로퍼티"""
        return self._data.expanded
    
    @expanded.setter
    def expanded(self, value: bool) -> None:
        if self._data.expanded != value:
            self._data.expanded = value
            self.expandedChanged.emit()
    
    @pyqtProperty(str)
    def id(self) -> str:
        """아이템 ID 프로퍼티"""
        return self._data.id
    
    @pyqtProperty(str)
    def parentId(self) -> str:
        """부모 아이템 ID 프로퍼티"""
        return self._data.parent_id or ""
    
    @pyqtProperty('QVariantList', notify=childrenChanged)
    def childrenIds(self) -> List[str]:
        """자식 아이템 ID 리스트 프로퍼티"""
        return self._data.children_ids
    
    # 액션 관련 메서드
    @pyqtSlot(result=str)
    def getNextInputType(self) -> str:
        """다음 입력 타입을 반환합니다."""
        return self._m_actions_cyclic.next(self._data.inp)
    
    @pyqtSlot(str, result='QVariantList')
    def getSubActions(self, input_type: str) -> List[str]:
        """입력 타입에 따른 서브 액션 리스트를 반환합니다."""
        return self._SUB_ACTIONS.get(input_type, [])
    
    @pyqtSlot(result=bool)
    def toggleInputType(self) -> bool:
        """입력 타입을 토글합니다."""
        next_type = self.getNextInputType()
        self.inp = next_type
        return True
    
    # 데이터 관리 메서드
    @pyqtSlot(dict)
    def updateFromDict(self, data_dict: Dict[str, Any]) -> None:
        """딕셔너리에서 데이터를 업데이트합니다."""
        if 'name' in data_dict and self._data.name != data_dict['name']:
            self._data.name = data_dict['name']
            self.nameChanged.emit()
            
        if 'inp' in data_dict and self._data.inp != data_dict['inp']:
            self._data.inp = data_dict['inp']
            self.inpChanged.emit()
            
        if 'sub_con' in data_dict and self._data.sub_con != data_dict['sub_con']:
            self._data.sub_con = data_dict['sub_con']
            self.subConChanged.emit()
            
        if 'sub' in data_dict and self._data.sub != data_dict['sub']:
            self._data.sub = data_dict['sub']
            self.subChanged.emit()
            
        if 'expanded' in data_dict and self._data.expanded != data_dict['expanded']:
            self._data.expanded = data_dict['expanded']
            self.expandedChanged.emit()
            
        if 'id' in data_dict:
            self._data.id = data_dict['id']
            
        if 'parent_id' in data_dict:
            self._data.parent_id = data_dict['parent_id']
            
        if 'children_ids' in data_dict:
            self._data.children_ids = data_dict['children_ids']
            self.childrenChanged.emit()
    
    @pyqtSlot(result=dict)
    def toDict(self) -> Dict[str, Any]:
        """아이템 데이터를 딕셔너리로 변환합니다."""
        return {
            'id': self._data.id,
            'name': self._data.name,
            'inp': self._data.inp,
            'sub_con': self._data.sub_con,
            'sub': self._data.sub,
            'expanded': self._data.expanded,
            'parent_id': self._data.parent_id,
            'children_ids': self._data.children_ids
        }