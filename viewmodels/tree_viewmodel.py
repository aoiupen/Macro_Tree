# macro_tree/viewmodels/tree_viewmodel.py
"""트리 뷰모델 모듈

트리 위젯의 상태와 동작을 관리하는 뷰모델을 제공합니다.
"""
from PyQt5.QtCore import QObject, pyqtProperty, pyqtSignal, pyqtSlot
from viewmodels.tree_executor import TreeExecutor
from core.tree_state import TreeState
from typing import Optional

class TreeViewModel(QObject):
    """트리 뷰모델 클래스
    
    트리 위젯의 상태와 동작을 관리합니다.
    """
    
    dataChanged = pyqtSignal()
    
    def __init__(self, tree_executor: TreeExecutor):
        """TreeViewModel 생성자
        
        Args:
            tree_executor: 트리 실행기 인스턴스
        """
        super().__init__()
        self._tree_executor = tree_executor
        self._tree_state: Optional[TreeState] = None
        
    @pyqtProperty(TreeState, notify=dataChanged)
    def tree_state(self) -> Optional[TreeState]:
        """현재 트리 상태를 반환합니다."""
        return self._tree_state
        
    @tree_state.setter
    def tree_state(self, value: TreeState) -> None:
        """트리 상태를 설정합니다.
        
        Args:
            value: 새로운 트리 상태
        """
        self._tree_state = value
        self.dataChanged.emit()
    
    @pyqtSlot(str)
    def execute_item(self, item_id: str) -> None:
        """지정된 아이템을 실행합니다.
        
        Args:
            item_id: 실행할 아이템의 ID
        """
        self._tree_executor.execute_item(item_id)
        self.dataChanged.emit()