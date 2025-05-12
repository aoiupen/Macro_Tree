from PyQt6.QtWidgets import QTreeWidget, QTreeWidgetItem, QAbstractItemView
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon
from core.interfaces.base_item_data import MTNodeType
import os
from viewmodel.impl.tree_viewmodel import MTTreeViewModel

class MTTreeWidget(QTreeWidget):
    def __init__(self, viewmodel: MTTreeViewModel, parent=None):
        super().__init__(parent)
        self._viewmodel = viewmodel
        self.setHeaderLabel("Macro Tree")
        self.itemClicked.connect(self.item_clicked)
        self.itemExpanded.connect(self._on_item_expanded)
        self.itemCollapsed.connect(self._on_item_collapsed)
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.setDropIndicatorShown(True)
        self.setDragDropMode(QAbstractItemView.DragDropMode.InternalMove)
        self.update_tree_items()

    def update_tree_items(self):
        selected_ids = self._viewmodel.get_selected_items()
        self.clear()
        self._id_to_widget_map = {}
        self._build_tree_items()
        self._apply_tree_state()

    def _build_tree_items(self):
        all_items = self._viewmodel.get_tree_items()
        def add_children(parent_id, parent_widget):
            for item_id, item in all_items.items():
                if item.get_property("parent_id") == parent_id:
                    self._add_tree_item(item, parent_widget)
                    add_children(item.id, self._id_to_widget_map[item.id])
        for item_id, item in all_items.items():
            if not item.get_property("parent_id"):
                self._add_tree_item(item, self)
                add_children(item.id, self._id_to_widget_map[item.id])

    def _apply_tree_state(self):
        for item_id, widget_item in self._id_to_widget_map.items():
            item = self._viewmodel.get_item(item_id)
            if item:
                if item.get_property("expanded", False):
                    self.expandItem(widget_item)
                if item_id in self._viewmodel.get_selected_items():
                    widget_item.setSelected(True)

    def _add_tree_item(self, item, parent_widget):
        widget_item = QTreeWidgetItem(parent_widget, [item.get_property("name", item.id)])
        widget_item.setData(0, Qt.ItemDataRole.UserRole, item.id)
        node_type = item.get_property("node_type", None)
        icon_path = None
        if node_type is not None:
            if str(node_type) == "MTNodeType.GROUP" or str(node_type) == "group":
                icon_path = os.path.join("images", "icons", "group.png")
            elif str(node_type) == "MTNodeType.INSTRUCTION" or str(node_type) == "instruction":
                icon_path = os.path.join("images", "icons", "inst.png")
        if icon_path and os.path.exists(icon_path):
            widget_item.setIcon(0, QIcon(icon_path))
        self._id_to_widget_map[item.id] = widget_item

    def item_clicked(self, item, column):
        item_id = item.data(0, Qt.ItemDataRole.UserRole)
        self._viewmodel.select_item(item_id)

    def _on_item_expanded(self, item):
        item_id = item.data(0, Qt.ItemDataRole.UserRole)
        self._viewmodel.toggle_expanded(item_id, True)

    def _on_item_collapsed(self, item):
        item_id = item.data(0, Qt.ItemDataRole.UserRole)
        self._viewmodel.toggle_expanded(item_id, False)

    def dropEvent(self, event):
        drop_indicator = self.dropIndicatorPosition()
        target_item = self.itemAt(event.position().toPoint())
        dragged_item = self.currentItem()
        if not dragged_item or not target_item:
            event.ignore()
            return
        dragged_id = dragged_item.data(0, Qt.ItemDataRole.UserRole)
        target_id = target_item.data(0, Qt.ItemDataRole.UserRole)
        if dragged_id == target_id:
            event.ignore()
            return
        if drop_indicator == QTreeWidget.DropIndicatorPosition.OnItem:
            target_item_obj = self._viewmodel.get_item(target_id)
            if target_item_obj is None:
                event.ignore()
                print("target_item_obj is None")
                return
            target_node_type = target_item_obj.get_property("node_type")
            if target_node_type == MTNodeType.GROUP:
                self._viewmodel.move_item(dragged_id, target_id)
            else:
                event.ignore()
                print("target의 node_type이 group이 아님: 이동 불가")
                return
        elif drop_indicator == QTreeWidget.DropIndicatorPosition.AboveItem or drop_indicator == QTreeWidget.DropIndicatorPosition.BelowItem:
            target_item_obj = self._viewmodel.get_item(target_id)
            if target_item_obj is None:
                event.ignore()
                return
            target_parent_id = target_item_obj.get_property("parent_id")
            self._viewmodel.move_item(dragged_id, target_parent_id)
        else:
            self._viewmodel.move_item(dragged_id, None)
        self.update_tree_items()
        event.accept()

    def mousePressEvent(self, event):
        item = self.itemAt(event.position().toPoint())
        if item is not None:
            item_id = item.data(0, Qt.ItemDataRole.UserRole)
            # 항상 단일 선택 모드로 ViewModel에 반영
            self._viewmodel.select_item(item_id, multi_select=False)
        super().mousePressEvent(event)

    def startDrag(self, supportedActions):
        # 드래그 시작 시 선택 상태를 클리어
        self._viewmodel._view._selected_items.clear()
        self._viewmodel._view._notify_change()
        super().startDrag(supportedActions)