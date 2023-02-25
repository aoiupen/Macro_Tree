from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from package import pos as ps
from package import compo as cp

class PosBtn(QPushButton):
    double_signal = pyqtSignal()
    def __init__(self, name):
        super().__init__()
        self.setText(name)
        self.clicked.connect(self.run)
    def run(self):
        self.double_signal.emit()

class RegBtn(QPushButton):
    def __init__(self, name):
        super().__init__()
        self.setText(name)
        self.pos_pair = []
        self.setFixedSize(QSize(50,20))
        self.setStyleSheet("color:red")

class MouseTogBtn(QPushButton):
    signal = pyqtSignal()
    def __init__(self, parent, typ, cur):
        QPushButton.__init__(self)
        self.setFixedWidth(30)
        self.prnt = parent
        self.cur_typ = "C1"
        if cur:
            self.cur_typ = cur
            self.setStyleSheet("background-color: #B4EEB4")
            
        self.clicked.connect(self.run)
        icon = QIcon("src/cursor.png" if typ == "C1" else "src/cursor2.png")
        self.setIcon(icon)

    def run(self):
        self.signal.emit()

class KeyTogBtn(QPushButton):
    signal = pyqtSignal()
    def __init__(self, parent, typ, cur):
        QPushButton.__init__(self)
        self.setFixedWidth(30)
        self.prnt = parent
        self.cur_typ = "T"
        if cur:
            self.cur_typ = cur
            self.setStyleSheet("background-color: #B4EEB4")
        
        self.clicked.connect(self.run)
        icon = {
            "C": "src/copy.png",
            "P": "src/paste.png",
            "A": "src/all.png",
        }.get(typ, "src/key.png")
        self.setIcon(QIcon(icon))

    def run(self):
        self.signal.emit()

class TypBtn(QPushButton):
    signal = pyqtSignal()
    def __init__(self, parent, typ):
        super().__init__(self)
        self.prnt = parent
        self.setText(typ)
        self.clicked.connect(self.run)
        icon = "src/cursor.png" if typ == "M" else "src/key.png"
        self.setIcon(QIcon(icon))

    def run(self):
        self.signal.emit()

class ActCb(QComboBox):
    signal = pyqtSignal()
    def __init__(self, tw, typ, act):
        QComboBox.__init__(self)
        act_lst = tw.act_items[typ]
        ix = act_lst.index(act)
        self.addItems(act_lst) # remember this way!
        self.setCurrentIndex(ix)
        ##self.setStyleSheet("background-color: rgb(250,250,250);")
        self.currentIndexChanged.connect(self.run)
        
    def run(self):
        self.signal.emit()

class PosWidget(QWidget):
    signal = pyqtSignal()
    def __init__(self, pos):
        QWidget.__init__(self)
        self.widget_lay = QHBoxLayout(self)
        self.widget_lay.setContentsMargins(0,0,0,0)
        self.widget_lay.setSpacing(0)
        self.coor = QLineEdit(pos.rstrip(","),self)
        self.coor.setFixedWidth(80)
        self.btn = cp.PosBtn("")
        self.btn.setIcon(QIcon("src/coor.png"))
        self.btn.setFixedWidth(30)
        self.widget_lay.addWidget(self.coor)
        self.widget_lay.addWidget(self.btn)
        self.btn.clicked.connect(self.run)

    def run(self):
        self.signal.emit()

    def get_pos(self):
        self.second = ps.Second(self, self. btn)
        self.second.show()
    
