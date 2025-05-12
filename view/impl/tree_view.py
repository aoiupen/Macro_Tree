from PyQt6.QtWidgets import QVBoxLayout, QWidget, QPushButton, QHBoxLayout, QSizePolicy
from PyQt6.QtGui import QIcon, QPixmap, QFontMetrics
from PyQt6.QtCore import Qt, QSize
from viewmodel.impl.tree_viewmodel import MTTreeViewModel
from view.impl.tree_widget import MTTreeWidget
from core.interfaces.base_item_data import MTNodeType
import os

class TreeView(QWidget):
    def __init__(self, viewmodel: MTTreeViewModel, parent=None):
        super().__init__(parent)
        self._viewmodel = viewmodel

        self.layout = QVBoxLayout(self)

        # 버튼을 위한 수평 레이아웃 (왼쪽 정렬)
        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(0, 0, 0, 0)
        # 버튼 사이 간격 설정 (예: 5px)
        button_layout.setSpacing(5)

        # 아이콘 경로 - 프로젝트 루트 아래 images 폴더 기준
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")) # view/impl 에서 두 단계 위
        icon_path = os.path.join(project_root, "images/icons", "add.png") # images 폴더 안의 add.png

        if not os.path.exists(icon_path):
            print(f"Warning: Icon file not found at {icon_path}.")
            icon = QIcon() # 최종적으로 못 찾으면 빈 아이콘
        else:
            icon = QIcon(icon_path) # images 폴더 기준 경로 사용

        # 버튼 생성 및 설정
        self.add_button = QPushButton("Add")
        self.add_button.setIcon(icon)
        if icon.isNull():
             self.add_button.setIconSize(self.add_button.iconSize()) # 기본 아이콘 크기 유지
        else:
             # 아이콘 크기를 버튼 텍스트 높이에 맞춤
             font = self.add_button.font()
             fm = QFontMetrics(font)
             text_height = fm.height()
             # 아이콘이 텍스트 높이에 적절히 보이도록 크기 조정 (예: 텍스트 높이보다 2px 작게)
             icon_dimension = max(8, text_height - 2)  # 최소 크기 8px 보장
             self.add_button.setIconSize(QSize(icon_dimension, icon_dimension))

        # 아이콘 왼쪽에 약간의 여백 추가 (버튼 내용 전체가 오른쪽으로 이동)
        self.add_button.setStyleSheet("QPushButton { padding-left: 8px; padding-right: 5px; padding-top: 1px; padding-bottom: 1px; }")

        # 버튼의 최소 높이를 현재 sizeHint보다 10% 크게 설정
        current_add_button_hint_height = self.add_button.sizeHint().height()
        target_min_button_height = int(current_add_button_hint_height * 1.1)
        self.add_button.setMinimumHeight(target_min_button_height)

        self.add_button.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        # 버튼의 최대 너비를 기존보다 10% 크게 설정
        base_width_percentage = 0.25
        increased_width_percentage = base_width_percentage * 1.1
        base_fallback_width = 200
        increased_fallback_width = int(base_fallback_width * 1.1)

        self.add_button.setMaximumWidth(int(self.width() * increased_width_percentage) if self.width() > 0 else increased_fallback_width)
        self.add_button.clicked.connect(self.on_add_item)

        # --- Del 버튼 아이콘 경로 및 설정 --- #
        del_icon_path = os.path.join(project_root, "images/icons", "del.png")
        if not os.path.exists(del_icon_path):
            print(f"Warning: Icon file not found at {del_icon_path}.")
            del_icon = QIcon()
        else:
            del_icon = QIcon(del_icon_path)

        # "Del" 버튼 생성
        self.del_button = QPushButton("Del")
        self.del_button.setIcon(del_icon) # 아이콘 설정
        if del_icon.isNull():
            self.del_button.setIconSize(self.del_button.iconSize())
        else:
            # Del 버튼 아이콘 크기도 텍스트 높이에 맞춤
            del_font = self.del_button.font()
            del_fm = QFontMetrics(del_font)
            del_text_height = del_fm.height()
            del_icon_dimension = max(8, del_text_height - 2)
            self.del_button.setIconSize(QSize(del_icon_dimension, del_icon_dimension))

        # Del 버튼 스타일 및 크기 정책 (Add 버튼과 동일하게)
        self.del_button.setStyleSheet("QPushButton { padding-left: 8px; padding-right: 5px; padding-top: 1px; padding-bottom: 1px; }")
        self.del_button.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        self.del_button.setMinimumHeight(target_min_button_height) # Add 버튼 기준으로 계산된 최소 높이 적용
        # Del 버튼 최대 너비도 Add 버튼과 동일하게 설정
        self.del_button.setMaximumWidth(int(self.width() * increased_width_percentage) if self.width() > 0 else increased_fallback_width)

        self.del_button.clicked.connect(self.on_del_item)

        # 버튼을 레이아웃에 추가 (왼쪽 정렬을 위해 addStretch 사용)
        button_layout.addWidget(self.add_button) # alignment 제거
        button_layout.addWidget(self.del_button)
        button_layout.addStretch(1) # 버튼들을 왼쪽으로 밀어주는 신축성 공간 추가

        # 버튼 레이아웃을 메인 레이아웃에 추가
        self.layout.addLayout(button_layout)

        self.tree_widget = MTTreeWidget(self._viewmodel)
        self.layout.addWidget(self.tree_widget)
        self.setLayout(self.layout)

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

    def on_add_item(self):
        selected_items = self.tree_widget.selectedItems()
        parent_id = None
        if selected_items:
            parent_id = selected_items[0].data(0, 32)  # Qt.ItemDataRole.UserRole
        self._viewmodel.add_item('New Item', parent_id, node_type=MTNodeType.INSTRUCTION)

    def on_del_item(self):
        print("Delete button clicked")
        selected_items = self.tree_widget.selectedItems()
        if selected_items:
            item_to_delete = selected_items[0]
            item_id = item_to_delete.data(0, 32) # UserRole에서 ID 가져오기
            print(f"Attempting to delete item with ID: {item_id}")
            # self._viewmodel.remove_item(item_id) # 뷰모델에 삭제 요청
        else:
            print("No item selected to delete.")

    def set_viewmodel(self, viewmodel):
        self._viewmodel = viewmodel
        self.tree_widget.set_viewmodel(viewmodel)

    def on_viewmodel_signal(self, signal_type, data):
        # ViewModel로부터 받은 신호에 따라 TreeWidget의 특정 업데이트 메서드 호출
        if signal_type == 'item_added':
            item_id = data.get('item_id')
            parent_id = data.get('parent_id')
            if item_id:
                # ViewModel을 통해 추가된 아이템의 상세 정보 가져오기
                item_data = self._viewmodel.get_item(item_id)
                if item_data:
                    print(f"View: Received item_added signal for {item_id}, calling handle_item_added...")
                    self.tree_widget.handle_item_added(item_data, parent_id)
                else:
                    print(f"Warning: Could not get item data for added item {item_id}")
                    self.tree_widget.update_tree_items() # 예외 처리: 정보 없으면 전체 업데이트
            else:
                 self.tree_widget.update_tree_items() # 예외 처리: ID 없으면 전체 업데이트

        elif signal_type == 'item_removed':
            item_id = data.get('item_id')
            if item_id:
                print(f"View: Received item_removed signal for {item_id}, calling handle_item_removed...")
                self.tree_widget.handle_item_removed(item_id)
            else:
                self.tree_widget.update_tree_items() # 예외 처리

        elif signal_type == 'item_moved':
            item_id = data.get('item_id')
            new_parent_id = data.get('new_parent_id')
            old_parent_id = data.get('old_parent_id') # 이동 전 부모 정보도 필요할 수 있음
            if item_id:
                 print(f"View: Received item_moved signal for {item_id}, calling handle_item_moved...")
                 self.tree_widget.handle_item_moved(item_id, new_parent_id, old_parent_id)
            else:
                 self.tree_widget.update_tree_items() # 예외 처리

        elif signal_type == 'item_modified':
            item_id = data.get('item_id')
            changes = data.get('changes')
            if item_id and changes:
                 print(f"View: Received item_modified signal for {item_id}, calling handle_item_modified...")
                 self.tree_widget.handle_item_modified(item_id, changes)
            else:
                 self.tree_widget.update_tree_items() # 예외 처리

        elif signal_type == 'tree_reset':
            print("View: Received tree_reset signal, calling update_tree_items...")
            self.tree_widget.update_tree_items() # 트리가 리셋되면 전체 업데이트 필요
        # 필요시 추가 분기