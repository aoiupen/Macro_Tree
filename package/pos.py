from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from package import compo as cp
from screeninfo import get_monitors

class Second(QWidget):
    def __init__(self,pos_wgt):
        super().__init__()
        self.pos_wgt = pos_wgt
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.m = get_monitors()[0]
        
        # Set up shortcuts
        self.shortcut_info_list = [('ESC', self.cls_win),
                         ('Ctrl+M', self.max_win),
                         ('Ctrl+S', self.min_win)]
        self.shortcut_list = []
        for shortcut_info in self.shortcut_info_list:
            shortcut = QShortcut(QKeySequence(shortcut_info[0]), self)
            shortcut.activated.connect(shortcut_info[1])
            self.shortcut_list.append(shortcut)
        
        # Set up opacity and background color
        opacity = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(opacity)
        self.setAutoFillBackground(True)
        self.setWindowOpacity(0.1)
        self.setStyleSheet("background-color: white;")
            
        # Maximize the window and set the button
        self.max_win()
        self.pos_wgt.coor_btn
        
    def min_win(self):
        self.setGeometry(0, 0, 20, 20)
 
    def max_win(self):
        self.setGeometry(0, 0, self.m.width,self.m.height)

    # pos -> treewidgetitem에 저장
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            x = str(event.pos().x())
            y = str(event.pos().y())
            coor = x + "," + y
            
            # treewidgetitem->pos_wgt->cp.PosBtn
            if isinstance(self.pos_wgt.coor_btn,cp.PosBtn):
                self.pos_wgt.coor_btn.pos = coor
                self.pos_wgt.coor_btn.setStyleSheet("color:black")       
                self.pos_wgt.ledit_coor.setText(coor)
                self.close()
            else:
                pos_pair = self.coor_btn.pos_pair
                pos_pair.append(coor)

                if len(pos_pair) == 2:
                    self.pos_wgt.coor_btn.setStyleSheet("color:black")
                    self.close()
                    pos_pair.clear()
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
        painter.drawEllipse(40, 40, 40, 40)
        return
        
