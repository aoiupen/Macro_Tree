import pyautogui as pag
from package.tree_widget_item import TreeWidgetItem

class TreeItemExecutor:
    def __init__(self, tree_widget):
        self.tree_widget = tree_widget

    def execute_selected_items(self):
        """선택된 TreeWidgetItem들을 실행"""
        selected_items = self.tree_widget.selectedItems()
        for item in selected_items:
            if isinstance(item, TreeWidgetItem):
                self.execute_item(item)

    def execute_item(self, item):
        """선택된 아이템에 따라 특정 동작을 수행합니다."""
        inp = item.inp_tog.cur  # 입력 상태
        sub = item.sub_tog.cur   # 서브 액션

        if inp == "M":  # 마우스 동작
            self.perform_mouse_action(sub, item)
        elif inp == "K":  # 키보드 동작
            self.perform_keyboard_action(sub, item)

    def perform_mouse_action(self, action, item):
        """마우스 동작을 수행합니다."""
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

    def perform_keyboard_action(self, action, item):
        """키보드 동작을 수행합니다."""
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