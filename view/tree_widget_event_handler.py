"""트리 위젯 이벤트 핸들러 모듈

트리 위젯의 이벤트를 처리하는 클래스를 제공합니다.
"""
from typing import List, Optional
from PyQt5.QtWidgets import QMenu, QAction, QTreeWidgetItem, QTreeWidget
from PyQt5.QtCore import Qt, QPoint, pyqtSlot
from PyQt5.QtGui import QCursor, QKeySequence, QDropEvent, QMouseEvent, QKeyEvent
from viewmodels.tree_undo_redo import TreeUndoCommand


class TreeWidgetEventHandler:
    """트리 위젯 이벤트 핸들러 클래스
    
    트리 위젯의 다양한 이벤트를 처리합니다.
    """

    def __init__(self, tree_widget: QTreeWidget) -> None:
        """TreeWidgetEventHandler 생성자
        
        Args:
            tree_widget: 이벤트를 처리할 트리 위젯 인스턴스
        """
        self.tree_widget = tree_widget
        
        # 이벤트 핸들러 설정
        self.tree_widget.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tree_widget.customContextMenuRequested.connect(self.show_context_menu)
        
        # 원본 이벤트 핸들러 저장
        self.original_keypress = self.tree_widget.keyPressEvent
        self.original_drop = self.tree_widget.dropEvent
        
        # 이벤트 핸들러 오버라이드
        self.tree_widget.keyPressEvent = self.key_press_event
        self.tree_widget.dropEvent = self.drop_event
    
    def show_context_menu(self, position: QPoint) -> None:
        """컨텍스트 메뉴를 표시합니다.
        
        Args:
            position: 메뉴를 표시할 위치
        """
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
        
        # 구분선
        menu.addSeparator()
        
        # 선택된 아이템이 있는 경우에만 삭제 액션 추가
        if self.tree_widget.selectedItems():
            delete_action = QAction("삭제", self.tree_widget)
            delete_action.setShortcut(QKeySequence.Delete)
            delete_action.triggered.connect(self.tree_widget.delete_selected_items)
            menu.addAction(delete_action)
            
            # 구분선
            menu.addSeparator()
            
            # 실행 액션
            execute_action = QAction("실행", self.tree_widget)
            execute_action.setShortcut("F5")
            execute_action.triggered.connect(self.tree_widget.execute_selected_items)
            menu.addAction(execute_action)
        
        # 메뉴 표시
        menu.exec_(QCursor.pos())
    
    def key_press_event(self, event: QKeyEvent) -> None:
        """키 입력 이벤트를 처리합니다.
        
        Args:
            event: 키 이벤트 객체
        """
        # Delete 키 처리
        if event.key() == Qt.Key_Delete:
            self.tree_widget.delete_selected_items()
        # F5 키 처리
        elif event.key() == Qt.Key_F5:
            self.tree_widget.execute_selected_items()
        # Ctrl+Z 처리
        elif event.key() == Qt.Key_Z and event.modifiers() == Qt.ControlModifier:
            self.tree_widget.undo_redo_manager.undo()
        # Ctrl+Y 처리
        elif event.key() == Qt.Key_Y and event.modifiers() == Qt.ControlModifier:
            self.tree_widget.undo_redo_manager.redo()
        # 기타 키 이벤트는 원본 핸들러로 전달
        else:
            self.original_keypress(event)
    
    def drop_event(self, event: QDropEvent) -> None:
        """드롭 이벤트를 처리합니다.
        
        Args:
            event: 드롭 이벤트 객체
        """
        # 드롭 전 상태 저장
        old_state = self.tree_widget.get_current_state()
        
        # 원본 드롭 이벤트 처리
        self.original_drop(event)
        
        # 드롭 후 상태 저장
        new_state = self.tree_widget.get_current_state()
        
        # 실행 취소 명령 추가
        self.tree_widget.undo_redo_manager.push_undo_command(old_state, new_state)
    
    def create_undo_point(self) -> None:
        """현재 상태를 실행 취소 지점으로 저장합니다."""
        # 현재 상태 저장
        current_state = self.tree_widget.get_current_state()
        
        # 스냅샷 추가
        self.tree_widget.tree_repository.add_snapshot(current_state)
    
    def handle_item_change(self, item: QTreeWidgetItem, column: int) -> None:
        """아이템 변경 이벤트를 처리합니다.
        
        Args:
            item: 변경된 아이템
            column: 변경된 열 인덱스
        """
        # 이름 열이 변경된 경우
        if column == 0:
            # 변경 전 상태 저장
            old_state = self.tree_widget.get_current_state()
            
            # 아이템 이름 업데이트
            item.logic.name = item.text(0)
            
            # 변경 후 상태 저장
            new_state = self.tree_widget.get_current_state()
            
            # 실행 취소 명령 추가
            self.tree_widget.undo_redo_manager.push_undo_command(old_state, new_state)
    
    def handle_item_selection_change(self) -> None:
        """아이템 선택 변경 이벤트를 처리합니다."""
        # 선택된 아이템 가져오기
        selected_items = self.tree_widget.selectedItems()
        
        # 선택된 아이템이 없으면 처리하지 않음
        if not selected_items:
            return
        
        # 첫 번째 선택된 아이템 정보 출력
        item = selected_items[0]
        print(f"선택된 아이템: {item.text(0)}")
        
        # 아이템 속성 출력
        print(f"입력 타입: {item.logic.inp}")
        print(f"서브 액션: {item.logic.sub}")
        print(f"서브 액션 값: {item.logic.sub_con}")
    
    def handle_item_expanded(self, item: QTreeWidgetItem) -> None:
        """아이템 확장 이벤트를 처리합니다.
        
        Args:
            item: 확장된 아이템
        """
        # 확장된 아이템 정보 출력
        print(f"확장된 아이템: {item.text(0)}")
        
        # 자식 아이템 수 출력
        print(f"자식 아이템 수: {item.childCount()}")
    
    def handle_item_collapsed(self, item: QTreeWidgetItem) -> None:
        """아이템 축소 이벤트를 처리합니다.
        
        Args:
            item: 축소된 아이템
        """
        # 축소된 아이템 정보 출력
        print(f"축소된 아이템: {item.text(0)}")
    
    def handle_item_double_clicked(self, item: QTreeWidgetItem, column: int) -> None:
        """아이템 더블 클릭 이벤트를 처리합니다.
        
        Args:
            item: 더블 클릭된 아이템
            column: 더블 클릭된 열 인덱스
        """
        # 이름 열이 더블 클릭된 경우
        if column == 0:
            # 아이템 편집 모드 시작
            self.tree_widget.editItem(item, column)
        # 실행 열이 더블 클릭된 경우
        elif column == 3:
            # 아이템 실행
            self.tree_widget.executor.execute_item(item) 