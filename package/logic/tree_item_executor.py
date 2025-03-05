"""트리 아이템 실행 모듈

트리 위젯 아이템의 실행 로직을 처리하는 클래스를 제공합니다.
"""
import pyautogui as pag
from typing import List, Optional
from package.tree_widget_item import TreeWidgetItem


class TreeItemExecutor:
    """트리 아이템 실행 클래스
    
    트리 위젯 아이템의 실행 로직을 처리합니다.
    """
    
    def __init__(self, tree_widget) -> None:
        """TreeItemExecutor 생성자
        
        Args:
            tree_widget: 실행할 아이템이 포함된 트리 위젯
        """
        self.tree_widget = tree_widget

    def execute_selected_items(self) -> None:
        """선택된 TreeWidgetItem들을 실행합니다."""
        selected_items = self.tree_widget.selectedItems()
        for item in selected_items:
            if isinstance(item, TreeWidgetItem):
                self.execute_item(item)

    def execute_item(self, item: TreeWidgetItem) -> None:
        """선택된 아이템에 따라 특정 동작을 수행합니다.
        
        Args:
            item: 실행할 트리 위젯 아이템
        """
        inp = item.inp_tog.cur  # 입력 상태
        sub = item.sub_tog.cur  # 서브 액션

        if inp == "M":  # 마우스 동작
            self.perform_mouse_action(sub, item)
        elif inp == "K":  # 키보드 동작
            self.perform_keyboard_action(sub, item)

    def perform_mouse_action(self, action: str, item: TreeWidgetItem) -> None:
        """마우스 동작을 수행합니다.
        
        Args:
            action: 수행할 마우스 동작 유형
            item: 동작을 수행할 트리 위젯 아이템
        """
        x, y = map(int, item.sub_wid.coor_str.split(','))  # 좌표 가져오기
        
        if action == "click":
            print(f"Mouse click at ({x}, {y}): {item.text(0)}")
            pag.click(x=x, y=y)
        elif action == "double":
            print(f"Mouse double click at ({x}, {y}): {item.text(0)}")
            pag.click(x=x, y=y, clicks=2)
        elif action == "right":
            print(f"Mouse right click at ({x}, {y}): {item.text(0)}")
            pag.rightClick(x=x, y=y)
        elif action == "drag":
            print(f"Mouse drag from ({x}, {y}): {item.text(0)}")
            pag.moveTo(x=x, y=y)
            pag.dragTo(x=x + 100, y=y + 100, duration=0.2)  # 예시로 드래그 동작

    def perform_keyboard_action(self, action: str, item: TreeWidgetItem) -> None:
        """키보드 동작을 수행합니다.
        
        Args:
            action: 수행할 키보드 동작 유형
            item: 동작을 수행할 트리 위젯 아이템
        """
        if action == "typing":
            print(f"Keyboard typing: {item.text(0)}")
            pag.write(item.text(0))  # 텍스트 입력
        elif action == "copy":
            print(f"Keyboard copy: {item.text(0)}")
            pag.hotkey('ctrl', 'c')  # 복사
        elif action == "paste":
            print(f"Keyboard paste: {item.text(0)}")
            pag.hotkey('ctrl', 'v')  # 붙여넣기
        elif action == "select_all":
            print(f"Keyboard select all: {item.text(0)}")
            pag.hotkey('ctrl', 'a')  # 전체 선택