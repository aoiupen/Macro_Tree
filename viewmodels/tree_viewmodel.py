from PyQt6.QtCore import QObject, pyqtProperty, pyqtSignal, pyqtSlot
from viewmodels.tree_executor import TreeExecutor
from core.tree_state import TreeState
from models.tree_data_repository import TreeDataRepository
from typing import Optional

class TreeViewModel(QObject):
    """트리 뷰모델 클래스"""
    
    dataChanged = pyqtSignal()
    selectionChanged = pyqtSignal(list)
    
    def __init__(self, tree_executor: TreeExecutor, repository=None):
        """TreeViewModel 생성자"""
        super().__init__()
        self._tree_executor = tree_executor
        self._repository = repository or TreeDataRepository()
        self._tree_state = self._repository.load_tree()
        self._selected_items = []
    
    @pyqtProperty(TreeState, notify=dataChanged)
    def tree_state(self):
        """현재 트리 상태를 반환합니다."""
        return self._tree_state
    
    @tree_state.setter
    def tree_state(self, value):
        self._tree_state = value
        self.dataChanged.emit()
    
    @pyqtProperty(list, notify=selectionChanged)
    def selectedItems(self):
        """선택된 아이템 목록을 반환합니다."""
        return self._selected_items
    
    @pyqtSlot(list)
    def setSelectedItems(self, items):
        """선택된 아이템을 설정합니다."""
        self._selected_items = items
        self.selectionChanged.emit(items)
    
    @pyqtSlot(str)
    def execute_item(self, item_id):
        """아이템을 실행합니다."""
        self._tree_executor.execute_item(item_id)
        self.dataChanged.emit()
    
    @pyqtSlot(result=bool)
    def addGroup(self):
        """그룹을 추가합니다."""
        parent_id = self._get_selected_parent_id()
        success = self._repository.add_group(self._tree_state, parent_id)
        if success:
            self.dataChanged.emit()
        return success
    
    @pyqtSlot(result=bool)
    def addInstance(self):
        """인스턴스를 추가합니다."""
        parent_id = self._get_selected_parent_id()
        success = self._repository.add_instance(self._tree_state, parent_id)
        if success:
            self.dataChanged.emit()
        return success
    
    @pyqtSlot(result=bool)
    def saveTree(self):
        """트리를 저장합니다."""
        return self._repository.save_tree(self._tree_state)
    
    @pyqtSlot(result=bool)
    def undo(self):
        """실행 취소합니다."""
        if self._repository.state_manager.can_undo():
            state = self._repository.state_manager.undo()
            if state:
                self._tree_state = state
                self.dataChanged.emit()
                return True
        return False
    
    @pyqtSlot(result=bool)
    def redo(self):
        """다시 실행합니다."""
        if self._repository.state_manager.can_redo():
            state = self._repository.state_manager.redo()
            if state:
                self._tree_state = state
                self.dataChanged.emit()
                return True
        return False
    
    def _get_selected_parent_id(self):
        """선택된 부모 ID를 반환합니다."""
        if not self._selected_items:
            return self._repository.get_root_id()
        
        selected_id = self._selected_items[0]
        if self._repository.is_group(self._tree_state, selected_id):
            return selected_id
        
        parent_id = self._repository.get_parent_id(self._tree_state, selected_id)
        return parent_id if parent_id else self._repository.get_root_id()
    
    @pyqtProperty(bool, notify=dataChanged)
    def canUndo(self):
        """Undo 가능 여부"""
        return self._repository.state_manager.can_undo()
    
    @pyqtProperty(bool, notify=dataChanged)
    def canRedo(self):
        """Redo 가능 여부"""
        return self._repository.state_manager.can_redo()
    
    @pyqtSlot(result=bool)
    def undo(self):
        """실행 취소"""
        if self.canUndo:
            state = self._repository.state_manager.undo()
            if state:
                self._tree_state = state
                self.dataChanged.emit()
                return True
        return False