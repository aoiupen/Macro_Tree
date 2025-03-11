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
        self.command_buffer = []
    
    def add_to_buffer(self, item):
        """명령을 버퍼에 추가"""
        self.command_buffer.append(item)
    
    def clear_buffer(self):
        """버퍼 초기화"""
        self.command_buffer.clear()
    
    def execute_buffered_commands(self):
        """버퍼에 있는 모든 명령을 순회하며 실행"""
        for item in self.command_buffer:
            self.traverse_and_execute(item)
        self.clear_buffer()
    
    def traverse_and_execute(self, item):
        """
        트리 구조를 순회하며 명령을 찾아 실행합니다.
        
        그룹 아이템인 경우 모든 자식 아이템을 재귀적으로 순회하고,
        인스턴스 아이템인 경우 해당 명령을 실행합니다.
        
        Args:
            item: 순회 시작 아이템 객체
        """
        # 그룹 아이템(폴더)인 경우 자식들을 재귀적으로 순회
        if item.logic.is_group():
            for i in range(item.childCount()):
                self.traverse_and_execute(item.child(i))
        else:
            # 그룹이 아닌 경우(인스턴스 아이템)는 실행
            self.execute_command(item.logic.sub)
    
    def execute_command(self, logic_sub):
        """
        명령을 실행합니다.
        
        명령 타입에 따라 적절한 실행 함수를 호출합니다.
        
        Args:
            logic_sub: 명령 타입 및 세부 정보
        """
        if logic_sub.startswith('K_'):
            self._execute_keyboard_command(logic_sub)
        elif logic_sub.startswith('M_'):
            self._execute_mouse_command(logic_sub)
        else:
            raise ValueError(f"Unknown command type: {logic_sub}")
    
    def _execute_keyboard_command(self, logic_sub):
        """키보드 명령 실행"""
        # 기존 execute_keyboard_item 로직
        pass
    
    def _execute_mouse_command(self, logic_sub):
        """마우스 명령 실행"""
        # 기존 execute_mouse_item 로직
        pass
    
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
            # 접두사 제거하여 실제 액션 추출
            action = item.logic.sub
            if action.startswith("M_"):
                action = action[2:]
            self.execute_mouse_item(action, item)
        else:  # item.logic.inp == "K"
            # 접두사 제거하여 실제 액션 추출
            action = item.logic.sub
            if action.startswith("K_"):
                action = action[2:]
            self.execute_keyboard_item(action, item)
    
    def execute_mouse_item(self, action: str, item) -> None:
        """마우스 아이템을 실행합니다.
        
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
    
    def execute_keyboard_item(self, action: str, item) -> None:
        """키보드 아이템을 실행합니다.
        
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