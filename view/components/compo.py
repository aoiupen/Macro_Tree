from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from utils import mouse_position as ps
from resources.resources import *
import copy

class PosBtn(QPushButton):
    double_signal = pyqtSignal()
    def __init__(self, name):
        super().__init__()
        self.setText(name)
        self.clicked.connect(self.run)
        
    def run(self):
        self.double_signal.emit()

class InpTogBtn(QPushButton):
    signal = pyqtSignal()
    def __init__(self, parent, inp):
        QPushButton.__init__(self)
        self.prnt = parent
        self.setFixedWidth(30)
        self.clicked.connect(self.run)
        self.cur = inp
        self.iters = iter(rsc["input"])
        # 현재 입력 타입에 맞게 이터레이터 위치 조정
        for item in rsc["input"]:
            if item == self.cur:
                break
            next(self.iters, None)
        
        self.setIcon(QIcon(rsc["inputs"][self.cur]["icon"]))

    def run(self):
        self.signal.emit()
        
class SubTogBtn(QPushButton):
    signal = pyqtSignal()
    def __init__(self, parent, inp, sub):
        QPushButton.__init__(self)
        self.prnt = parent
        self.cur = sub
        self.iters = iter(rsc["inputs"][inp]["subacts"])
        # 현재 서브액션에 맞게 이터레이터 위치 조정
        for item in rsc["inputs"][inp]["subacts"]:
            if item == self.cur:
                break
            next(self.iters, None)
            
        self.setFixedWidth(30)
        self.clicked.connect(self.run)
        self.setIcon(QIcon(rsc["subacts"][self.cur]["icon"])) # 주어진 sub_act을 넣고, next 기반 마련해야함

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
        self.coor_btn = PosBtn("")
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
        
    def update_position(self, x, y):
        """마우스 위치를 업데이트합니다.
        
        Args:
            x: X 좌표
            y: Y 좌표
        """
        self.coor_x_edit.setText(str(x))
        self.coor_y_edit.setText(str(y)) 