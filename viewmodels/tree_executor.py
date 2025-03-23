"""트리 아이템 실행 모듈

트리 위젯 아이템의 실행 로직을 처리하는 클래스를 제공합니다.
"""
import pyautogui as pag
from typing import List, Optional, Any
from viewmodels.interfaces.item_interface import IItemViewModel
from viewmodels.interfaces.tree_interface import ITreeViewModel
from viewmodels.interfaces.executor_interface import IExecutor


class TreeExecutor(IExecutor):
    """트리 아이템 실행 클래스
    
    트리 위젯 아이템의 실행 로직을 처리합니다.
    """
    
    def __init__(self, tree_view_model: ITreeViewModel) -> None:
        """TreeExecutor 생성자
        
        Args:
            tree_view_model: 트리 뷰모델
        """
        self.command_buffer: List[str] = []  # Item 대신 ID 저장
        self._tree_view_model = tree_view_model
    
    def add_to_buffer(self, item_id: str) -> None:
        """명령을 버퍼에 추가"""
        self.command_buffer.append(item_id)
    
    def clear_buffer(self) -> None:
        """버퍼 초기화"""
        self.command_buffer.clear()
    
    def execute_buffered_commands(self) -> None:
        """버퍼에 있는 모든 명령을 순회하며 실행"""
        for item_id in self.command_buffer:
            self.execute_item(item_id)
        self.clear_buffer()
    
    def execute_item(self, item_id: str) -> bool:
        """아이템 ID로 실행"""
        item_vm = self._tree_view_model.get_item(item_id)
        if not item_vm:
            return False
            
        # 그룹 아이템인 경우 자식 아이템들을 모두 실행
        if item_vm.is_group():
            children_ids = self._tree_view_model.get_children_ids(item_id)
            for child_id in children_ids:
                self.execute_item(child_id)
            return True
            
        # 인스턴스 아이템인 경우 실행하지 않음
        if item_vm.is_inst():
            return False
            
        # 입력 타입에 따라 실행
        if item_vm.inp == "M":
            action = item_vm.sub
            if action.startswith("M_"):
                action = action[2:]
            return self._execute_mouse_action(action, item_vm)
        else:  # item_vm.inp == "K"
            action = item_vm.sub
            if action.startswith("K_"):
                action = action[2:]
            return self._execute_keyboard_action(action, item_vm)
    
    def _execute_mouse_action(self, action: str, item_vm: IItemViewModel) -> bool:
        """마우스 액션 실행"""
        try:
            x, y = map(int, item_vm.sub_con.split(','))
            
            # 액션 수행
            if action == "click":
                pag.click(x, y)
            elif action == "double":
                pag.doubleClick(x, y)
            else:
                print(f"지원하지 않는 마우스 액션: {action}")
                return False
            return True
        except (ValueError, AttributeError):
            print(f"잘못된 좌표 형식: {item_vm.sub_con}")
            return False
    
    def _execute_keyboard_action(self, action: str, item_vm: IItemViewModel) -> bool:
        """키보드 액션 실행"""
        # 텍스트 값 가져오기
        text = item_vm.sub_con
        
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
            return False
        return True
    
    def execute_selected_items(self) -> None:
        """선택된 아이템들을 실행합니다."""
        selected_items = self._tree_view_model.selected_items
        for item_id in selected_items:
            self.execute_item(item_id)
    
    def execute_mouse_item(self, action: str, item_vm: IItemViewModel) -> None:
        """마우스 아이템을 실행합니다.
        
        Args:
            action: 수행할 액션 (click, double)
            item_vm: 실행할 아이템의 뷰모델
        """
        self._execute_mouse_action(action, item_vm)
    
    def execute_keyboard_item(self, action: str, item_vm: IItemViewModel) -> None:
        """키보드 아이템을 실행합니다.
        
        Args:
            action: 수행할 액션 (typing, copy, paste)
            item_vm: 실행할 아이템의 뷰모델
        """
        self._execute_keyboard_action(action, item_vm) 