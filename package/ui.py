from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from package import tree as tr
from enum import Enum
from resources import *

class UI():
    def __init__(self,win,app):
        super().__init__()
        self.col_n = 5
        self.col_w = 10

        self.setup_win(win,app)
        self.setup_tree()
        self.setup_menubar(self.tw)
        self.tw.load_log_from_csv()
        
    def setup_win(self,win,app):
        self.app = app
        self.win = win
        self.win.setWindowTitle("Macro")
        self.win.setGeometry(*rsc["win_geo"])
        self.ctr_wid = QWidget()
        self.ctr_lay = QHBoxLayout(self.ctr_wid)
        self.win.setCentralWidget(self.ctr_wid)

    def setup_tree(self):
        self.tw = tr.TreeWidget(self)
        self.tw.setColumnCount(self.col_n)
        self.tw.setHeaderLabels(rsc["header"])
        self.tw.setColumnWidth(1,self.col_w)
        self.ctr_lay.addWidget(self.tw)

    def setup_menubar(self,tw):
        # menubar
        self.menubar = self.win.menuBar()
        self.menubar.setNativeMenuBar(False)
        
        # menubar_file(act)
        self.menubar_file = self.menubar.addMenu('&File')
        name_list = ["Save","Load","Execute","Exit"]
        shcut_list = ['Ctrl+S','Ctrl+L','Ctrl+E','Ctrl+Q']
        func_list = [tw.save,tw.load_log_from_csv,tw.exec_inst,qApp.quit]
        
        for ix in range(len(name_list)):
            act = QAction(name_list[ix],self.win)
            act.setShortcut(shcut_list[ix])
            act.triggered.connect(func_list[ix])
            self.menubar_file.addAction(act)