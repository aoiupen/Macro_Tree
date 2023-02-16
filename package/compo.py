from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from package import pos as ps
from package import compo as cp

class PosBtn(QPushButton):
    double_signal = pyqtSignal()
    def __init__(self,name):
        super().__init__()
        self.setText(name)
        self.clicked.connect(self.run)
    def run(self):
        self.double_signal.emit()

class RegBtn(QPushButton):
    def __init__(self,name):
        super().__init__()
        self.setText(name)
        self.pos_pair = []
        self.setFixedSize(QSize(50,20))
        self.setStyleSheet("color:red")

class MouseTogBtn(QPushButton):
    signal = pyqtSignal()
    def __init__(self,parent,typ):
        QPushButton.__init__(self)
        self.setFixedWidth(30)
        self.prnt = parent
        #self.setText(typ)
        self.cur_typ = "C1"
        self.clicked.connect(self.run)
        if typ == "C1":
            self.setIcon(QIcon("src/cursor.png"))
        else:
            self.setIcon(QIcon("src/cursor2.png"))

    def run(self):
        self.signal.emit()

class KeyTogBtn(QPushButton):
    signal = pyqtSignal()
    def __init__(self,parent,typ):
        QPushButton.__init__(self)
        self.setFixedWidth(30)
        self.prnt = parent
        self.cur_typ = "T"
        #self.setText(typ)
        self.clicked.connect(self.run)
        if typ == "C":
            self.setIcon(QIcon("src/copy.png"))
        elif typ == "P":
            self.setIcon(QIcon("src/paste.png"))
        elif typ == "A":
            self.setIcon(QIcon("src/all.png"))
        else:
            self.setIcon(QIcon("src/key.png"))

    def run(self):
        self.signal.emit()

class TypBtn(QPushButton):
    signal = pyqtSignal()
    def __init__(self,parent,typ):
        QPushButton.__init__(self)
        self.prnt = parent
        self.setText(typ)
        self.clicked.connect(self.run)
        if typ == "M":
            self.setIcon(QIcon("src/cursor.png"))
        else:
            self.setIcon(QIcon("src/key.png"))

    def run(self):
        self.signal.emit()

class ActCb(QComboBox):
    signal = pyqtSignal()
    def __init__(self,tw,typ,act):
        QComboBox.__init__(self)
        act_lst = tw.act_items[typ]
        ix = act_lst.index(act)
        for a in act_lst:
            self.addItem(a)
        self.setCurrentIndex(ix)
        ##self.setStyleSheet("background-color: rgb(250,250,250);")
        self.currentIndexChanged.connect(self.run)
        
    def run(self):
        self.signal.emit()

class PosWidget(QWidget):
    signal = pyqtSignal()
    def __init__(self,pos):
        QWidget.__init__(self)
        self.minimumSize().height()
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
        self.second = ps.Second(self,self.btn)
        self.second.show()
    
