from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from package import compo as cp
from screeninfo import get_monitors

class PosWin(QWidget):
    def __init__(self,pos_wgt):
        super().__init__()
        self.pos_wgt = pos_wgt
        self.setWindowFlags(Qt.FramelessWindowHint) # Frame 없는 Window
        self.monitor_num = 0 # 0번 모니터
        self.monitor = get_monitors()[self.monitor_num]
        self.max_width = self.monitor.width
        self.max_height = self.monitor.height
        self.min_width = 20
        self.min_height = 20
        
        # Set up shortcut_list
        self.shortcut_info_dict = {'ESC' : self.cls_win,
                                'Ctrl+M' : self.max_win,
                                'Ctrl+S' : self.min_win}
        self.shortcut_list = []
        for key_sq_name, key_sq_func in self.shortcut_info_dict.items():
            shortcut = QShortcut(QKeySequence(key_sq_name), self)
            shortcut.activated.connect(key_sq_func)
            self.shortcut_list.append(shortcut)
        
        # Set up opacity val and bg color
        effect = QGraphicsOpacityEffect(self)
        alpha = 0.1
        color = "white"
        self.setGraphicsEffect(effect)
        self.setAutoFillBackground(True)
        self.setWindowOpacity(alpha)
        self.setStyleSheet("background-color:{bg_color};".format(bg_color = color))
            
        # Maximize the window and set the button
        self.max_win()
        
    def min_win(self):
        self.setGeometry(0, 0, self.min_width, self.min_height)
 
    def max_win(self):
        self.setGeometry(0, 0, self.max_width, self.max_height)

    # pos -> treewidgetitem에 저장
    # pos, coor, val 간 naming 기준 필요 : coor_x_val, coor_x_str 로 
    # format : "{상징},{상징}".format(상징=설명,상징=설명)
    # poswidget과 PosWinwin간 변수 통일 필요
    
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            coor_x_val = event.pos().x()
            coor_y_val = event.pos().y()
            coor_x_str = str(coor_x_val)
            coor_y_str = str(coor_y_val)
            coor_str = "{x},{y}".format(x = coor_x_str, y = coor_y_str)
            
            # treewidgetitem -> pos_wgt -> cp.PosBtn
            if isinstance(self.pos_wgt.coor_btn, cp.PosBtn):
                self.pos_wgt.coor_btn.pos = coor_str
                self.pos_wgt.coor_x_edit.setText(coor_x_str)
                self.pos_wgt.coor_y_edit.setText(coor_y_str)
                self.close()
            else:
                self.coor_btn.coor_list.append(coor_str)

                if len(self.coor_btn.coor_list) == 2:
                    self.coor_btn.coor_list.clear()
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
        painter.drawEllipse(40, 40, 40, 40)
        return
        
