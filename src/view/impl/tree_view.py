import sys # resource_path를 위해 추가
from PyQt6.QtWidgets import QVBoxLayout, QWidget, QPushButton, QHBoxLayout, QSizePolicy, QMessageBox, QFileDialog
from PyQt6.QtGui import QIcon, QFontMetrics
from PyQt6.QtCore import Qt, QSize
from viewmodel.impl.tree_viewmodel import MTTreeViewModel
from view.impl.tree_widget import MTTreeWidget
from core.interfaces.base_item_data import MTNodeType, MTItemDTO
from model.events.interfaces.base_tree_event_mgr import MTTreeEvent
from typing import Any
import os
import random
import logging

logger = logging.getLogger(__name__)

# resource_path 함수 정의 시작
def resource_path(relative_path: str) -> str:
    """ Get absolute path to resource, works for dev and for PyInstaller """
    base_path = getattr(sys, "_MEIPASS", None)
    if base_path is None:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)
# resource_path 함수 정의 끝

class TreeView(QWidget):
    def __init__(self, viewmodel: MTTreeViewModel, parent=None):
        super().__init__(parent)
        self._viewmodel = viewmodel

        self._layout = QVBoxLayout(self)

        # 버튼을 위한 수평 레이아웃 (왼쪽 정렬)
        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(0, 0, 0, 0)
        # 버튼 사이 간격 설정 (예: 5px)
        button_layout.setSpacing(5)

        # 아이콘 경로를 resource_path로 처리
        add_icon_path = resource_path("src/images/icons/add.png")
        del_icon_path = resource_path("src/images/icons/del.png")

        add_icon = QIcon(add_icon_path)
        del_icon = QIcon(del_icon_path)

        # 버튼 생성 및 설정
        self.add_button = QPushButton("Add")
        self.add_button.setIcon(add_icon)
        if add_icon.isNull():
            self.add_button.setIconSize(self.add_button.iconSize())
        else:
            font = self.add_button.font()
            fm = QFontMetrics(font)
            text_height = fm.height()
            icon_dimension = max(8, text_height - 2)
            self.add_button.setIconSize(QSize(icon_dimension, icon_dimension))
        self.add_button.setStyleSheet("QPushButton { padding-left: 8px; padding-right: 5px; padding-top: 1px; padding-bottom: 1px; }")
        current_add_button_hint_height = self.add_button.sizeHint().height()
        target_min_button_height = int(current_add_button_hint_height * 1.1)
        self.add_button.setMinimumHeight(target_min_button_height)
        self.add_button.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        base_width_percentage = 0.25
        increased_width_percentage = base_width_percentage * 1.1
        base_fallback_width = 200
        increased_fallback_width = int(base_fallback_width * 1.1)
        self.add_button.setMaximumWidth(int(self.width() * increased_width_percentage) if self.width() > 0 else increased_fallback_width)
        self.add_button.clicked.connect(self.on_add_item)

        # Del 버튼
        self.del_button = QPushButton("Del")
        self.del_button.setIcon(del_icon)
        if del_icon.isNull():
            self.del_button.setIconSize(self.del_button.iconSize())
        else:
            del_font = self.del_button.font()
            del_fm = QFontMetrics(del_font)
            del_text_height = del_fm.height()
            del_icon_dimension = max(8, del_text_height - 2)
            self.del_button.setIconSize(QSize(del_icon_dimension, del_icon_dimension))
        self.del_button.setStyleSheet("QPushButton { padding-left: 8px; padding-right: 5px; padding-top: 1px; padding-bottom: 1px; }")
        self.del_button.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        self.del_button.setMinimumHeight(target_min_button_height) # Add 버튼 기준으로 계산된 최소 높이 적용
        # Del 버튼 최대 너비도 Add 버튼과 동일하게 설정
        self.del_button.setMaximumWidth(int(self.width() * increased_width_percentage) if self.width() > 0 else increased_fallback_width)

        self.del_button.clicked.connect(self.on_del_item)

        # Save/Load 버튼에 사용할 임시 아이콘 (Add/Del 아이콘 재사용)
        save_icon = add_icon
        load_icon = del_icon

        # Save 버튼
        self.save_button = QPushButton("Save")
        self.save_button.setIcon(save_icon)
        self.save_button.setIconSize(self.add_button.iconSize())
        self.save_button.setStyleSheet("QPushButton { padding-left: 8px; padding-right: 5px; padding-top: 1px; padding-bottom: 1px; }")
        self.save_button.setMinimumHeight(target_min_button_height)
        self.save_button.setMaximumWidth(int(self.width() * increased_width_percentage) if self.width() > 0 else increased_fallback_width)
        self.save_button.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        self.save_button.clicked.connect(self.on_save_clicked)

        # Load 버튼
        self.load_button = QPushButton("Load")
        self.load_button.setIcon(load_icon)
        self.load_button.setIconSize(self.del_button.iconSize())
        self.load_button.setStyleSheet("QPushButton { padding-left: 8px; padding-right: 5px; padding-top: 1px; padding-bottom: 1px; }")
        self.load_button.setMinimumHeight(target_min_button_height)
        self.load_button.setMaximumWidth(int(self.width() * increased_width_percentage) if self.width() > 0 else increased_fallback_width)
        self.load_button.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        self.load_button.clicked.connect(self.on_load_clicked)

        # 버튼을 레이아웃에 추가 (왼쪽 정렬을 위해 addStretch 사용)
        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.del_button)
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.load_button)
        button_layout.addStretch(1)

        # 버튼 레이아웃을 메인 레이아웃에 추가
        self._layout.addLayout(button_layout)

        self.tree_widget = MTTreeWidget(self._viewmodel)
        self._layout.addWidget(self.tree_widget)
        self.setLayout(self._layout)

        # ViewModel 시그널 연결
        self._viewmodel.item_added.connect(self.on_item_crud_slot)
        self._viewmodel.item_removed.connect(self.on_item_crud_slot)
        self._viewmodel.item_moved.connect(self.on_item_crud_slot)
        self._viewmodel.item_modified.connect(self.on_item_crud_slot)
        self._viewmodel.tree_reset.connect(self.on_item_crud_slot)
        self._viewmodel.tree_undo.connect(self.on_tree_undoredo_slot)
        self._viewmodel.tree_redo.connect(self.on_tree_undoredo_slot)

    """MTTreeWidget에서 현재 선택된 아이템의 ID를 반환합니다."""
    def get_selected_item_id(self):
        selected_items = self.tree_widget.selectedItems()
        if selected_items:
            # UserRole에 저장된 ID를 가져옵니다.
            return selected_items[0].data(0, Qt.ItemDataRole.UserRole)
        return None

    def resizeEvent(self, event):
        if self.add_button:
            # 창 크기 변경 시 버튼 최대 폭도 10% 증가된 값으로 조정
            base_width_percentage = 0.25
            increased_width_percentage = base_width_percentage * 1.1
            self.add_button.setMaximumWidth(int(self.width() * increased_width_percentage))
            # Del 버튼 너비도 동일하게 조정
            if hasattr(self, 'del_button') and self.del_button:
                self.del_button.setMaximumWidth(int(self.width() * increased_width_percentage))
                # Del 버튼 최소 높이도 resizeEvent에서 Add 버튼 기준으로 업데이트 (필요하다면)
                # self.del_button.setMinimumHeight(target_min_button_height) # target_min_button_height가 이 스코프에 있어야 함

            # 높이도 sizeHint 기반으로 resizeEvent에서 업데이트 필요시 여기에 추가 (보통은 __init__에서 충분)
            # current_hint_height = self.add_button.sizeHint().height()
            # self.add_button.setMinimumHeight(int(current_hint_height * 1.1))
        super().resizeEvent(event)

    # --- UI 이벤트 핸들러 ---
    def on_add_item(self):
        selected_item_id = self.get_selected_item_id()
        item_name = f"New Item {random.randint(100, 999)}"
        item_type = MTNodeType.INSTRUCTION
        new_item_id = self._viewmodel.add_item(name=item_name, 
                                               new_item_node_type=item_type,
                                               selected_potential_parent_id=selected_item_id)

    def on_del_item(self):
        selected_item_id = self.get_selected_item_id()
        if selected_item_id:
            self._viewmodel.remove_item(selected_item_id)

    def on_save_clicked(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "트리 저장", "", "JSON 파일 (*.json);;모든 파일 (*.*)")
        if file_path:
            try:
                # ViewModel에 save_tree(file_path) 메서드가 있다고 가정
                if hasattr(self._viewmodel, 'save_tree'):
                    success = self._viewmodel.save_tree(file_path)
                    if not success:
                        QMessageBox.critical(self, "저장 실패", "파일을 저장할 수 없습니다.")
                else:
                    QMessageBox.critical(self, "오류", "ViewModel에 save_tree 메서드가 없습니다.")
            except Exception as e:
                QMessageBox.critical(self, "저장 오류", f"저장 중 오류 발생: {e}")

    def on_load_clicked(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "트리 불러오기", "", "JSON 파일 (*.json);;모든 파일 (*.*)")
        if file_path:
            try:
                # ViewModel에 load_tree(file_path) 메서드가 있다고 가정
                if hasattr(self._viewmodel, 'load_tree'):
                    success = self._viewmodel.load_tree(file_path)
                    if not success:
                        QMessageBox.critical(self, "불러오기 실패", "파일을 불러올 수 없습니다.")
                    else:
                        self.tree_widget.update_tree_items()
                else:
                    QMessageBox.critical(self, "오류", "ViewModel에 load_tree 메서드가 없습니다.")
            except Exception as e:
                QMessageBox.critical(self, "불러오기 오류", f"불러오기 중 오류 발생: {e}")

    # --- ViewModel 시그널 슬롯 ---
    def on_tree_undoredo_slot(self, event_type: MTTreeEvent, data: dict[str, Any]):
        logger.debug(f"Undo/Redo Slot triggered: {event_type}, data keys: {data.keys() if isinstance(data, dict) else 'Not a dict'}")
        self.tree_widget.update_tree_items(data)

    def on_item_crud_slot(self, event_type: MTTreeEvent, data: dict[str, Any]):
        logger.debug(f"Item CRUD Slot triggered: {event_type}, data: {data}")
        if event_type == MTTreeEvent.ITEM_ADDED:
            item_id = data.get('item_id')
            parent_id = data.get('parent_id')
            if item_id:
                item_dto = self._viewmodel.get_item_dto(item_id)
                if item_dto:
                    self.tree_widget.handle_item_added(item_dto, parent_id)
                else:
                    self.tree_widget.update_tree_items()
            else:
                self.tree_widget.update_tree_items()
        elif event_type == MTTreeEvent.ITEM_REMOVED:
            item_id = data.get('item_id')
            if item_id:
                self.tree_widget.handle_item_removed(item_id)
            else:
                self.tree_widget.update_tree_items()
        elif event_type == MTTreeEvent.ITEM_MOVED:
            self.tree_widget.update_tree_items()
        elif event_type == MTTreeEvent.ITEM_MODIFIED:
            item_id = data.get('item_id')
            item_dto_dict = data.get('changes')
            if item_id and isinstance(item_dto_dict, dict):
                item_dto = MTItemDTO.from_dict(item_dto_dict)
                self.tree_widget.handle_item_modified(item_id, item_dto)
            else:
                self.tree_widget.update_tree_items()
        elif event_type == MTTreeEvent.TREE_CRUD:
            logger.debug(f"Handling TREE_CRUD event by updating all tree items.")
            self.tree_widget.update_tree_items(data)
        elif event_type == MTTreeEvent.TREE_RESET:
            self.tree_widget.update_tree_items()

    def set_viewmodel(self, viewmodel):
        self._viewmodel = viewmodel
        self.tree_widget.set_viewmodel(viewmodel)