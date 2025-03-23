"""트리 위젯 이벤트 핸들러 모듈

트리 위젯의 이벤트를 처리하는 클래스를 제공합니다.
"""
from typing import List, Optional, cast
from PyQt6.QtWidgets import QMenu, QTreeWidgetItem, QTreeWidget
from PyQt6.QtCore import QObject, pyqtSignal, pyqtSlot, QPoint
from PyQt6.QtGui import QCursor, QKeySequence, QDropEvent, QMouseEvent, QKeyEvent, QAction
from view.item import Item

class TreeEventHandler(QObject):
    """트리 이벤트 처리 클래스"""
    
    selectionChanged = pyqtSignal(list)
    dropCompleted = pyqtSignal(bool)
    treeChanged = pyqtSignal()
    
    def __init__(self, view_model, tree_widget, parent=None):
        super().__init__(parent)
        self._view_model = view_model
        self.tree_widget = tree_widget
        
        # 컨텍스트 메뉴 설정
        self.tree_widget.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tree_widget.customContextMenuRequested.connect(self.show_context_menu)
        
        # 이벤트 핸들러 연결
        self.tree_widget.itemChanged.connect(self.handle_item_change)
        self.tree_widget.itemSelectionChanged.connect(self.handle_item_selection_change)
        self.tree_widget.itemExpanded.connect(self.handle_item_expanded)
        self.tree_widget.itemCollapsed.connect(self.handle_item_collapsed)
        self.tree_widget.itemDoubleClicked.connect(self.handle_item_double_clicked)
        
        # 이벤트 필터 설정
        self.tree_widget.installEventFilter(self.tree_widget)
        
        # 드래그 앤 드롭 설정
        self.tree_widget.setDragDropMode(QTreeWidget.InternalMove)
        
        # 선택된 아이템 추적
        self.selected_items: List[QTreeWidgetItem] = []
    
    def show_context_menu(self, position: QPoint) -> None:
        """컨텍스트 메뉴를 표시합니다.
        
        Args:
            position: 메뉴를 표시할 위치
        """
        # 현재 선택된 아이템 가져오기
        item = self.tree_widget.itemAt(position)
        
        # 메뉴 생성
        menu = QMenu()
        
        # 그룹 추가 액션
        add_group_action = QAction("그룹 추가", self.tree_widget)
        add_group_action.triggered.connect(self.tree_widget.add_group)
        menu.addAction(add_group_action)
        
        # 인스턴스 추가 액션
        add_instance_action = QAction("인스턴스 추가", self.tree_widget)
        add_instance_action.triggered.connect(self.tree_widget.add_instance)
        menu.addAction(add_instance_action)
        
        # 액션 추가 액션
        add_action_action = QAction("액션 추가", self.tree_widget)
        add_action_action.triggered.connect(self.tree_widget.add_action)
        menu.addAction(add_action_action)
        
        # 구분선 추가
        menu.addSeparator()
        
        # 실행 액션 (아이템이 선택된 경우에만)
        if item:
            execute_action = QAction("실행", self.tree_widget)
            execute_action.triggered.connect(lambda: self.tree_widget.execute_selected_items())
            menu.addAction(execute_action)
            
            # 구분선 추가
            menu.addSeparator()
            
            # 삭제 액션
            delete_action = QAction("삭제", self.tree_widget)
            delete_action.triggered.connect(self.delete_selected_items)
            menu.addAction(delete_action)
        
        # 메뉴 표시
        menu.exec_(self.tree_widget.mapToGlobal(position))
    
    def key_press_event(self, event: QKeyEvent) -> None:
        """키 입력 이벤트를 처리합니다.
        
        Args:
            event: 키 이벤트 객체
        """
        # Delete 키 처리
        if event.key() == Qt.Key.Key_Delete:
            self.delete_selected_items()
            event.accept()
        # Ctrl+Z (실행 취소)
        elif event.key() == Qt.Key_Z and event.modifiers() == Qt.KeyboardModifier.ControlModifier:
            self.tree_widget.parent().findChild(QAction, "Undo").trigger()
            event.accept()
        # Ctrl+Y (다시 실행)
        elif event.key() == Qt.Key_Y and event.modifiers() == Qt.KeyboardModifier.ControlModifier:
            self.tree_widget.parent().findChild(QAction, "Redo").trigger()
            event.accept()
        else:
            event.ignore()
    
    def drop_event(self, event: QDropEvent) -> None:
        """드롭 이벤트를 처리합니다."""
        # ViewModel에 위임
        self._view_model.begin_change()
        
        # 기본 드롭 이벤트 처리
        QTreeWidget.dropEvent(self.tree_widget, event)
        
        # 상태 변경을 ViewModel에 전달
        current_state = self.tree_widget.get_current_state()
        self._view_model.end_change(current_state)
    
    def create_undo_point(self) -> None:
        """실행 취소 지점을 생성합니다."""
        # ViewModel에 위임하도록 변경
        current_state = self.tree_widget.get_current_state()
        self._view_model.save_state(current_state)
    
    def handle_item_change(self, item: QTreeWidgetItem, column: int) -> None:
        """아이템 변경 이벤트를 처리합니다."""
        if not isinstance(item, Item):
            return
            
        item_obj = cast(Item, item)
        item_id = item_obj.logic.id
        value = item.text(column)
        
        # ViewModel에 변경 위임
        self._view_model.update_item_property(item_id, column, value)
    
    def handle_item_selection_change(self) -> None:
        """아이템 선택 변경 이벤트를 처리합니다."""
        # 현재 선택된 아이템 저장
        self.selected_items = self.tree_widget.selectedItems()
    
    def delete_selected_items(self) -> None:
        """선택된 아이템들을 삭제합니다."""
        selected = self.tree_widget.selectedItems()
        # ViewModel에 작업 위임
        self._view_model.delete_items([item.logic.id for item in selected])
    
    def handle_item_expanded(self, item: QTreeWidgetItem) -> None:
        """아이템 확장 이벤트를 처리합니다."""
        if isinstance(item, Item):
            item_id = cast(Item, item).logic.id
            # ViewModel에 위임
            self._view_model.update_item_expanded_state(item_id, True)
    
    def handle_item_collapsed(self, item: QTreeWidgetItem) -> None:
        """아이템 축소 이벤트를 처리합니다."""
        if isinstance(item, Item):
            item_id = cast(Item, item).logic.id
            # ViewModel에 위임
            self._view_model.update_item_expanded_state(item_id, False)
    
    def handle_item_double_clicked(self, item: QTreeWidgetItem, column: int) -> None:
        """아이템 더블 클릭 이벤트를 처리합니다."""
        if isinstance(item, Item) and column == 0:
            # 직접 실행하지 않고 ViewModel에 위임
            self._view_model.execute_item(cast(Item, item).logic.id)

    # QML에서 호출할 메서드들 정의
    @pyqtSlot(int, int)
    def moveItem(self, source_index, target_index):
        """항목 위치를 이동합니다."""
        # ViewModel의 moveItem 호출
        return self._view_model.moveItem(source_index, target_index)