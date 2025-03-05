"""트리 위젯 이벤트 핸들러 모듈

트리 위젯의 이벤트를 처리하는 클래스를 제공합니다.
"""
from typing import List, Optional
from PyQt5.QtWidgets import QMenu, QAction, QTreeWidgetItem, QTreeWidget
from PyQt5.QtCore import Qt, QPoint, pyqtSlot
from PyQt5.QtGui import QCursor, QKeySequence, QDropEvent, QMouseEvent, QKeyEvent
from package.logic.tree_undo_redo_manager import TreeUndoCommand


class TreeWidgetEventHandler:
    """트리 위젯 이벤트 핸들러 클래스
    
    트리 위젯의 다양한 이벤트를 처리합니다.
    """

    def __init__(self, tree_widget: QTreeWidget) -> None:
        """TreeWidgetEventHandler 생성자
        
        Args:
            tree_widget: 이벤트를 처리할 트리 위젯
        """
        self.tree_widget = tree_widget

    def tree_drop_event(self, event: QDropEvent) -> None:
        """드롭 이벤트를 처리합니다.
        
        Args:
            event: 드롭 이벤트 객체
        """
        target_item = self.tree_widget.itemAt(event.pos())
        if target_item is None:
            return

        # 현재 상태를 스냅샷으로 저장
        self.tree_widget.snapshot_manager.add_snapshot(self.tree_widget.tree_state)

        # 드롭된 아이템 처리
        if event.source() == self.tree_widget:
            selected_items = self.tree_widget.selectedItems()
            for item in selected_items:
                target_parent = target_item if target_item.parent() else target_item
                target_parent.addChild(item)
                item.setSelected(False)  # 드롭 후 선택 해제

        event.accept()

    def mouse_press_event(self, event: QMouseEvent) -> None:
        """마우스 클릭 이벤트를 처리합니다.
        
        Args:
            event: 마우스 이벤트 객체
        """
        if event.modifiers() != Qt.ControlModifier:
            super(self.tree_widget.__class__, self.tree_widget).mousePressEvent(event)

    def mouse_release_event(self, event: QMouseEvent) -> None:
        """마우스 버튼 해제 이벤트를 처리합니다.
        
        Args:
            event: 마우스 이벤트 객체
        """
        if event.modifiers() == Qt.ControlModifier:
            super(self.tree_widget.__class__, self.tree_widget).mousePressEvent(event)
            items = self.tree_widget.currentItem()
            if items:
                self.tree_widget.setCurrentItem(items)
        super(self.tree_widget.__class__, self.tree_widget).mouseReleaseEvent(event)

    def context_menu(self, pos: QPoint) -> None:
        """컨텍스트 메뉴를 표시합니다.
        
        Args:
            pos: 메뉴를 표시할 위치
        """
        index = self.tree_widget.indexAt(pos)
        if not index.isValid():
            return

        item = self.tree_widget.itemAt(pos)
        name = item.logic.name

        menu = QMenu()
        menu.addAction("action")
        menu.addAction(name)
        menu.addSeparator()
        menu.addAction("Choix 1")
        menu.addAction("Choix 2")
        menu.addSeparator()
        menu.addAction("Choix 3")
        menu.exec_(self.tree_widget.mapToGlobal(pos))

    def key_press_event(self, event: QKeyEvent) -> None:
        """키 입력 이벤트를 처리합니다.
        
        Args:
            event: 키 이벤트 객체
        """
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
            super(self.tree_widget.__class__, self.tree_widget).keyPressEvent(event)

    def delete_selected_items(self) -> None:
        """선택된 아이템들을 삭제합니다."""
        old_state = self.tree_widget.tree_state
        for selected_item in self.tree_widget.selectedItems():
            (selected_item.parent() or self.tree_widget.invisibleRootItem()).removeChild(selected_item)
        self.tree_widget.update_tree_state()
        new_state = self.tree_widget.tree_state
        self.tree_widget.undoStack.push(TreeUndoCommand(self.tree_widget, old_state, new_state))

    def copy_selected_items(self) -> None:
        """선택된 아이템들을 복사합니다."""
        selected_item_names = [item.logic.name for item in self.tree_widget.selectedItems()]
        self.tree_widget.selected_node_items = [
            item for item in self.tree_widget.selectedItems()
            if item.logic.parent_id not in selected_item_names
        ]

    def paste_selected_items(self) -> None:
        """복사된 아이템들을 붙여넣기합니다."""
        old_state = self.tree_widget.tree_state
        destination_item = self.tree_widget.currentItem()
        
        if destination_item and destination_item.logic.is_group():
            for selected_node_item in self.tree_widget.selected_node_items:
                row = [
                    selected_node_item.logic.parent_id,
                    selected_node_item.logic.name,
                    selected_node_item.logic.inp,
                    selected_node_item.logic.sub_con,
                    selected_node_item.logic.sub
                ]
                self.tree_widget.create_tree_item_with_id(destination_item, row)
        
        self.tree_widget.update_tree_state()
        new_state = self.tree_widget.tree_state
        self.tree_widget.undoStack.push(TreeUndoCommand(self.tree_widget, old_state, new_state))
        # 스냅샷 생성
        self.tree_widget.snapshot_manager.add_snapshot(new_state)

    def context_menu_event(self, event: QMouseEvent) -> None:
        """컨텍스트 메뉴 이벤트를 처리합니다.
        
        Args:
            event: 마우스 이벤트 객체
        """
        context_menu = QMenu(self.tree_widget)
        delete_action = QAction('Delete', self.tree_widget)
        ungroup_action = QAction('Ungroup', self.tree_widget)
        group_action = QAction('Group', self.tree_widget)
        
        delete_action.triggered.connect(lambda: self.tree_widget.recur_del(event))
        ungroup_action.triggered.connect(lambda: self.tree_widget.ungroup_sel_items(event))
        group_action.triggered.connect(lambda: self.tree_widget.group_sel_items(event))
        
        context_menu.addActions([delete_action, ungroup_action, group_action])
        context_menu.popup(QCursor.pos())

    @pyqtSlot(QTreeWidgetItem, int)
    def on_item_clicked(self, item: QTreeWidgetItem, column: int) -> None:
        """아이템 클릭 이벤트를 처리합니다.
        
        Args:
            item: 클릭된 트리 위젯 아이템
            column: 클릭된 열 번호
        """
        print(f"Item clicked: {item.text(0)}")  # 클릭된 아이템의 텍스트 출력