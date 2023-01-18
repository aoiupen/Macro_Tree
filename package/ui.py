from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from package import tree as tr
import itertools
from enum import Enum
        
class ShortC(Enum):
    name = 0
    key = 1
    tip = 2
    func = 3

class UI():
    def __init__(self):
        super().__init__()
    
    def setup_ctr(self,MainWindow,app):
        self.app = app
        self.win = MainWindow
        self.win.setWindowTitle("Macro")
        self.win.setGeometry(100,100,500,400)
        self.ctr_wid = QWidget()
        self.ctr_lay = QHBoxLayout(self.ctr_wid)
        self.win.setCentralWidget(self.ctr_wid)
        self.dark = DarkTheme(self.app)
    
    def setup_top(self,tw):
        #shortcut
        self.act_list = []
        self.act_info_list = [['Save','Ctrl+S','Save application',tw.save],
                         ['Load','Ctrl+O','Load application',tw.load],
                         #['Execute','','Execute application',tw.exec_inst],
                         ['Exit','Ctrl+Q','Exit application',qApp.quit],
                         ['Dark','Ctrl+D','Dark Theme',lambda:self.change_them(self.dark,self.app)]]
        for act_info in self.act_info_list:
            act = QAction(act_info[ShortC.name.value],self.win)
            act.setShortcut(act_info[ShortC.key.value])
            act.setStatusTip(act_info[ShortC.tip.value])
            act.triggered.connect(act_info[ShortC.func.value])
            self.act_list.append(act)
        
        # menubar
        self.menubar = self.win.menuBar()
        self.menubar.setNativeMenuBar(False)       
    
        # filemenu
        self.filemenu = self.menubar.addMenu('&File')
        for act in self.act_list:
            self.filemenu.addAction(act)
    
    def change_them(self,dark,app):
        if dark.is_dark:
            app.setPalette(app.style().standardPalette())
            dark.is_dark = 0
        else:
            app.setPalette(dark.palette)
            dark.is_dark = 1
            
    def setup_ui(self,MainWindow,app):
        # central widget, top menu
        self.setup_ctr(MainWindow,app)
        
        # tree
        col_num = 5
        self.tw = tr.TreeWidget(self)
        self.tw.setColumnCount(col_num)
        self.tw.setHeaderLabels(["Name","Type","Act","Value",""])
        self.tw.setColumnWidth(1,10)
        self.ctr_lay.addWidget(self.tw)
        
        self.setup_top(self.tw)
        
        # finish
        #self.win.adjustSize()
        self.tw.load()
        
def change_them(dark,app):
    if dark.is_dark:
        app.setPalette(app.style().standardPalette())
        dark.is_dark = 0
    else:
        app.setPalette(dark.palette)
        dark.is_dark = 1
        
class DarkTheme(QObject):
    def __init__(self,app):
        QObject.__init__(self)
        self.is_dark = 0
        self.palette = QPalette()
        self.palette.setColor(QPalette.Window, QColor(53, 53, 53))
        self.palette.setColor(QPalette.WindowText, Qt.white)
        self.palette.setColor(QPalette.Base, QColor(25, 25, 25))
        self.palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
        self.palette.setColor(QPalette.ToolTipBase, Qt.white)
        self.palette.setColor(QPalette.ToolTipText, Qt.white)
        self.palette.setColor(QPalette.Text, Qt.white)
        self.palette.setColor(QPalette.Button, QColor(53, 53, 53))
        self.palette.setColor(QPalette.ButtonText, Qt.white)
        self.palette.setColor(QPalette.BrightText, Qt.red)
        self.palette.setColor(QPalette.Link, QColor(42, 130, 218))
        self.palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
        self.palette.setColor(QPalette.HighlightedText, Qt.black)
    