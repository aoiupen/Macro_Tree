from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from package import tree as tr
from enum import Enum

class UI():
    def __init__(self,Mainwindow,app):
        super().__init__()
        self.setup_win(Mainwindow,app)
        self.setup_ctr()
        self.setup_tree()
        self.setup_menubar(self.tw)
        self.tw.load()
        
    def setup_win(self,Mainwindow,app):
        self.app = app
        self.win = Mainwindow
        self.win.setWindowTitle("Macro") # ui_prefer 1
        self.win.setGeometry(100,100,500,400) # ui_prefer 2

    def setup_ctr(self):
        self.ctr_wid = QWidget()
        self.ctr_lay = QHBoxLayout(self.ctr_wid)
        self.win.setCentralWidget(self.ctr_wid)
    
    def setup_tree(self):
        col_num = 5 # ui_prefer 3
        self.tw = tr.TreeWidget(self)
        self.tw.setColumnCount(col_num)
        self.tw.setHeaderLabels(["Name","M/K","Value","Act",""]) # ui_prefer 4
        self.tw.setColumnWidth(1,10) # ui_prefer 5
        self.ctr_lay.addWidget(self.tw)

    def setup_menubar(self,tw):
        # menubar
        self.menubar = self.win.menuBar()
        self.menubar.setNativeMenuBar(False)       
        
        # file_act
        self.file_act_info_list = [['Save','Ctrl+S',tw.save],
                         ['Load','Ctrl+L',tw.load],
                         ['Execute','Ctrl+E',tw.exec_inst],
                         ['Exit','Ctrl+Q',qApp.quit]]
        
        self.menubar_file = self.menubar.addMenu('&File')
        for file_act_info in self.file_act_info_list:
            file_act = QAction(file_act_info[0],self.win)
            file_act.setShortcut(file_act_info[1])
            file_act.triggered.connect(file_act_info[2])
            self.menubar_file.addAction(file_act)