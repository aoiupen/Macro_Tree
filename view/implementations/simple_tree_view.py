from PyQt5.QtWidgets import (QTreeWidget, QTreeWidgetItem, QApplication, QStyle, 
                         QMenu, QAction, QInputDialog, QMessageBox)
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtGui import QCursor

from ...viewmodel.implementations.simple_tree_viewmodel import SimpleTreeViewModel

class SimpleTreeView(QTreeWidget):
    def __init__(self, viewmodel, parent=None):
        super().__init__(parent)
        self._viewmodel = viewmodel
        
        # 이벤트 연결
        self.itemClicked.connect(self.item_clicked)
        self.itemExpanded.connect(self._on_item_expanded)
        self.itemCollapsed.connect(self._on_item_collapsed)
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self._show_context_menu)
        
        # 드래그 앤 드롭 설정
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.setDropIndicatorShown(True)
        self.setDragDropMode(QTreeWidget.InternalMove)
        
        self.setHeaderLabel("트리 아이템")
        self.update_tree_items()
    
    def set_viewmodel(self, viewmodel):
        """
        뷰모델을 설정합니다.
        
        Args:
            viewmodel: 새 뷰모델
        """
        self._viewmodel = viewmodel
        self.update_tree_items()
    
    def update_tree_items(self):
        # 현재 선택 상태 기억
        selected_ids = self._viewmodel.get_selected_items()
        
        self.clear()
        
        # 아이템 ID -> QTreeWidgetItem 매핑
        self._id_to_widget_map = {}
        
        # 부모-자식 관계 처리를 위한 두 단계 접근법
        self._build_tree_items()
        self._apply_tree_state()
    
    def _build_tree_items(self):
        # 1단계: 모든 아이템 생성
        all_items = self._viewmodel.get_tree_items()
        
        # 먼저 루트 아이템 추가
        for item_id, item in all_items.items():
            parent_id = item.get_property("parent_id")
            if not parent_id:
                self._add_tree_item(item, self)
        
        # 다음 자식 아이템 추가 (부모 참조로)
        for item_id, item in all_items.items():
            parent_id = item.get_property("parent_id")
            if parent_id and parent_id in self._id_to_widget_map:
                parent_widget = self._id_to_widget_map[parent_id]
                self._add_tree_item(item, parent_widget)
    
    def _add_tree_item(self, item, parent):
        widget_item = QTreeWidgetItem(parent)
        widget_item.setText(0, item.get_property("name", ""))
        widget_item.setData(0, Qt.UserRole, item.get_id())
        
        # 내장 확장/축소 아이콘 자동 사용
        
        # ID -> 위젯 매핑 저장
        self._id_to_widget_map[item.get_id()] = widget_item
        return widget_item
    
    def _apply_tree_state(self):
        # 2단계: 확장/선택 상태 적용
        for item_id, widget_item in self._id_to_widget_map.items():
            item = self._viewmodel.get_item(item_id)
            if item:
                # 확장 상태 적용
                if item.get_property("expanded", False):
                    self.expandItem(widget_item)
                
                # 선택 상태 적용
                if item_id in self._viewmodel.get_selected_items():
                    widget_item.setSelected(True)
    
    def item_clicked(self, item, column):
        item_id = item.data(0, Qt.UserRole)
        self._viewmodel.select_item(item_id)
        self.update_tree_items()
    
    def _on_item_expanded(self, item):
        item_id = item.data(0, Qt.UserRole)
        self._viewmodel.toggle_expanded(item_id, True)
    
    def _on_item_collapsed(self, item):
        item_id = item.data(0, Qt.UserRole)
        self._viewmodel.toggle_expanded(item_id, False)
        
    def _show_context_menu(self, position):
        """컨텍스트 메뉴 표시"""
        item = self.itemAt(position)
        
        menu = QMenu()
        
        # 항상 사용 가능한 액션
        action_add_root = menu.addAction("루트 항목 추가")
        
        # 아이템 선택 시에만 사용 가능한 액션들
        if item:
            item_id = item.data(0, Qt.UserRole)
            
            menu.addSeparator()
            action_add_child = menu.addAction("하위 항목 추가")
            action_rename = menu.addAction("이름 변경")
            action_delete = menu.addAction("삭제")
            
        # 메뉴 표시 및 선택 처리
        action = menu.exec_(self.mapToGlobal(position))
        
        # 선택된 액션 처리
        if action == action_add_root:
            self._add_new_item()
        elif item and action == action_add_child:
            self._add_new_item(item_id)
        elif item and action == action_rename:
            self._rename_item(item_id)
        elif item and action == action_delete:
            self._delete_item(item_id)
    
    def _add_new_item(self, parent_id=None):
        """새 아이템 추가"""
        name, ok = QInputDialog.getText(self, "새 항목", "항목 이름:")
        if ok and name:
            new_id = self._viewmodel.add_item(name, parent_id)
            if new_id:
                self.update_tree_items()
                # 새 아이템 선택
                self._viewmodel.select_item(new_id)
                self.update_tree_items()
    
    def _rename_item(self, item_id):
        """아이템 이름 변경"""
        item = self._viewmodel.get_item(item_id)
        if not item:
            return
            
        current_name = item.get_property("name", "")
        name, ok = QInputDialog.getText(self, "이름 변경", "새 이름:", text=current_name)
        if ok and name:
            self._viewmodel.update_item(item_id, name=name)
            self.update_tree_items()
    
    def _delete_item(self, item_id):
        """아이템 삭제"""
        item = self._viewmodel.get_item(item_id)
        if not item:
            return
            
        name = item.get_property("name", "")
        reply = QMessageBox.question(self, "항목 삭제", 
                                    f"'{name}' 항목을 삭제하시겠습니까?\n모든 하위 항목도 함께 삭제됩니다.",
                                    QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            self._viewmodel.delete_item(item_id)
            self.update_tree_items()
            
    def dropEvent(self, event):
        """
        드래그 앤 드롭으로 아이템 이동 시 호출됨
        """
        # 드롭 대상 (위치)
        drop_indicator = self.dropIndicatorPosition()
        target_item = self.itemAt(event.pos())
        
        # 드래그 중인 아이템 (QTreeWidgetItem)
        dragged_item = self.currentItem()
        
        if not dragged_item or not target_item:
            event.ignore()
            return
            
        dragged_id = dragged_item.data(0, Qt.UserRole)
        target_id = target_item.data(0, Qt.UserRole)
        
        if dragged_id == target_id:
            event.ignore()
            return
            
        # 드롭 위치에 따라 처리
        if drop_indicator == QTreeWidget.OnItem:
            # 항목 위에 드롭: 하위 항목으로 이동
            self._viewmodel.move_item(dragged_id, target_id)
        elif drop_indicator == QTreeWidget.AboveItem or drop_indicator == QTreeWidget.BelowItem:
            # 항목 위나 아래에 드롭: 같은 레벨로 이동
            target_parent_id = self._viewmodel.get_item(target_id).get_property("parent_id")
            self._viewmodel.move_item(dragged_id, target_parent_id)
        else:
            # 기타 위치 (루트 레벨로 이동)
            self._viewmodel.move_item(dragged_id, None)
            
        # UI 갱신
        self.update_tree_items()
        
        # 기본 처리 무시 (직접 처리했으므로)
        event.accept()
