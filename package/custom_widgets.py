from PyQt5.QtWidgets import QPushButton, QLineEdit, QLabel, QWidget, QGridLayout
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import pyqtSignal, QObject
from resources import rsc

class Signal(QObject):
    signal = pyqtSignal()

class InpTogBtn(QPushButton):
    def __init__(self, parent, inp):
        super().__init__()
        self.parent = parent
        self.inp = inp
        self.setFixedSize(30, 25)
        self.setIcon(QIcon(rsc["inputs"][self.inp]["icon"]))
        self.clicked.connect(self.signal.signal.emit)
        self.signal = Signal()

class SubTogBtn(QPushButton):
    def __init__(self, parent, inp, sub):
        super().__init__()
        self.parent = parent
        self.inp = inp
        self.sub = sub
        self.setFixedSize(30, 25)
        self.setIcon(QIcon(rsc["subacts"][self.sub]["icon"]))
        self.clicked.connect(self.signal.signal.emit)
        self.signal = Signal()

class PosWidget(QWidget):
    def __init__(self, x, y):
        super().__init__()
        self.x_edit = QLineEdit(str(x))
        self.y_edit = QLineEdit(str(y))
        layout = QGridLayout(self)
        layout.addWidget(self.x_edit, 0, 0)
        layout.addWidget(self.y_edit, 0, 1)