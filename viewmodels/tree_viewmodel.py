from PyQt6.QtCore import QObject, pyqtProperty, pyqtSignal, pyqtSlot
from viewmodels.tree_executor import TreeExecutor
from core.tree_state import TreeState
from models.tree_data_repository import TreeDataRepository
from typing import Optional

class TreeViewModel(QObject):
    """트리 뷰모델 클래스"""
    
    dataChanged = pyqtSignal()
    selectionChanged = pyqtSignal(list)
    
    def __init__(self, state_manager):
        """TreeViewModel 생성자"""
        super().__init__()
        self._state_manager = state_manager
        # View 계층은 직접 관리하지 않음
    
    @pyqtProperty(TreeState, notify=dataChanged)
    def tree_state(self):
        """현재 트리 상태를 반환합니다."""
        return self._state_manager.current_state()
    
    @pyqtProperty(list, notify=selectionChanged)
    def selectedItems(self):
        """선택된 아이템 목록을 반환합니다."""
        return self._state_manager.selected_items
    
    @pyqtSlot(list)
    def setSelectedItems(self, items):
        """선택된 아이템을 설정합니다."""
        self._state_manager.selected_items = items
        self.selectionChanged.emit(items)
    
    @pyqtSlot(str)
    def executeItem(self, item_id):
        """아이템을 실행합니다."""
        self._state_manager.execute_item(item_id)
        self.dataChanged.emit()
    
    @pyqtSlot(result=bool)
    def addGroup(self):
        """그룹을 추가합니다."""
        parent_id = self._get_selected_parent_id()
        success = self._state_manager.add_group(self.tree_state, parent_id)
        if success:
            self.dataChanged.emit()
        return success
    
    @pyqtSlot(result=bool)
    def addInstance(self):
        """인스턴스를 추가합니다."""
        parent_id = self._get_selected_parent_id()
        success = self._state_manager.add_instance(self.tree_state, parent_id)
        if success:
            self.dataChanged.emit()
        return success
    
    @pyqtSlot(result=bool)
    def saveTree(self):
        """트리를 저장합니다."""
        return self._state_manager.save_tree(self.tree_state)
    
    @pyqtSlot(result=bool)
    def undo(self):
        """실행 취소합니다."""
        if self._state_manager.can_undo():
            state = self._state_manager.undo()
            if state:
                self._state_manager.current_state = state
                self.dataChanged.emit()
                return True
        return False
    
    @pyqtSlot(result=bool)
    def redo(self):
        """다시 실행합니다."""
        if self._state_manager.can_redo():
            state = self._state_manager.redo()
            if state:
                self._state_manager.current_state = state
                self.dataChanged.emit()
                return True
        return False
    
    def _get_selected_parent_id(self):
        """선택된 부모 ID를 반환합니다."""
        if not self._state_manager.selected_items:
            return self._state_manager.get_root_id()
        
        selected_id = self._state_manager.selected_items[0]
        if self._state_manager.is_group(self.tree_state, selected_id):
            return selected_id
        
        parent_id = self._state_manager.get_parent_id(self.tree_state, selected_id)
        return parent_id if parent_id else self._state_manager.get_root_id()
    
    @pyqtProperty(bool, notify=dataChanged)
    def canUndo(self):
        """Undo 가능 여부"""
        return self._state_manager.can_undo()
    
    @pyqtProperty(bool, notify=dataChanged)
    def canRedo(self):
        """Redo 가능 여부"""
        return self._state_manager.can_redo()
    
    @pyqtSlot(list)
    def deleteItems(self, item_ids):
        """항목들을 삭제합니다."""
        self._save_current_state()
        
        # 삭제 로직 처리
        for item_id in item_ids:
            self._state_manager.delete_item(self.tree_state, item_id)
        
        self._notify_state_changed()
    
    @pyqtSlot(int, int)
    def moveItem(self, source_index, target_index):
        """항목 위치를 이동합니다."""
        # 상태 저장
        self._state_manager.save_state(self.tree_state)
        
        # 이동 로직 처리
        success = self._state_manager.move_item(self.tree_state, source_index, target_index)
        
        # 상태 변경 알림
        if success:
            self.dataChanged.emit()
        
        return success
    
    @pyqtSlot(object)
    def save_state(self, state):
        """현재 상태를 저장합니다."""
        self._state_manager.save_state(state)
        self.dataChanged.emit()
    
    @pyqtSlot()
    def begin_change(self):
        """변경 시작을 알립니다."""
        self._save_current_state()
    
    @pyqtSlot(object)
    def end_change(self, new_state):
        """변경 완료를 알립니다."""
        self._state_manager.current_state = new_state
        self._notify_state_changed()
    
    @pyqtSlot(str, int, str)
    def update_item_property(self, item_id, property_index, value):
        """항목 속성을 업데이트합니다."""
        # 상태 저장
        self._state_manager.save_state(self.tree_state)
        
        # 속성 업데이트 로직
        prop_names = ["name", "inp", "sub_con", "sub"]
        if 0 <= property_index < len(prop_names):
            prop_name = prop_names[property_index]
            success = self._state_manager.update_item_property(self.tree_state, item_id, prop_name, value)
            if success:
                self.dataChanged.emit()
    
    @pyqtSlot(str, bool)
    def update_item_expanded_state(self, item_id, is_expanded):
        """아이템 확장 상태를 업데이트합니다."""
        # 상태 저장
        self._state_manager.save_state(self.tree_state)
        
        # 아이템 확장 상태 업데이트
        success = self._state_manager.update_item_expanded_state(self.tree_state, item_id, is_expanded)
        
        # 상태 변경 알림
        if success:
            self.dataChanged.emit()

    def _save_current_state(self):
        """현재 상태를 저장합니다."""
        self._state_manager.save_state(self.tree_state)

    def _notify_state_changed(self):
        """상태 변경을 알립니다."""
        self.dataChanged.emit()