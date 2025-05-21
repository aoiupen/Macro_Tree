import sys
from PyQt6.QtWidgets import QTreeWidget, QTreeWidgetItem, QAbstractItemView
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon
from core.interfaces.base_item_keys import DomainKeys as DK, UIStateKeys as UK
from core.interfaces.base_item_data import MTNodeType, MTItemDTO
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
        self.itemClicked.connect(self.on_qtree_item_clicked)
        self.itemExpanded.connect(self.on_qtree_item_expanded)
        self.itemCollapsed.connect(self.on_qtree_item_collapsed)
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.setDropIndicatorShown(True)
        self.setDragDropMode(QAbstractItemView.DragDropMode.InternalMove)
        self._id_to_widget_map = {}

        self.update_tree_items()

    def update_tree_items(self, tree_snapshot_data: dict | None = None):
        self.clear()
        self._id_to_widget_map.clear()
        
        root_items_dtos = self._viewmodel.get_item_children(None)
        
        for item_dto in root_items_dtos:
            self._add_tree_item_recursive(item_dto, self.invisibleRootItem())

    def _add_tree_item_recursive(self, item_dto: MTItemDTO, parent_q_widget: QTreeWidgetItem | QTreeWidget):
        widget_item = QTreeWidgetItem(parent_q_widget, [item_dto.domain_data.name])
        widget_item.setData(0, Qt.ItemDataRole.UserRole, item_dto.id)
        self._id_to_widget_map[item_dto.id] = widget_item

        node_type = item_dto.domain_data.node_type
        icon_path = None
        if node_type == MTNodeType.GROUP:
            icon_path = resource_path("src/images/icons/group.png")
        elif node_type == MTNodeType.INSTRUCTION:
            icon_path = resource_path("src/images/icons/inst.png")
        
        if icon_path and os.path.exists(icon_path):
            widget_item.setIcon(0, QIcon(icon_path))
        elif icon_path:
            logger.warning(f"Icon file not found at {icon_path} for item {item_dto.id}")

        widget_item.setExpanded(item_dto.ui_state_data.is_expanded)
        if item_dto.ui_state_data.is_selected:
            widget_item.setSelected(True)

        children_dtos = self._viewmodel.get_item_children(item_dto.id)
        for child_dto in children_dtos:
            self._add_tree_item_recursive(child_dto, widget_item)

    def handle_item_added(self, item: MTItemDTO, parent_id: str | None):
        parent_q_widget: QTreeWidgetItem | QTreeWidget | None = None
        if parent_id is None or parent_id == self._viewmodel.get_dummy_root_id():
            parent_q_widget = self.invisibleRootItem()
        else:
            parent_q_widget = self._id_to_widget_map.get(parent_id)

        if parent_q_widget is None:
            logger.warning(f"Parent widget not found for {parent_id}, cannot add {item.id}. Triggering full update.")
            self.update_tree_items()
            return

        if item.id in self._id_to_widget_map:
            logger.warning(f"Item DTO {item.id} already in widget map. Skipping add.")
            return
        
        widget_item = QTreeWidgetItem(parent_q_widget, [item.domain_data.name])
        widget_item.setData(0, Qt.ItemDataRole.UserRole, item.id)
        self._id_to_widget_map[item.id] = widget_item

        node_type = item.domain_data.node_type
        icon_path = None
        if node_type == MTNodeType.GROUP:
            icon_path = resource_path("src/images/icons/group.png")
        elif node_type == MTNodeType.INSTRUCTION:
            icon_path = resource_path("src/images/icons/inst.png")
        
        if icon_path and os.path.exists(icon_path):
            widget_item.setIcon(0, QIcon(icon_path))
        elif icon_path:
            logger.warning(f"Icon file not found at {icon_path} for item {item.id}")

        widget_item.setExpanded(item.ui_state_data.is_expanded)
        if item.ui_state_data.is_selected:
            widget_item.setSelected(True)

    def handle_item_removed(self, item_id: str):
        widget_item = self._id_to_widget_map.pop(item_id, None)
        if widget_item:
            parent_widget = widget_item.parent()
            if parent_widget:
                parent_widget.removeChild(widget_item)
            else:
                index = self.indexOfTopLevelItem(widget_item)
                if index != -1:
                    self.takeTopLevelItem(index)

    def handle_item_modified(self, item_id: str, item: MTItemDTO):
        widget_item = self._id_to_widget_map.get(item_id)
        if widget_item:
            widget_item.setText(0, item.domain_data.name)
            node_type = item.domain_data.node_type
            icon_path = None
            if node_type == MTNodeType.GROUP:
                icon_path = resource_path("src/images/icons/group.png")
            elif node_type == MTNodeType.INSTRUCTION:
                icon_path = resource_path("src/images/icons/inst.png")
            if icon_path and os.path.exists(icon_path):
                widget_item.setIcon(0, QIcon(icon_path))
            elif icon_path: logger.warning(f"Icon file not found {icon_path}")
            else: widget_item.setIcon(0, QIcon())

            widget_item.setExpanded(item.ui_state_data.is_expanded)
            widget_item.setSelected(item.ui_state_data.is_selected)

    def on_qtree_item_clicked(self, item: QTreeWidgetItem, column: int):
        item_id = item.data(0, Qt.ItemDataRole.UserRole)
        if item_id:
            self._viewmodel.select_item(item_id)

    def on_qtree_item_expanded(self, item: QTreeWidgetItem):
        item_id = item.data(0, Qt.ItemDataRole.UserRole)
        if item_id:
            self._viewmodel.toggle_expanded_state(item_id, True)

    def on_qtree_item_collapsed(self, item: QTreeWidgetItem):
        item_id = item.data(0, Qt.ItemDataRole.UserRole)
        if item_id:
            self._viewmodel.toggle_expanded_state(item_id, False)

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

    def handle_item_moved(self, item_id, new_parent_id, old_parent_id):
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

    def set_viewmodel(self, viewmodel):
        self._viewmodel = viewmodel
        self.update_tree_items()
    