from PyQt5.QtWidgets import QMenu, QAction
from PyQt5.QtCore import Qt, QPoint, pyqtSlot
from PyQt5.QtGui import QCursor, QKeySequence

class TreeWidgetEventHandler:
    def __init__(self, tree_widget):
        self.tree_widget = tree_widget

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
        self.tree_widget.save_to_db()

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

    @pyqtSlot(QTreeWidgetItem, int)
    def on_item_clicked(self, it, col):
        pass