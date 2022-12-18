from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from package import tree as tr
from package import func as fn
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
        self.win.setWindowTitle("window title")
        self.win.setGeometry(100,100,1000,400)
        self.ctr_wid = QWidget()
        self.ctr_lay = QHBoxLayout(self.ctr_wid)
        self.win.setCentralWidget(self.ctr_wid)
    
    def setup_top(self,tw):
        #shortcut
        self.act_list = []
        self.act_info_list = [['Save','Ctrl+S','Save application',tw.save],
                         ['Load','Ctrl+O','Load application',tw.load],
                         ['Execute','','Execute application',tw.exec_inst],
                         ['Exit','Ctrl+Q','Exit application',tw.set_cls_win]]
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
            
    def setup_ui(self,MainWindow,app):
        # central widget, top menu
        self.setup_ctr(MainWindow,app)
        
        # tree
        col_num = 5
        self.tw = tr.TreeWidget(self)
        self.tw.setColumnCount(col_num)
        self.tw.setHeaderLabels(["Name","Type","Act","Pos","Content"])
        self.ctr_lay.addWidget(self.tw)
        
        self.setup_top(self.tw)
        
        # finish
        #self.win.adjustSize()
        self.tw.load()
        
    