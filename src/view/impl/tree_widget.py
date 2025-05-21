import sys
from PyQt6.QtWidgets import QTreeWidget, QTreeWidgetItem, QAbstractItemView
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon
from core.interfaces.base_item_keys import DomainKeys as DK, UIStateKeys as UK
from core.interfaces.base_item_data import MTNodeType
import os
from viewmodel.impl.tree_viewmodel import MTTreeViewModel
import logging                                                                                              

logger = logging.getLogger(__name__)

def resource_path(relative_path: str) -> str:
    """ Get absolute path to resource, works for dev and for PyInstaller """
    base_path = getattr(sys, "_MEIPASS", None)
    if base_path is None:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

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
        self.clear()
        self._id_to_widget_map = {}
        self._build_tree_items()
        self._apply_tree_state()

    def _build_tree_items(self):
        dummy_root_id = self._viewmodel.get_dummy_root_id()
        all_items = self._viewmodel.get_tree_items()
        def add_children_to_widget(parent_item_id_in_model, parent_qwidget_item):
            for item_id, item_model in all_items.items():
                if item_model.get_property(DK.PARENT_ID) == parent_item_id_in_model:
                    self._add_tree_item(item_model, parent_qwidget_item)
                    new_qwidget_item = self._id_to_widget_map.get(item_id)
                    if new_qwidget_item:
                        add_children_to_widget(item_id, new_qwidget_item)
        if dummy_root_id:
            for item_id, item_model in all_items.items():
                if item_model.get_property(DK.PARENT_ID) == dummy_root_id:
                    self._add_tree_item(item_model, self)
                    top_level_qwidget_item = self._id_to_widget_map.get(item_id)
                    if top_level_qwidget_item:
                        add_children_to_widget(item_id, top_level_qwidget_item)
        else:
            logger.warning("Dummy root ID not found. Tree might not be built correctly.")
        print("build", self._id_to_widget_map)
    def _apply_tree_state(self):
        for item_id, widget_item in self._id_to_widget_map.items():
            item = self._viewmodel.get_item(item_id)
            if item:
                if item.get_property(UK.EXPANDED, False):
                    self.expandItem(widget_item)
                if item_id in self._viewmodel.get_selected_items():
                    widget_item.setSelected(True)
        print("apply", self._id_to_widget_map)
    def _add_tree_item(self, item, parent_widget):
        widget_item = QTreeWidgetItem(parent_widget, [item.get_property(DK.NAME, item.id)])
        widget_item.setData(0, Qt.ItemDataRole.UserRole, item.id)
        node_type = item.get_property(DK.NODE_TYPE, None)
        icon_path = None

        # Define project_root relative to this file's location
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))

        if node_type is not None:
            if node_type == MTNodeType.GROUP:
                icon_path = resource_path("src/images/icons/group.png")
            elif node_type == MTNodeType.INSTRUCTION:
                icon_path = resource_path("src/images/icons/inst.png")

        if icon_path and os.path.exists(icon_path):
            widget_item.setIcon(0, QIcon(icon_path))
        elif icon_path:
            print(f"Warning: Icon file not found at {icon_path}")

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
                print(f"DropEvent: Requesting move {dragged_id} onto {target_id}")
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
            print(f"DropEvent: Requesting move {dragged_id} near {target_id} (parent: {target_parent_id})")
            self._viewmodel.move_item(dragged_id, target_parent_id)
        else:
            print(f"DropEvent: Requesting move {dragged_id} to root (None)")
            self._viewmodel.move_item(dragged_id, None)
        event.ignore()

    def handle_item_added(self, item_data, parent_id):
        """새 아이템 추가를 처리합니다."""
        parent_widget = None
        if parent_id == self._viewmodel.get_dummy_root_id() or parent_id is None:
            parent_widget = self.invisibleRootItem()
        elif parent_id:
            parent_widget = self._id_to_widget_map.get(parent_id)
            if parent_widget is None:
                print(f"Warning: Parent widget not found for {parent_id}, cannot add {item_data.id}. Triggering full update.")
                self.update_tree_items()
                return

        self._add_tree_item(item_data, parent_widget)
        new_widget_item = self._id_to_widget_map.get(item_data.id)
        if new_widget_item and item_data.get_property(UK.EXPANDED, False):
            self.expandItem(new_widget_item)
        if new_widget_item and item_data.id in self._viewmodel.get_selected_items():
             new_widget_item.setSelected(True)

    def handle_item_removed(self, item_id):
        """아이템 제거를 처리합니다."""
        widget_item = self._id_to_widget_map.pop(item_id, None)
        if widget_item:
            parent_widget = widget_item.parent()
            if parent_widget:
                parent_widget.removeChild(widget_item)
            else:
                index = self.indexOfTopLevelItem(widget_item)
                if index != -1:
                    self.takeTopLevelItem(index)

    def handle_item_modified(self, item_id, changes):
        """아이템 수정을 처리합니다."""
        widget_item = self._id_to_widget_map.get(item_id)
        if widget_item:
            if 'name' in changes:
                widget_item.setText(0, changes['name'])
            if 'node_type' in changes:
                node_type = changes['node_type']
                icon_path = None
                project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
                if node_type == MTNodeType.GROUP:
                    icon_path = os.path.join(project_root, "src", "images", "icons", "group.png")
                elif node_type == MTNodeType.INSTRUCTION:
                    icon_path = os.path.join(project_root, "src", "images", "icons", "inst.png")

                if icon_path and os.path.exists(icon_path):
                     widget_item.setIcon(0, QIcon(icon_path))
                elif icon_path:
                     print(f"Warning: Icon file not found at (handle_item_modified) {icon_path}")
                     widget_item.setIcon(0, QIcon()) # Fallback to no icon
                else:
                     widget_item.setIcon(0, QIcon()) # Fallback to no icon

    def handle_item_moved(self, item_id, new_parent_id, old_parent_id):
        """아이템 이동을 처리합니다."""
        widget_item_popped = self._id_to_widget_map.pop(item_id, None) 

        if not widget_item_popped:
            self.update_tree_items()
            return

        old_q_parent_widget = widget_item_popped.parent()
        taken_item_from_ui = None
        if old_q_parent_widget:
            index_in_old_parent = old_q_parent_widget.indexOfChild(widget_item_popped)
            if index_in_old_parent != -1:
                taken_item_from_ui = old_q_parent_widget.takeChild(index_in_old_parent)
        else:
            index_in_toplevel = self.indexOfTopLevelItem(widget_item_popped)
            if index_in_toplevel != -1:
                taken_item_from_ui = self.takeTopLevelItem(index_in_toplevel)

        if taken_item_from_ui is None:
             self.update_tree_items()
             return
        
        new_q_parent_widget_target = None
        is_new_parent_invisible_root = False
        if new_parent_id == self._viewmodel.get_dummy_root_id() or new_parent_id is None:
            new_q_parent_widget_target = self.invisibleRootItem()
            is_new_parent_invisible_root = True
        elif new_parent_id:
            new_q_parent_widget_target = self._id_to_widget_map.get(new_parent_id)
        
        if new_q_parent_widget_target is None and not is_new_parent_invisible_root:
            self.update_tree_items() 
            return

        if is_new_parent_invisible_root:
            self.addTopLevelItem(taken_item_from_ui)
        elif new_q_parent_widget_target:
            new_q_parent_widget_target.addChild(taken_item_from_ui)
        else:
            self.update_tree_items()
            return
        
        current_ui_parent = taken_item_from_ui.parent()

        self._id_to_widget_map[item_id] = taken_item_from_ui 

        if item_data_from_model := self._viewmodel.get_item(item_id):
            if item_data_from_model.get_property(UK.EXPANDED, False):
                self.expandItem(taken_item_from_ui)
            else:
                self.collapseItem(taken_item_from_ui)
            
            if item_id in self._viewmodel.get_selected_items():
                taken_item_from_ui.setSelected(True)
            else:
                taken_item_from_ui.setSelected(False)
    