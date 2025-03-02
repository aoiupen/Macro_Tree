from PyQt5.QtWidgets import QMenu, QAction
from PyQt5.QtCore import Qt, QPoint, pyqtSlot
from PyQt5.QtGui import QCursor, QKeySequence
from package.logic.tree_undo_redo_manager import TreeUndoCommand
from PyQt5.QtWidgets import QTreeWidgetItem

class TreeWidgetEventHandler:
    def __init__(self, tree_widget):
        self.tree_widget = tree_widget

    def tree_drop_event(self, event):
        """드롭 이벤트 처리"""
        target_item = self.tree_widget.itemAt(event.pos())
        if target_item is None:
            return

        self.tree_widget.snapshot()  # 현재 상태를 스냅샷으로 저장

        # 드롭된 아이템 처리 로직
        if event.source() == self.tree_widget:
            selected_items = self.tree_widget.selectedItems()
            for item in selected_items:
                # 드롭할 위치에 따라 부모를 변경하는 로직
                target_parent = target_item.parent() if target_item else self.tree_widget.invisibleRootItem()
                target_parent.addChild(item)
                item.setSelected(False)  # 드롭 후 선택 해제

        event.accept()  # 이벤트 수용

    def context_menu(self, pos):
        index = self.tree_widget.indexAt(pos)
        if not index.isValid():
            return

        item = self.tree_widget.itemAt(pos)
        name = item.logic.name

        menu = QMenu()
        menu.addAction("action")
        menu.addAction(name)
        menu.addSeparator()
        action_1 = menu.addAction("Choix 1")
        action_2 = menu.addAction("Choix 2")
        menu.addSeparator()
        action_3 = menu.addAction("Choix 3")
        menu.exec_(self.tree_widget.mapToGlobal(pos))

    def key_press_event(self, event):
        if event.key() == Qt.Key_Delete:
            self.delete_selected_items()
        elif event.matches(QKeySequence.Copy):
            self.copy_selected_items()
        elif event.matches(QKeySequence.Paste):
            self.paste_selected_items()
        elif event.matches(QKeySequence.Undo):
            self.tree_widget.undoStack.undo()
        elif event.matches(QKeySequence.Redo):
            self.tree_widget.undoStack.redo()
        else:
            self.tree_widget.keyPressEvent(event)

    def delete_selected_items(self):
        old_state = self.tree_widget.tree_state
        for sel_it in self.tree_widget.selectedItems():
            (sel_it.parent() or self.tree_widget.invisibleRootItem()).removeChild(sel_it)
        self.tree_widget.update_tree_state()
        new_state = self.tree_widget.tree_state
        self.tree_widget.undoStack.push(TreeUndoCommand(self.tree_widget, old_state, new_state))

    def copy_selected_items(self):
        sel_it_name_list = [sel_it.logic.name for sel_it in self.tree_widget.selectedItems()]
        self.tree_widget.sel_nd_it_list = [sel_it for sel_it in self.tree_widget.selectedItems() if sel_it.logic.prnt not in sel_it_name_list]

    def paste_selected_items(self):
        old_state = self.tree_widget.tree_state
        dst_it = self.tree_widget.currentItem()
        if dst_it and dst_it.logic.is_group():
            for sel_nd_it in self.tree_widget.sel_nd_it_list:
                row = [sel_nd_it.logic.prnt, sel_nd_it.logic.name, sel_nd_it.logic.inp, sel_nd_it.logic.sub_con, sel_nd_it.logic.sub]
                self.tree_widget.create_tree_item_with_id(dst_it, row)
        self.tree_widget.update_tree_state()
        new_state = self.tree_widget.tree_state
        self.tree_widget.undoStack.push(TreeUndoCommand(self.tree_widget, old_state, new_state))
        self.tree_widget.save_to_db() # 스냅샷으로 바꿔야

    def mouse_press_event(self, event):
        if event.modifiers() != Qt.ControlModifier:
            return self.tree_widget.mousePressEvent(event)

    def mouse_release_event(self, event):
        if event.modifiers() == Qt.ControlModifier:
            self.tree_widget.mousePressEvent(event)
            items = self.tree_widget.currentItem()
            if items:
                self.tree_widget.setCurrentItem(items)
        return self.tree_widget.mouseReleaseEvent(event)

    def context_menu_event(self, event):
        self.tree_widget.ctxt = QMenu(self.tree_widget)
        del_act = QAction('Delete', self.tree_widget)
        ungr_act = QAction('Ungroup', self.tree_widget)
        gr_act = QAction('Group', self.tree_widget)
        del_act.triggered.connect(lambda: self.tree_widget.recur_del(event))
        ungr_act.triggered.connect(lambda: self.tree_widget.ungroup_sel_items(event))
        gr_act.triggered.connect(lambda: self.tree_widget.group_sel_items(event))
        self.tree_widget.ctxt.addActions([del_act, ungr_act, gr_act])
        self.tree_widget.ctxt.popup(QCursor.pos())

    def on_item_clicked(self, item, column):
        # 아이템 클릭 처리 로직
        print(f"Item clicked: {item.text(0)}")  # 예시로 클릭된 아이템의 텍스트 출력