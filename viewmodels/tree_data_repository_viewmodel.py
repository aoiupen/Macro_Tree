"""트리 데이터 저장소 뷰모델 모듈

트리 데이터 저장소와 View 사이를 중개하는 뷰모델을 제공합니다.
"""
from typing import Optional
from PyQt6.QtCore import QObject, pyqtSignal, pyqtSlot
from models.interfaces.repository_interface import ITreeDataRepository
from core.tree_state import TreeState
from viewmodels.interfaces.repository_viewmodel_interface import IRepositoryViewModel


class TreeDataRepositoryViewModel(QObject):
    """트리 데이터 저장소 뷰모델 클래스
    
    트리 데이터 저장소와 View 사이를 중개합니다.
    """
    
    dataLoaded = pyqtSignal(TreeState)
    dataSaved = pyqtSignal(bool)
    
    def __init__(self, repository: Optional[ITreeDataRepository] = None):
        """TreeDataRepositoryViewModel 생성자
        
        Args:
            repository: 트리 데이터 저장소 인스턴스 (선택적)
        """
        super().__init__()
        self._repository = repository or TreeDataRepository()
    
    @pyqtSlot()
    def load_tree(self) -> Optional[TreeState]:
        """저장소에서 트리를 로드합니다."""
        tree_state = self._repository.load_tree()
        if tree_state:
            self.dataLoaded.emit(tree_state)
        return tree_state
    
    @pyqtSlot(TreeState)
    def save_tree(self, tree_state: TreeState) -> bool:
        """트리를 저장소에 저장합니다."""
        result = self._repository.save_tree(tree_state)
        self.dataSaved.emit(result)
        return result
    
    @pyqtSlot(TreeState)
    def save_state(self, tree_state: TreeState) -> None:
        """현재 상태를 저장소에 저장합니다."""
        self._repository.save_state(tree_state) 