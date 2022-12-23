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

class TypBtn(QPushButton):
    signal = pyqtSignal()
    def __init__(self,parent,typ):
        QPushButton.__init__(self)
        self.prnt = parent
        self.setText(typ)
        self.clicked.connect(self.run)
        if typ == "Mouse":
            self.setIcon(QIcon("src/cursor.png"))
        else:
            self.setIcon(QIcon("src/key.png"))
        
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
        self.coor = QLineEdit(pos,self)
        self.coor.setFixedWidth(80)
        self.btn = cp.PosBtn("pos")
        self.btn.setFixedWidth(50)
        self.widget_lay.addWidget(self.coor)
        self.widget_lay.addWidget(self.btn)
        self.btn.clicked.connect(self.run)
        
    def run(self):
        self.signal.emit()
                
    def get_pos(self):
        self.second = ps.Second(self,self.btn)
        self.second.show()
    
class ActCb(QComboBox):
    signal = pyqtSignal()
    def __init__(self,typ,act):
        QComboBox.__init__(self)
        if typ == "Mouse":
            act_lst = ["Click","Double","Right","Drag","Move"]
            for a in act_lst:
                self.addItem(a)
            if act == "Click":
                self.setCurrentIndex(0)
            elif act == "Double":
                self.setCurrentIndex(1)
            elif act == "Right":
                self.setCurrentIndex(2)
            elif act == "Drag":
                self.setCurrentIndex(3)
            else:
                self.setCurrentIndex(4)
        elif typ == "Key":
            self.addItem("Copy")
            self.addItem("Paste")
            self.addItem("Select All")
            if act == "Copy":
                self.setCurrentIndex(0)
            elif act == "Paste":
                self.setCurrentIndex(1)
            else:
                self.setCurrentIndex(2)    
        #self.setStyleSheet("background-color: rgb(250,250,250);")
        self.currentIndexChanged.connect(self.run)
        
    def run(self):
        self.signal.emit()