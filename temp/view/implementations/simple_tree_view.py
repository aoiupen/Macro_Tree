from PyQt5.QtWidgets import QTreeWidget, QTreeWidgetItem, QApplication, QStyle
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QCursor

from ...viewmodel.implementations.simple_tree_viewmodel import SimpleTreeViewModel

class SimpleTreeView(QTreeWidget):
    def __init__(self, viewmodel: SimpleTreeViewModel, parent=None):
        super().__init__(parent)
        self._viewmodel = viewmodel
        
        # 아이콘 설정
        style = QApplication.style()
        self.expanded_icon = style.standardIcon(QStyle.SP_DirOpenIcon)
        self.collapsed_icon = style.standardIcon(QStyle.SP_DirClosedIcon)
        
        # 이벤트 연결
        self.itemClicked.connect(self.item_clicked)
        
        self.setHeaderLabel("트리 아이템")
        self._update_display()
    
    def _update_display(self):
        self.update_tree_items()
    
    def item_clicked(self, item, column):
        """아이템 클릭 처리"""
        item_id = item.data(0, Qt.UserRole)
        
        # 특정 아이콘 영역이 클릭되었는지 확인 (확장/축소 영역)
        if self.is_expand_icon_clicked(item):
            # 확장/축소 토글
            self._viewmodel.toggle_expanded(item_id)
        else:
            # 일반 클릭은 선택 처리
            self._viewmodel.select_item(item_id)
        
        self._update_display()  # 화면 갱신

    def is_expand_icon_clicked(self, item):
        """클릭 위치가 확장/축소 아이콘 영역인지 확인"""
        # 마우스 위치 가져오기
        pos = self.mapFromGlobal(QCursor.pos())
        item_rect = self.visualItemRect(item)
        
        # 아이콘 영역은 보통 항목 시작 부분에 있음
        # 예: 좌측에서 20px 영역을 아이콘 영역으로 간주
        icon_rect_width = 20
        
        # 레벨에 따른 들여쓰기 고려
        level = item.data(0, Qt.UserRole + 1) or 0
        
        # 아이콘 영역 계산 (들여쓰기 + 아이콘 위치)
        icon_left = item_rect.left() + level
        icon_right = icon_left + icon_rect_width
        
        # 클릭 위치가 아이콘 영역 내에 있는지 확인
        return pos.x() >= icon_left and pos.x() <= icon_right and \
               pos.y() >= item_rect.top() and pos.y() <= item_rect.bottom()

    def update_tree_items(self):
        """트리 아이템 갱신 - 계층 구조 지원"""
        self.clear()
        
        # ViewModel 메서드 호환성 처리
        if hasattr(self._viewmodel, 'get_visible_items'):
            items = self._viewmodel.get_visible_items()
        else:
            items = self._viewmodel.get_items_for_display()
        
        for item_data in items:
            tree_item = QTreeWidgetItem(self)
            tree_item.setText(0, item_data["name"])
            tree_item.setData(0, Qt.UserRole, item_data["id"])
            
            # 선택 상태 적용
            if item_data.get("selected", False):
                tree_item.setSelected(True)
            
            # 확장/축소 상태 표시 (has_children 속성이 있는 경우)
            if item_data.get("has_children", False):
                if item_data.get("expanded", False):
                    tree_item.setIcon(0, self.expanded_icon)
                else:
                    tree_item.setIcon(0, self.collapsed_icon)
            
            # 들여쓰기 추가 (레벨 정보가 있는 경우)
            if "level" in item_data:
                indent = item_data["level"] * 20  # 20픽셀 단위로 들여쓰기
                tree_item.setData(0, Qt.UserRole + 1, indent)  # 커스텀 데이터로 저장
