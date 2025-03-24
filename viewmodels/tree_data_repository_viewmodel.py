"""트리 데이터 저장소 뷰모델 모듈

트리 데이터 저장소와 View 사이를 중개하는 뷰모델을 제공합니다.
"""
from typing import Optional
from PyQt6.QtCore import QObject, pyqtSignal, pyqtSlot
from models.tree_data_repository import TreeDataRepository
from models.interfaces.repository_interface import ITreeDataRepository
from models.dummy_data import get_default_tree
from core.tree_state import TreeState
from core.tree_state_manager import TreeStateManager
from viewmodels.interfaces.repository_viewmodel_interface import IRepositoryViewModel


class TreeDataRepositoryViewModel(QObject):
    """트리 데이터 저장소 뷰모델 클래스
    
    트리 데이터 저장소와 View 사이를 중개합니다.
    """
    
    dataLoaded = pyqtSignal(TreeState)
    dataSaved = pyqtSignal(bool)
    stateChanged = pyqtSignal(TreeState)
    
    def __init__(self, repository: Optional[ITreeDataRepository] = None):
        """TreeDataRepositoryViewModel 생성자
        
        Args:
            repository: 트리 데이터 저장소 인스턴스 (선택적)
        """
        super().__init__()
        self._repository = repository or TreeDataRepository()
        self._state_manager = TreeStateManager()
        
        # 상태 관리자 변경 시그널 연결
        self._state_manager.stateChanged.connect(self._on_state_changed)
    
    def _on_state_changed(self):
        """상태 변경 시 호출되는 슬롯"""
        current_state = self.get_current_state()
        if current_state:
            self.stateChanged.emit(current_state)
    
    @pyqtSlot(result=TreeState)
    def get_current_state(self) -> Optional[TreeState]:
        """현재 상태를 반환합니다."""
        return self._state_manager.current_state()
    
    @pyqtSlot(result=bool)
    def create_new_tree(self) -> bool:
        """새 트리를 생성합니다.
        
        Returns:
            성공 여부
        """
        try:
            # 기본 트리 생성
            new_tree = get_default_tree()
            
            # 상태 관리자에 저장
            self._state_manager.clear()
            self._state_manager.save_state(new_tree)
            
            # 변경 이벤트 발생
            self.stateChanged.emit(new_tree)
            
            return True
        except Exception as e:
            print(f"새 트리 생성 오류: {e}")
            return False
    
    @pyqtSlot(result=bool)
    def load_tree_from_db(self) -> bool:
        """데이터베이스에서 트리를 로드합니다.
        
        Returns:
            로드 성공 여부
        """
        try:
            tree_state = self._repository.load_tree()
            if tree_state:
                # 상태 관리자에 다시 저장
                self._state_manager.clear()
                self._state_manager.save_state(tree_state)
                
                # 데이터 로드 이벤트 발생
                self.dataLoaded.emit(tree_state)
                return True
            return False
        except Exception as e:
            print(f"트리 로드 오류: {e}")
            return False
    
    @pyqtSlot(TreeState, result=bool)
    def save_tree(self, tree_state: TreeState) -> bool:
        """트리를 저장소에 저장합니다."""
        result = self._repository.save_tree(tree_state)
        self.dataSaved.emit(result)
        return result
    
    @pyqtSlot(result=bool)
    def save_current_tree(self) -> bool:
        """현재 트리 상태를 DB에 저장합니다."""
        current_state = self.get_current_state()
        if current_state:
            return self.save_tree(current_state)
        return False
    
    @pyqtSlot(TreeState)
    def save_state(self, tree_state: TreeState) -> None:
        """현재 상태를 상태 관리자에 저장합니다."""
        self._state_manager.save_state(tree_state)
    
    @pyqtSlot(result=bool)
    def can_undo(self) -> bool:
        """실행 취소 가능 여부를 반환합니다."""
        return self._state_manager.can_undo()
    
    @pyqtSlot(result=bool)
    def can_redo(self) -> bool:
        """다시 실행 가능 여부를 반환합니다."""
        return self._state_manager.can_redo()
    
    @pyqtSlot(result=bool)
    def undo(self) -> bool:
        """변경 사항을 취소합니다."""
        return self._state_manager.undo() is not None
    
    @pyqtSlot(result=bool)
    def redo(self) -> bool:
        """취소한 변경 사항을 다시 적용합니다."""
        return self._state_manager.redo() is not None
    
    @pyqtSlot()
    def clear_history(self) -> None:
        """상태 이력을 모두 지웁니다."""
        self._state_manager.clear() 