from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from package import pos as ps
from package.components import compo as cp
from package import resources
from ..resources import *
import copy

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
        self.coor_list = []
        self.setFixedSize(50,20)
        self.setStyleSheet("color:red")

class InpTogBtn(QPushButton):
    signal = pyqtSignal()
    def __init__(self, parent, inp):
        QPushButton.__init__(self)
        self.prnt = parent
        self.setFixedWidth(30)
        self.clicked.connect(self.run)
        self.cur = inp
        self.iters = copy.deepcopy(rsc["input"])
        # 함수화하기
        while True:
            temp = next(self.iters)
            if self.cur == temp:
                break
        #----------
        self.setIcon(QIcon(rsc[self.cur]["icon"]))

    def run(self):
        self.signal.emit()
        
class SubTogBtn(QPushButton):
    signal = pyqtSignal()
    def __init__(self, parent, inp, sub):
        QPushButton.__init__(self)
        self.prnt = parent
        self.cur = sub
        self.iters = copy.deepcopy(rsc[inp]["subacts"])
        while self.cur != next(self.iters):
            pass
        self.setFixedWidth(30)
        self.clicked.connect(self.run)
        self.setIcon(QIcon(rsc[self.cur]["icon"])) # 주어진 sub_act을 넣고, next 기반 마련해야함

    def run(self):
        self.signal.emit()

class ActCb(QComboBox):
    signal = pyqtSignal()
    def __init__(self, tw, inp, sub):
        QComboBox.__init__(self)
        act_lst = tw.act_items[inp]
        ix = act_lst.index(sub)
        self.addItems(act_lst) # remember this way!
        self.setCurrentIndex(ix)
        self.currentIndexChanged.connect(self.run)
        
    def run(self):
        self.signal.emit()

class PosWidget(QWidget):
    signal = pyqtSignal()
    def __init__(self, coor_x_val, coor_y_val):
        QWidget.__init__(self)
        self.h_lay = QHBoxLayout(self)
        self.h_lay.setContentsMargins(0,0,0,0)
        self.h_lay.setSpacing(0)
        
        # Size of widget
        self.edit_width = 40
        self.lbl_width = 5
        self.btn_width = 30
        
        # Displaying coordinate value
        self.coor_x_edit = QLineEdit(str(coor_x_val), self)
        self.coor_x_edit.setFixedWidth(self.edit_width)
        self.coor_x_edit.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.coor_x_edit.textChanged.connect(self.update_coor)
        self.coor_lbl = QLabel(",")
        self.coor_lbl.setAlignment(Qt.AlignCenter)
        self.coor_lbl.setFixedWidth(self.lbl_width)
        self.coor_y_edit = QLineEdit(str(coor_y_val), self)
        self.coor_y_edit.setFixedWidth(self.edit_width)
        self.coor_y_edit.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.coor_y_edit.textChanged.connect(self.update_coor)
        self.coor_str = self.coor_x_edit.text() + self.coor_lbl.text() + self.coor_y_edit.text()
        
        # Button for getting coordinate
        self.coor_btn = cp.PosBtn("")
        self.coor_btn.setIcon(QIcon(rsc["coor"]["icon"]))
        self.coor_btn.setFixedWidth(self.btn_width)
        self.coor_btn.clicked.connect(lambda ignore,f=self.get_pos:f())
        
        # Adding widgets to layout
        self.h_lay.addWidget(self.coor_x_edit)
        self.h_lay.addWidget(self.coor_lbl)
        self.h_lay.addWidget(self.coor_y_edit)
        self.h_lay.addWidget(self.coor_btn)
    
    def get_pos(self):
        self.poswin = ps.PosWin(self)
        self.poswin.show()
    
    def update_coor(self):
        self.coor_str = self.coor_x_edit.text() + self.coor_lbl.text() + self.coor_y_edit.text()
