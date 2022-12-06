from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from package import compo as cp
from screeninfo import get_monitors

class Second(QWidget):
    def __init__(self,ui,btn):
        super().__init__()
        self.ui = ui
        self.setWindowTitle("Test")
        self.setWindowFlags(Qt.FramelessWindowHint)
        m = get_monitors()[0]
        self.res_w = m.width
        self.res_h = m.height
        
        self.shocut_dict = [('ESC',self.cls_win),('Ctrl+M',self.max_win),('Ctrl+S',self.min_win)]
        self.shocut_list = []
        for shocut_d in self.shocut_dict:
            shocut = QShortcut(QKeySequence(shocut_d[0]), self)
            shocut.activated.connect(shocut_d[1])
            self.shocut_list.append(shocut)
        
        self.setGraphicsEffect(QGraphicsOpacityEffect(self))
        self.setAutoFillBackground(True)
        self.setWindowOpacity(0.1)
        self.setStyleSheet("background-color: white;")
        self.max_win()
        self.btn = btn
        
    def min_win(self):
        self.setGeometry(0, 0, 20, 20)
 
    def max_win(self):
        self.setGeometry(0, 0, self.res_w,self.res_h)
    
    def input_coor_to_btn(self,str):
        pass
    
    # pos -> treewidgetitem에 저장
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.offset = event.pos()
            x= str(self.offset.x())
            y= str(self.offset.y())
            coor = x + "," + y
            # treewidgetitem->poswidget->cp.PosBtn
            if isinstance(self.btn,cp.PosBtn):
                self.btn.pos = coor
                self.btn.parent().coor.setText(coor)
                self.btn.setStyleSheet("color:black")               
                self.close()
            else:
                pos_pair = self.btn.pos_pair
                if len(pos_pair) == 2:
                    pos_pair = []
                pos_pair.append(coor)
                if len(pos_pair) == 2:
                    self.btn.setStyleSheet("color:black")
                    self.close()
        else:
            super().mousePressEvent(event)
            
    def mouseMoveEvent(self, event):
        if self.offset is not None and event.buttons() == Qt.LeftButton:
            self.move(self.pos() + event.pos() - self.offset)
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        self.offset = None
        super().mouseReleaseEvent(event)        

    def cls_win(self):
        self.close()
        
    # move to getpos.py later
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setPen(QPen(Qt.green, 8, Qt.SolidLine))
        # db.inst_dict
        painter.drawEllipse(40, 40, 40, 40)
        return
        