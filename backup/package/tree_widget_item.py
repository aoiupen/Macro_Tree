"""트리 위젯 아이템 모듈

트리 위젯의 각 아이템을 관리하는 클래스를 제공합니다.
"""
from typing import Optional, Union
from PyQt6.QtWidgets import QTreeWidgetItem, QLineEdit, QLabel, QTreeWidget
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import Qt
from package.logic.tree_widget_item_logic import TreeWidgetItemLogic
from package.components.custom_widgets import InpTogBtn, SubTogBtn, PosWidget
from package.resources.resources import rsc


class TreeWidgetItem(QTreeWidgetItem):
    """트리 위젯의 아이템을 관리하는 클래스
    
    각 아이템의 상태와 동작을 처리합니다.
    """

    def __init__(self, tree_widget: QTreeWidget, parent: Optional[QTreeWidgetItem] = None, row: str = "") -> None:
        """TreeWidgetItem 생성자
        
        Args:
            tree_widget: 부모 트리 위젯
            parent: 부모 아이템 (기본값: None)
            row: 아이템 데이터 문자열 (기본값: "")
        """
        super().__init__(parent)
        self.tree_widget = tree_widget
        self.logic = TreeWidgetItemLogic(row)

        self.setCheckState(0, Qt.CheckState.Checked)
        self.setIcon(0, QIcon(rsc["tree_icons"][self.logic.typ]["icon"]))
        self.setText(0, self.logic.name)
        self.setFlags(self.flags() | Qt.ItemIsEditable)
        self.setExpanded(True)

        if self.logic.is_inst():
            self.set_widget(self.tree_widget)

    def set_widget(self, tree_widget: QTreeWidget) -> None:
        """아이템의 위젯을 설정합니다.
        
        Args:
            tree_widget: 트리 위젯 인스턴스
        """
        self.setFlags(self.flags() ^ Qt.ItemIsDropEnabled)

        self.inp_tog = InpTogBtn(self, self.logic.inp)
        self.inp_tog.inp_changed.connect(self.toggle_input)

        if self.logic.inp == "M":
            x, y = self.logic.sub_con.split(",")
            self.sub_wid = PosWidget(x, y)
        else:
            if self.logic.sub == "typing":
                self.sub_wid = QLineEdit()
            else:
                self.sub_wid = QLabel()
            self.sub_wid.setText(self.logic.sub_con)
            self.sub_wid.setFixedSize(115, 25)

        self.sub_tog = SubTogBtn(self, self.logic.inp, self.logic.sub)
        self.sub_tog.sub_changed.connect(self.toggle_subact)

        tree_widget.setItemWidget(self, 1, self.inp_tog)
        tree_widget.setItemWidget(self, 2, self.sub_wid)
        tree_widget.setItemWidget(self, 3, self.sub_tog)

    def toggle_input(self) -> None:
        """입력 상태를 토글합니다."""
        self.logic.toggle_input()
        self.inp_tog.setIcon(QIcon(rsc["inputs"][self.logic.inp]["icon"]))
        self.sub_tog.setIcon(QIcon(rsc["subacts"][self.logic.sub]["icon"]))
        self.finish_tog()

    def toggle_subact(self) -> None:
        """하위 동작 상태를 토글합니다."""
        self.logic.toggle_subact()
        self.sub_tog.setIcon(QIcon(rsc["subacts"][self.logic.sub]["icon"]))
        self.update_sub_widget()
        self.finish_tog()

    def update_sub_widget(self) -> None:
        """하위 위젯을 업데이트합니다."""
        self.tree_widget.removeItemWidget(self, 2)
        if self.logic.inp == "M":
            x, y = self.logic.sub_con.split(",")
            self.sub_wid = PosWidget(x, y)
        else:
            if self.logic.sub == "typing":
                self.sub_wid = QLineEdit()
            else:
                self.sub_wid = QLabel()
            self.sub_wid.setText(self.logic.sub_con)
            self.sub_wid.setFixedSize(115, 25)
        self.tree_widget.setItemWidget(self, 2, self.sub_wid)

    def finish_tog(self) -> None:
        """토글 작업을 완료하고 트리 상태를 업데이트합니다."""
        self.tree_widget.update_tree_state()
        self.tree_widget.save_to_db()
        self.tree_widget.setFocus()