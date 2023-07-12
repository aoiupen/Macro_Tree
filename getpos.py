import os
import sys       
from screeninfo import get_monitors
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import pynput
from pynput.mouse import Controller

class FramelessWidget(QWidget):
    def __init__(self, parent=None):
        super(FramelessWidget, self).__init__(parent)
        self.setWindowTitle("Test")
        self.setWindowFlags(Qt.FramelessWindowHint)
        m = get_monitors()[0]
        self.resolution_width = m.width
        self.resolution_height = m.height
        
        self.label = QLabel("", self)
        self.offset = None
        self.quitSc1 = QShortcut(QKeySequence('Ctrl+Q'), self)
        self.quitSc1.activated.connect(self.self_close)
        self.quitSc2 = QShortcut(QKeySequence('Ctrl+M'), self)
        self.quitSc2.activated.connect(self.set_maximize)
        self.quitSc3 = QShortcut(QKeySequence('Ctrl+S'), self)
        self.quitSc3.activated.connect(self.set_minimize)
        
        op = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(op)
        self.setAutoFillBackground(True)
        self.setWindowOpacity(0.3)
        
        self.x = 0
        self.y = 0
        self.offset = QPoint(0,0)

    def set_minimize(self):
        self.setGeometry(0, 0, 20, 20)
        self.setStyleSheet("background-color: yellow;")
        op = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(op)
        self.setAutoFillBackground(True)
        self.setWindowOpacity(1)

    def set_maximize(self):
        self.setGeometry(0, 0, self.resolution_width,
                         self.resolution_height-100)
        self.setStyleSheet("background-color: white;")
        op = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(op)
        self.setAutoFillBackground(True)
        self.setWindowOpacity(0.1)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.offset = event.pos()
            self.x = self.offset.x
            self.y = self.offset.y
            
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

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setPen(QPen(Qt.green, 8, Qt.SolidLine))
        painter.drawEllipse(self.offset,40,40)
        return

    def self_close(self):
        self.close()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = FramelessWidget()
    win.setGeometry(300, 300, 300, 300)
    win.show()
    sys.exit(app.exec_())
