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
        self.coor_list = []
        self.setFixedSize(QSize(50,20))
        self.setStyleSheet("color:red")

class MouseTogBtn(QPushButton):
    signal = pyqtSignal()
    def __init__(self, parent, typ, cur):
        QPushButton.__init__(self)
        self.setFixedWidth(30)
        self.prnt = parent
        self.cur_typ = "C1"
        if cur == "C1":
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
        if cur == "C":
            print(cur)
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
    def __init__(self, coor_x_val, coor_y_val):
        QWidget.__init__(self)
        self.widget_lay = QHBoxLayout(self)
        self.widget_lay.setContentsMargins(0,0,0,0)
        self.widget_lay.setSpacing(0)
        
        # Size of widget
        self.edit_width = 40
        self.lbl_width = 10
        self.btn_width = 30
        
        # Image source of widget
        self.coor_btn_icon_src = "src/coor.png"
        
        # Displaying coordinate value
        self.coor_x_edit = QLineEdit(str(coor_x_val), self)
        self.coor_x_edit.setFixedWidth(self.edit_width)
        self.coor_lbl = QLabel(",")
        self.coor_lbl.setAlignment(Qt.AlignCenter)
        self.coor_lbl.setFixedWidth(self.lbl_width)
        self.coor_y_edit = QLineEdit(str(coor_y_val), self)
        self.coor_y_edit.setFixedWidth(self.edit_width)
        
        # Button for getting coordinate
        self.coor_btn = cp.PosBtn("")
        self.coor_btn.setIcon(QIcon(self.coor_btn_icon_src))
        self.coor_btn.setFixedWidth(self.btn_width)
        self.coor_btn.clicked.connect(lambda ignore, f = self.get_pos : f())
        
        # Adding widgets to layout
        self.widget_lay.addWidget(self.coor_x_edit)
        self.widget_lay.addWidget(self.coor_lbl)
        self.widget_lay.addWidget(self.coor_y_edit)
        self.widget_lay.addWidget(self.coor_btn)
    
    def get_pos(self):
        self.poswin = ps.PosWin(self)
        self.poswin.show()
    
