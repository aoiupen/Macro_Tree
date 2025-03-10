"""트리 아이템 실행 모듈

트리 위젯 아이템의 실행 로직을 처리하는 클래스를 제공합니다.
"""
import pyautogui as pag
from typing import List, Optional


class TreeExecutor:
    """트리 아이템 실행 클래스
    
    트리 위젯 아이템의 실행 로직을 처리합니다.
    """
    
    def __init__(self, tree_widget) -> None:
        """TreeExecutor 생성자
        
        Args:
            tree_widget: 실행할 아이템이 포함된 트리 위젯
        """
        self.tree_widget = tree_widget
    
    def execute_selected_items(self) -> None:
        """선택된 아이템들을 실행합니다."""
        selected_items = self.tree_widget.selectedItems()
        for item in selected_items:
            self.execute_item(item)
    
    def execute_item(self, item) -> None:
        """단일 아이템을 실행합니다.
        
        Args:
            item: 실행할 트리 위젯 아이템
        """
        # 그룹 아이템인 경우 자식 아이템들을 모두 실행
        if item.logic.is_group():
            for i in range(item.childCount()):
                self.execute_item(item.child(i))
            return
        
        # 인스턴스 아이템인 경우 실행하지 않음
        if item.logic.is_inst():
            return
        
        # 입력 타입에 따라 실행
        if item.logic.inp == "M":
            self.perform_mouse_action(item.logic.sub, item)
        else:  # item.logic.inp == "K"
            self.perform_keyboard_action(item.logic.sub, item)
    
    def perform_mouse_action(self, action: str, item) -> None:
        """마우스 액션을 수행합니다.
        
        Args:
            action: 수행할 액션 (click, double)
            item: 실행할 트리 위젯 아이템
        """
        # 좌표 값 가져오기
        try:
            x, y = map(int, item.logic.sub_con.split(','))
        except (ValueError, AttributeError):
            print(f"잘못된 좌표 형식: {item.logic.sub_con}")
            return
        
        # 액션 수행
        if action == "click":
            pag.click(x, y)
        elif action == "double":
            pag.doubleClick(x, y)
        else:
            print(f"지원하지 않는 마우스 액션: {action}")
    
    def perform_keyboard_action(self, action: str, item) -> None:
        """키보드 액션을 수행합니다.
        
        Args:
            action: 수행할 액션 (typing, copy, paste)
            item: 실행할 트리 위젯 아이템
        """
        # 텍스트 값 가져오기
        text = item.logic.sub_con
        
        # 액션 수행
        if action == "typing":
            pag.typewrite(text)
        elif action == "copy":
            # 클립보드에 복사 (pyperclip 사용)
            try:
                import pyperclip
                pyperclip.copy(text)
            except ImportError:
                print("pyperclip 모듈이 설치되지 않았습니다.")
        elif action == "paste":
            # 클립보드에서 붙여넣기
            pag.hotkey('ctrl', 'v')
        else:
            print(f"지원하지 않는 키보드 액션: {action}") 