from PyQt6.QtWidgets import QMenu, QInputDialog, QMessageBox
from PyQt6.QtCore import Qt

class ContextMenuTreeViewMixin:
    # 컨텍스트 메뉴 표시 및 부가 액션 메서드
    def _show_context_menu(self, position):
        item = self.itemAt(position)
        menu = QMenu()
        action_add_root = menu.addAction("루트 항목 추가")
        if item:
            item_id = item.data(0, Qt.UserRole)
            menu.addSeparator()
            action_add_child = menu.addAction("하위 항목 추가")
            action_rename = menu.addAction("이름 변경")
            action_delete = menu.addAction("삭제")
        action = menu.exec(self.mapToGlobal(position))
        if action == action_add_root:
            self._add_new_item()
        elif item and action == action_add_child:
            self._add_new_item(item_id)
        elif item and action == action_rename:
            self._rename_item(item_id)
        elif item and action == action_delete:
            self._delete_item(item_id)
            
    # 컨텍스트 메뉴의 add 기능
    def _add_new_item(self, parent_id=None):
        name, ok = QInputDialog.getText(self, "새 항목", "항목 이름:")
        if ok and name:
            new_id = self._viewmodel.add_item(name, parent_id)
            if new_id:
                self.update_tree_items()
                self._viewmodel.select_item(new_id)
                self.update_tree_items()

    def _rename_item(self, item_id):
        item = self._viewmodel.get_item(item_id)
        if not item:
            return
        current_name = item.get_property("name", "")
        name, ok = QInputDialog.getText(self, "이름 변경", "새 이름:", text=current_name)
        if ok and name:
            self._viewmodel.update_item(item_id, name=name)
            self.update_tree_items()

    def _delete_item(self, item_id):
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