from PyQt5.QtWidgets import QPushButton, QLineEdit, QWidget, QGridLayout
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import pyqtSignal
from package.resources.resources import rsc
from package.db.tree_snapshot_manager import TreeSnapshotManager
from package.db.tree_db_dao import TreeDbDao
from package.db.tree_db import TreeDB

class InpTogBtn(QPushButton):
    inp_changed = pyqtSignal()

    def __init__(self, parent, inp):
        super().__init__()
        self.parent = parent
        self._inp = inp  # 내부적으로 inp를 _inp로 관리
        self.setFixedSize(30, 25)
        self.setIcon(QIcon(rsc["inputs"][self._inp]["icon"]))
        self.clicked.connect(self.inp_changed.emit)

    @property
    def inp(self):
        return self._inp

    @inp.setter
    def inp(self, value):
        self._inp = value
        self.setIcon(QIcon(rsc["inputs"][self._inp]["icon"]))

class SubTogBtn(QPushButton):
    sub_changed = pyqtSignal()

    def __init__(self, parent, inp, sub):
        super().__init__()
        self.parent = parent
        self._sub = sub  # 내부적으로 sub를 _sub로 관리
        self.setFixedSize(30, 25)
        self.setIcon(QIcon(rsc["subacts"][self._sub]["icon"]))
        self.clicked.connect(self.sub_changed.emit)

    @property
    def sub(self):
        return self._sub

    @sub.setter
    def sub(self, value):
        self._sub = value
        self.setIcon(QIcon(rsc["subacts"][self._sub]["icon"]))

class PosWidget(QWidget):
    position_changed = pyqtSignal(int, int)

    def __init__(self, x, y):
        super().__init__()
        self.x_edit = QLineEdit(str(x))
        self.y_edit = QLineEdit(str(y))
        layout = QGridLayout(self)
        layout.addWidget(self.x_edit, 0, 0)
        layout.addWidget(self.y_edit, 0, 1)

        self.x_edit.textChanged.connect(self.on_position_changed)
        self.y_edit.textChanged.connect(self.on_position_changed)

    def on_position_changed(self):
        try:
            x = int(self.x_edit.text())
            y = int(self.y_edit.text())
            self.position_changed.emit(x, y)
        except ValueError:
            pass  # 숫자가 아닌 값이 입력되었을 때 무시

    def get_position(self):
        try:
            x = int(self.x_edit.text())
            y = int(self.y_edit.text())
            return x, y
        except ValueError:
            return None # 숫자가 아닌 값이 입력되었을 때 None 반환

