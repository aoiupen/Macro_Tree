from PyQt6.QtWidgets import QTreeWidget, QTreeWidgetItem, QAbstractItemView
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon
from core.interfaces.base_item_data import MTNodeType
import os
from viewmodel.impl.tree_viewmodel import MTTreeViewModel
from PyQt6.QtCore import pyqtSlot
import logging

logger = logging.getLogger(__name__)

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

        # 프로젝트 루트 경로 계산 (TreeView와 유사하게)
        # 이 파일 위치(view/impl)에서 두 단계 위로 이동
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

        if node_type is not None:
            # Enum 타입 직접 비교로 변경
            if node_type == MTNodeType.GROUP:
                # 프로젝트 루트 기준 절대 경로 사용
                icon_path = os.path.join(project_root, "images", "icons", "group.png")
            elif node_type == MTNodeType.INSTRUCTION:
                # 프로젝트 루트 기준 절대 경로 사용
                icon_path = os.path.join(project_root, "images", "icons", "inst.png")

        # os.path.exists 호출은 디스크 접근을 유발함.
        # 만약 아이콘 경로가 항상 유효하다면 (예: 리소스 시스템 사용 또는 빌드 시 검증)
        # 이 부분을 제거하여 성능을 약간 향상시킬 수 있음.
        if icon_path and os.path.exists(icon_path):
            widget_item.setIcon(0, QIcon(icon_path))
        elif icon_path:
            print(f"Warning: Icon file not found at {icon_path}") # 경로가 생성되었으나 파일이 없을 때 경고

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
        event.accept()

    def mousePressEvent(self, event):
        item = self.itemAt(event.position().toPoint())
        if item is not None:
            item_id = item.data(0, Qt.ItemDataRole.UserRole)
            # 항상 단일 선택 모드로 ViewModel에 반영
            self._viewmodel.select_item(item_id, multi_select=False)
        super().mousePressEvent(event)

    def startDrag(self, supportedActions):
        # 드래그 시작 시 ViewModel을 통해 선택 상태 클리어 요청 (캡슐화)
        print("Requesting clear selection before drag...")
        self._viewmodel.clear_selection_state()
        super().startDrag(supportedActions)

    def handle_item_added(self, item_data, parent_id):
        """새 아이템 추가를 처리합니다."""
        parent_widget = None
        if parent_id:
            parent_widget = self._id_to_widget_map.get(parent_id)
            if parent_widget is None:
                print(f"Warning: Parent widget not found for {parent_id}, cannot add {item_data.id}. Triggering full update.")
                self.update_tree_items()
                return
        else:
            # parent_id가 None이면 최상위 아이템으로 추가
            parent_widget = self.invisibleRootItem() # QTreeWidget 자체 또는 가상 루트 사용

        # 새 QTreeWidgetItem 생성 및 추가 (기존 _add_tree_item 로직 재활용)
        # 주의: _add_tree_item은 이미 _id_to_widget_map에 추가하므로 여기서 직접 추가 불필요
        self._add_tree_item(item_data, parent_widget)
        print(f"Widget: Item {item_data.id} added under parent {parent_id}")
        # 필요시 새로 추가된 아이템 확장/선택 상태 적용
        new_widget_item = self._id_to_widget_map.get(item_data.id)
        if new_widget_item and item_data.get_property("expanded", False):
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
                print(f"Widget: Item {item_id} removed from parent {parent_widget.data(0, Qt.ItemDataRole.UserRole)}")
            else:
                # 최상위 아이템 제거
                index = self.indexOfTopLevelItem(widget_item)
                if index != -1:
                    self.takeTopLevelItem(index)
                    print(f"Widget: Top level item {item_id} removed")
        else:
             print(f"Warning: Widget item not found for {item_id} during removal.")
             # 필요시 전체 업데이트 self.update_tree_items()

    def handle_item_modified(self, item_id, changes):
        """아이템 수정을 처리합니다."""
        widget_item = self._id_to_widget_map.get(item_id)
        if widget_item:
            print(f"Widget: Modifying item {item_id} with changes: {changes}")
            if 'name' in changes:
                widget_item.setText(0, changes['name'])
            if 'node_type' in changes:
                # 아이콘 업데이트 로직 (기존 _add_tree_item의 아이콘 설정 부분 참고)
                node_type = changes['node_type']
                icon_path = None
                project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
                if node_type == MTNodeType.GROUP:
                    icon_path = os.path.join(project_root, "images", "icons", "group.png")
                elif node_type == MTNodeType.INSTRUCTION:
                    icon_path = os.path.join(project_root, "images", "icons", "inst.png")
                if icon_path and os.path.exists(icon_path):
                     widget_item.setIcon(0, QIcon(icon_path))
                elif icon_path:
                     print(f"Warning: Icon file not found for modified item {item_id} at {icon_path}")
                     widget_item.setIcon(0, QIcon()) # 아이콘 제거 또는 기본 아이콘
                else:
                     widget_item.setIcon(0, QIcon())
            # 필요시 다른 속성(툴팁 등) 업데이트 로직 추가
        else:
            print(f"Warning: Widget item not found for {item_id} during modification.")
            # 필요시 전체 업데이트 self.update_tree_items()

    def handle_item_moved(self, item_id, new_parent_id, old_parent_id):
        """아이템 이동을 처리합니다."""
        widget_item = self._id_to_widget_map.get(item_id)
        if not widget_item:
            print(f"Warning: Widget item not found for {item_id} during move.")
            self.update_tree_items() # 이동할 아이템 없으면 전체 업데이트
            return

        # 1. 기존 부모에서 제거 (UI 상에서만)
        old_parent_widget = widget_item.parent()
        taken_item = None
        if old_parent_widget:
            print(f"Widget: Taking item {item_id} from old parent {old_parent_widget.data(0, Qt.ItemDataRole.UserRole)}")
            taken_item = old_parent_widget.takeChild(old_parent_widget.indexOfChild(widget_item))
        else:
            index = self.indexOfTopLevelItem(widget_item)
            if index != -1:
                print(f"Widget: Taking top level item {item_id}")
                taken_item = self.takeTopLevelItem(index)

        if taken_item is None:
             print(f"Error: Failed to take item {item_id} from its old position.")
             # 원래 위치로 돌려놓거나 전체 업데이트 등 복구 로직 필요할 수 있음
             self.update_tree_items()
             return

        # 2. 새 부모에 추가
        new_parent_widget = None
        if new_parent_id:
            new_parent_widget = self._id_to_widget_map.get(new_parent_id)
            if new_parent_widget is None:
                print(f"Warning: New parent widget not found for {new_parent_id}, cannot move {item_id}. Triggering full update.")
                # 아이템을 원래 위치로 돌려놓는 로직 추가 필요할 수 있음
                self.update_tree_items()
                return
            print(f"Widget: Adding item {item_id} to new parent {new_parent_id}")
            new_parent_widget.addChild(taken_item)
        else:
            # 최상위로 이동
            print(f"Widget: Adding item {item_id} as top level item")
            self.addTopLevelItem(taken_item)

        # 이동 후 상태 업데이트 (필요시 확장 등)
        if item_data := self._viewmodel.get_item(item_id):
            if item_data.get_property("expanded", False):
                self.expandItem(widget_item)

    @pyqtSlot(str, int, str, MTNodeType)
    def update_ui_for_added_item(self, parent_id: str, index: int, new_id: str, new_type: MTNodeType):
        """ViewModel의 item_added 시그널을 처리하여 트리에 아이템을 추가합니다."""
        parent_item = self._find_item_by_id(parent_id)
        if parent_item is None:
            # 부모가 루트이거나 찾을 수 없는 경우 (오류 또는 초기 상태)
            parent_item = self.invisibleRootItem()
            if parent_id != "root": # 루트가 아닌데 못찾으면 경고
                 logger.warning(f"Parent item '{parent_id}' not found for adding '{new_id}'. Adding to root.")

        # 모델에서 새 아이템 정보 가져오기 (이름 등)
        item_data = self._viewmodel.get_item_data(new_id)
        if not item_data:
             logger.error(f"Could not retrieve data for newly added item '{new_id}'. Cannot add to tree.")
             return

        new_widget_item = QTreeWidgetItem([item_data.get('name', 'Unnamed')])
        new_widget_item.setData(0, Qt.ItemDataRole.UserRole, new_id) # UserRole에 ID 저장
        # 아이콘 설정 등 추가 속성 설정 가능
        self._set_icon_based_on_type(new_widget_item, new_type)

        parent_item.insertChild(index, new_widget_item)
        self._item_map[new_id] = new_widget_item
        logger.debug(f"UI: Added item '{new_id}' under '{parent_id}' at index {index}")

    @pyqtSlot(str, str, int)
    def update_ui_for_moved_item(self, source_id: str, target_parent_id: str, target_index: int):
        """ViewModel의 item_moved 시그널을 처리하여 트리에서 아이템을 이동합니다."""
        source_item = self._find_item_by_id(source_id)
        if not source_item:
            logger.error(f"Source item '{source_id}' not found for move.")
            return

        # 현재 부모로부터 제거
        current_parent = source_item.parent() or self.invisibleRootItem()
        taken_item = current_parent.takeChild(current_parent.indexOfChild(source_item))

        if taken_item: # takeChild가 성공적으로 아이템을 반환했을 때만 진행
            # 새 부모 찾기
            new_parent_item = self._find_item_by_id(target_parent_id)
            if new_parent_item is None:
                 new_parent_item = self.invisibleRootItem()
                 if target_parent_id != "root":
                     logger.warning(f"Target parent item '{target_parent_id}' not found for moving '{source_id}'. Moving to root.")

            # 새 부모에 삽입
            new_parent_item.insertChild(target_index, taken_item)
            logger.debug(f"UI: Moved item '{source_id}' to parent '{target_parent_id}' at index {target_index}")
        else:
             logger.error(f"Failed to take item '{source_id}' from its parent during move.")


    @pyqtSlot(str)
    def update_ui_for_removed_item(self, item_id: str):
        """ViewModel의 item_removed 시그널을 처리하여 트리에서 아이템을 제거합니다."""
        item_to_remove = self._find_item_by_id(item_id)
        if item_to_remove:
            parent = item_to_remove.parent() or self.invisibleRootItem()
            parent.removeChild(item_to_remove)
            if item_id in self._item_map: # Check if key exists before deleting
                del self._item_map[item_id] # 맵에서도 제거
            logger.debug(f"UI: Removed item '{item_id}'")
        else:
            logger.warning(f"Attempted to remove item '{item_id}', but it was not found in the tree.")


    @pyqtSlot(str, str)
    def update_ui_for_renamed_item(self, item_id: str, new_name: str):
        """ViewModel의 item_renamed 시그널을 처리하여 트리 아이템의 이름을 변경합니다."""
        item_to_rename = self._find_item_by_id(item_id)
        if item_to_rename:
            item_to_rename.setText(0, new_name)
            logger.debug(f"UI: Renamed item '{item_id}' to '{new_name}'")
        else:
            logger.warning(f"Attempted to rename item '{item_id}', but it was not found in the tree.")