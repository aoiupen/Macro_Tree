from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from package import pos as ps
from package import compo as cp

#옮길때 pos coor 값 보존
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

class TypCb(QComboBox):
    signal = pyqtSignal()
    def __init__(self,parent,typ):
        QComboBox.__init__(self)
        
        self.prnt = parent
        self.addItem("Mouse")
        self.addItem("Key")
        idx = lambda x : 0 if x == "Mouse" else 1
        self.setCurrentIndex(idx(typ))
        #self.setStyleSheet("background-color: rgb(250,250,250);")
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
        self.coor = QLineEdit(pos,self)
        self.coor.setFixedWidth(80)
        self.pos_btn = cp.PosBtn("pos")
        self.pos_btn.setFixedWidth(50)
        self.widget_lay.addWidget(self.coor)
        self.widget_lay.addWidget(self.pos_btn)
        self.pos_btn.clicked.connect(self.run)
        
    def run(self):
        self.signal.emit()
                
    def get_pos(self):
        self.second = ps.Second(self,self.pos_btn)
        self.second.show()
    
class ActCb(QComboBox):
    signal = pyqtSignal()
    def __init__(self,typ,act):
        QComboBox.__init__(self)
        if typ == "Mouse":
            self.addItem("Click")
            self.addItem("Double")
            self.addItem("Right")
            self.addItem("Drag")
            self.addItem("Move")
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