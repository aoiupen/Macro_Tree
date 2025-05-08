from PyQt6.QtWidgets import QTreeWidget, QTreeWidgetItem, QAbstractItemView
from PyQt6.QtCore import Qt
from viewmodel.impl.tree_viewmodel import MTTreeViewModel

# RF : 트리뷰는 트리뷰모델을 상속받지 않고, 참조
class TreeView(QTreeWidget):
    def __init__(self, viewmodel: MTTreeViewModel, parent=None):
        super().__init__(parent)
        self._viewmodel = viewmodel
        
        # 이벤트 연결
        self.itemClicked.connect(self.item_clicked)
        self.itemExpanded.connect(self._on_item_expanded)
        self.itemCollapsed.connect(self._on_item_collapsed)
        
        # 드래그 앤 드롭 설정
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.setDropIndicatorShown(True)
        self.setDragDropMode(QAbstractItemView.DragDropMode.InternalMove)
        
        self.setHeaderLabel("트리 아이템")
        self.update_tree_items()
    
    def set_viewmodel(self, viewmodel):
        """
        뷰모델을 설정합니다.
        
        Args:
            viewmodel: 새 뷰모델
        """
        self._viewmodel = viewmodel
        self.update_tree_items()
    
    def update_tree_items(self):
        # 현재 선택 상태 기억
        selected_ids = self._viewmodel.get_selected_items()
        
        self.clear()
        
        # 아이템 ID -> QTreeWidgetItem 매핑
        self._id_to_widget_map = {}
        
        # 부모-자식 관계 처리를 위한 두 단계 접근법
        self._build_tree_items()
        self._apply_tree_state()
    
    def _build_tree_items(self):
        # 1단계: 모든 아이템 생성
        all_items = self._viewmodel.get_tree_items()
        # 먼저 루트 아이템 추가
        for item_id, item in all_items.items():
            parent_id = item.get_property("parent_id")
            if not parent_id:
                self._add_tree_item(item, self)
        
        # 다음 자식 아이템 추가 (부모 참조로)
        for item_id, item in all_items.items():
            parent_id = item.get_property("parent_id")
            if parent_id and parent_id in self._id_to_widget_map:
                parent_widget = self._id_to_widget_map[parent_id]
                self._add_tree_item(item, parent_widget)
    
    def _apply_tree_state(self):
        # 2단계: 확장/선택 상태 적용
        for item_id, widget_item in self._id_to_widget_map.items():
            item = self._viewmodel.get_item(item_id)
            if item:
                # 확장 상태 적용
                if item.get_property("expanded", False):
                    self.expandItem(widget_item)
                
                # 선택 상태 적용
                if item_id in self._viewmodel.get_selected_items():
                    widget_item.setSelected(True)
    
    def item_clicked(self, item, column):
        item_id = item.data(0, Qt.UserRole)
        self._viewmodel.select_item(item_id)
        self.update_tree_items()

    def _on_item_expanded(self, item):
        item_id = item.data(0, Qt.UserRole)
        self._viewmodel.toggle_expanded(item_id, True)

    def _on_item_collapsed(self, item):
        item_id = item.data(0, Qt.UserRole)
        self._viewmodel.toggle_expanded(item_id, False) 
    
    def dropEvent(self, event):
        """
        드래그 앤 드롭으로 아이템 이동 시 호출됨
        """
        # 드롭 대상 (위치)
        drop_indicator = self.dropIndicatorPosition()
        target_item = self.itemAt(event.pos())
        
        # 드래그 중인 아이템 (QTreeWidgetItem)
        dragged_item = self.currentItem()
        
        if not dragged_item or not target_item:
            event.ignore()
            return
            
        dragged_id = dragged_item.data(0, Qt.UserRole)
        target_id = target_item.data(0, Qt.UserRole)
        
        if dragged_id == target_id:
            event.ignore()
            return
            
        # 드롭 위치에 따라 처리
        if drop_indicator == QTreeWidget.OnItem:
            # 항목 위에 드롭: 하위 항목으로 이동
            self._viewmodel.move_item(dragged_id, target_id)
        elif drop_indicator == QTreeWidget.AboveItem or drop_indicator == QTreeWidget.BelowItem:
            # 항목 위나 아래에 드롭: 같은 레벨로 이동
            target_parent_id = self._viewmodel.get_item(target_id).get_property("parent_id")
            self._viewmodel.move_item(dragged_id, target_parent_id)
        else:
            # 기타 위치 (루트 레벨로 이동)
            self._viewmodel.move_item(dragged_id, None)
            
        # UI 갱신
        self.update_tree_items()
        
        # 기본 처리 무시 (직접 처리했으므로)
        event.accept()
