class TreeItemExecutor:
    def __init__(self, tree_widget):
        self.tree_widget = tree_widget

    def execute_selected_items(self):
        """선택된 TreeWidgetItem들을 실행"""
        for item in self.tree_widget.selectedItems():
            # item을 실행하는 로직 구현
            if item.logic.inp == "M":
                # 마우스 동작 수행
                if item.logic.sub == "click":
                    print(f"Mouse click: {item.text(0)}")
                    # 마우스 클릭 동작 구현
                elif item.logic.sub == "double":
                    print(f"Mouse double click: {item.text(0)}")
                    # 마우스 더블 클릭 동작 구현
            elif item.logic.inp == "K":
                # 키보드 동작 수행
                if item.logic.sub == "typing":
                    print(f"Keyboard typing: {item.text(0)}")
                    # 키보드 타이핑 동작 구현
                elif item.logic.sub == "copy":
                    print(f"Keyboard copy: {item.text(0)}")
                    # 키보드 복사 동작 구현
                elif item.logic.sub == "paste":
                    print(f"Keyboard paste: {item.text(0)}")
                    # 키보드 붙여넣기 동작 구현

            # ... (다른 실행 관련 로직)