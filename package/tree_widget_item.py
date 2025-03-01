from PyQt5.QtWidgets import QTreeWidgetItem, QLineEdit, QLabel
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt
from package.logic.tree_widget_item_logic import TreeWidgetItemLogic
from package.components.custom_widgets import InpTogBtn, SubTogBtn, PosWidget
from package.resources.resources import rsc

class TreeWidgetItem(QTreeWidgetItem):
    def __init__(self, tw, parent=None, row=""):
        QTreeWidgetItem.__init__(self, parent)
        self.tw = tw
        self.logic = TreeWidgetItemLogic(row)

        self.setCheckState(0, Qt.Checked)
        self.setIcon(0, QIcon(rsc["tree_icons"][self.logic.typ]["icon"]))
        self.setText(0, self.logic.name)
        self.setFlags(self.flags() | Qt.ItemIsEditable)
        self.setExpanded(True)

        if self.logic.is_inst():
            self.set_widget(self.tw)

    def set_widget(self, tw):
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

        tw.setItemWidget(self, 1, self.inp_tog)
        tw.setItemWidget(self, 2, self.sub_wid)
        tw.setItemWidget(self, 3, self.sub_tog)

    def toggle_input(self):
        self.logic.toggle_input()
        self.inp_tog.setIcon(QIcon(rsc["inputs"][self.logic.inp]["icon"]))
        self.sub_tog.setIcon(QIcon(rsc["subacts"][self.logic.sub]["icon"]))
        self.update_sub_widget()
        self.finish_tog()

    def toggle_subact(self):
        self.logic.toggle_subact()
        self.sub_tog.setIcon(QIcon(rsc["subacts"][self.logic.sub]["icon"]))
        self.update_sub_widget()
        self.finish_tog()

    def update_sub_widget(self):
        self.tw.removeItemWidget(self, 2)
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
        self.tw.setItemWidget(self, 2, self.sub_wid)

    def finish_tog(self):
        self.tw.update_tree_state()
        self.tw.save_to_db()
        self.tw.setFocus()