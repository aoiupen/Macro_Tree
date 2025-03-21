"""트리 위젯 이벤트 핸들러 모듈

트리 위젯의 이벤트를 처리하는 클래스를 제공합니다.
"""
from typing import List, Optional, cast
from PyQt6.QtWidgets import QMenu, QAction, QTreeWidgetItem, QTreeWidget
from PyQt6.QtCore import QObject, pyqtSignal, pyqtSlot
from PyQt6.QtGui import QCursor, QKeySequence, QDropEvent, QMouseEvent, QKeyEvent
from view.item import Item


class TreeEventHandler(QObject):
    """트리 이벤트 처리 클래스"""
    
    selectionChanged = pyqtSignal(list)
    dropCompleted = pyqtSignal(bool)
    treeChanged = pyqtSignal()
    
    def __init__(self, model, parent=None):
        super().__init__(parent)
        self._model = model
        
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
        if event.key() == Qt.Key.Key_Delete::
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
        """드롭 이벤트를 처리합니다.
        
        Args:
            event: 드롭 이벤트 객체
        """
        # 드래그 앤 드롭 작업 전에 상태 저장
        self.create_undo_point()
        
        # 기본 드롭 이벤트 처리
        QTreeWidget.dropEvent(self.tree_widget, event)
        
        # 드래그 앤 드롭 작업 후 상태 변경 알림
        self.tree_widget.stateChanged.emit(self.tree_widget.get_current_state())
    
    def create_undo_point(self) -> None:
        """실행 취소 지점을 생성합니다."""
        # 현재 상태를 저장하여 실행 취소 지점 생성
        self.tree_widget.stateChanged.emit(self.tree_widget.get_current_state())
    
    def handle_item_change(self, item: QTreeWidgetItem, column: int) -> None:
        """아이템 변경 이벤트를 처리합니다.
        
        Args:
            item: 변경된 아이템
            column: 변경된 열 인덱스
        """
        # 아이템이 Item 클래스인 경우에만 처리
        if not isinstance(item, Item):
            return
            
        item_obj = cast(Item, item)
        
        # 첫 번째 열(이름)이 변경된 경우
        if column == 0:
            # 아이템 이름 업데이트
            item_obj.logic.name = item.text(0)
        # 두 번째 열(입력 타입)이 변경된 경우
        elif column == 1:
            # 입력 타입 업데이트
            item_obj.logic.inp = item.text(1)
        # 세 번째 열(서브 컨디션)이 변경된 경우
        elif column == 2:
            # 서브 컨디션 업데이트
            item_obj.logic.sub_con = item.text(2)
        # 네 번째 열(서브)이 변경된 경우
        elif column == 3:
            # 서브 업데이트
            item_obj.logic.sub = item.text(3)
    
    def handle_item_selection_change(self) -> None:
        """아이템 선택 변경 이벤트를 처리합니다."""
        # 현재 선택된 아이템 저장
        self.selected_items = self.tree_widget.selectedItems()
    
    def delete_selected_items(self) -> None:
        """선택된 아이템들을 삭제합니다."""
        # 실행 취소 지점 생성
        self.create_undo_point()
        
        # 선택된 아이템 삭제
        selected = self.tree_widget.selectedItems()
        for item in selected:
            parent = item.parent()
            if parent:
                parent.removeChild(item)
            else:
                index = self.tree_widget.indexOfTopLevelItem(item)
                self.tree_widget.takeTopLevelItem(index)
        
        # 상태 변경 알림
        self.tree_widget.stateChanged.emit(self.tree_widget.get_current_state())
    
    def handle_item_expanded(self, item: QTreeWidgetItem) -> None:
        """아이템 확장 이벤트를 처리합니다.
        
        Args:
            item: 확장된 아이템
        """
        # 아이템이 Item 클래스인 경우에만 처리
        if isinstance(item, Item):
            # 확장 상태 저장
            cast(Item, item).logic.expanded = True
    
    def handle_item_collapsed(self, item: QTreeWidgetItem) -> None:
        """아이템 축소 이벤트를 처리합니다.
        
        Args:
            item: 축소된 아이템
        """
        # 아이템이 Item 클래스인 경우에만 처리
        if isinstance(item, Item):
            # 축소 상태 저장
            cast(Item, item).logic.expanded = False
    
    def handle_item_double_clicked(self, item: QTreeWidgetItem, column: int) -> None:
        """아이템 더블 클릭 이벤트를 처리합니다.
        
        Args:
            item: 더블 클릭된 아이템
            column: 더블 클릭된 열 인덱스
        """
        # 아이템이 Item 클래스인 경우에만 처리
        if isinstance(item, Item) and column == 0:
            # 아이템 실행
            self.tree_widget.executor.execute_item(cast(Item, item))

    # QML에서 호출할 메서드들 정의
    @pyqtSlot(int, int)
    def moveItem(self, source_index, target_index):
        # 기존 로직 재활용하되 QML 호환 방식으로 변경
        # ...