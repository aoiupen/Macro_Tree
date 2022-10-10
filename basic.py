import csv
import sys
from types import NoneType
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import pandas as pd
from screeninfo import get_monitors
import pyautogui as pag
from openpyxl import load_workbook
import time

import itertools
#####icon log flexble
from requests import delete

class TreeWidgetItem(QTreeWidgetItem):
    def __init__(self,parent):
        QTreeWidgetItem.__init__(self,parent)
        self.setFlags(self.flags()|Qt.ItemIsEditable) #editable
        self.setFlags(self.flags() ^ Qt.ItemIsDropEnabled)
        self.setCheckState(0,Qt.Checked) #col,state
        self.setExpanded(True)
        self.a = None
        self.a = QComboBox()
        self.a.addItem("aa")
        self.a.addItem("bb")
        parent.setItemWidget(self,0,self.a)
class TreeWidget(QTreeWidget):
    def __init__(self,parent):
        super().__init__()
        self.win = parent
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        #self.dropEvent = self.treeDropEvent
        self.setEditTriggers(QAbstractItemView.DoubleClicked)
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)
        #self.setContextMenuPolicy(Qt.CustomContextMenu) #비활성화시키면 contextmenuevent 동작됨
        
        self.copy_buf = []
        self.log_lst = []
        self.log_str = ""
        self.undoStack = QUndoStack(self)
        self.undoStack.setIndex(0)
        self.cnt = 0
    def startDrag(self, supportedActions):
        drag = QDrag(self)
        mimedata = self.model().mimeData(self.selectedIndexes())
#
        #encoded = QByteArray()
        #stream = QDataStream(encoded, QIODevice.WriteOnly)
        #self.encodeData(self.selectedItems(), stream)
        #mimedata.setData(TreeWidget.customMimeType, encoded)
#
        #drag.setMimeData(mimedata)
        #drag.exec_(supportedActions)        
    def treeDropEvent(self, event):
        target = self.itemAt(event.pos())
        # 현 treewidget으로 drop
        root = self.invisibleRootItem()
        self.save_push_log()        
        if event.source() == self:
            modifiers = event.keyboardModifiers()   
            if event.mimeData().hasFormat(TreeWidget.customMimeType):
                encoded = event.mimeData().data(TreeWidget.customMimeType)
                items = self.decodeData(encoded, event.source())
                # problem : 복수 선택 후 복사할 때 child가 중복 복사되는 문제
                # solution : 선택된 것들의 이름 모으기, 부모 모으기
                # -> 내 부모의 이름이 이름안에 있으면 난 안됨
                # selected item에 col에 반영되지 않는 parent 정보가 있으면 편한데,
                # 지금은 우선 번거롭더라도 selected items에서 prnt_str으로 parent 이름을 받자
                prnt_lst = []
                for sel_item in self.selectedItems():
                    prnt_lst.append(sel_item.prnt_name)
                name_lst = []
                for item in items:
                    name_lst.append(item.text(0))
                main_lst = []
                for sel_item in self.selectedItems():
                    if sel_item.prnt_name not in name_lst:
                        main_lst.append(sel_item)    
            if modifiers == Qt.NoModifier:
                if target.typ_cbx == None:
                    for it in main_lst:
                        # QTree->TreeWidgetItem?
                        item = TreeWidgetItem(self,target)
                        self.fillItem(it, item)
                        self.fillItems(it, item)
                        (it.parent() or root).removeChild(it)
                    event.acceptProposedAction()
                    print("No Keyboard")
            elif modifiers == Qt.ControlModifier:
                # 받는 item이 inst가 아닐때만 가능
                if target.typ_cbx == None:
                    for it in main_lst:
                        # QTree->TreeWidgetItem?
                        item = TreeWidgetItem(self,target)
                        self.fillItem(it, item)
                        self.fillItems(it, item)
                    event.acceptProposedAction()
                    print("Control")
            elif modifiers == Qt.ShiftModifier:
                print("shift")
            #if (modifiers & Qt.ControlModifier) and (modifiers & Qt.ShiftModifier):
            #    print("Control+Shift")
        # 타 widget으로 drop     
        elif isinstance(event.source(), QTreeWidget):
            if event.mimeData().hasFormat(TreeWidget.customMimeType):
                encoded = event.mimeData().data(TreeWidget.customMimeType)
                items = self.decodeData(encoded, event.source())
                for it in items:
                    # QTree->TreeWidgetItem?
                    item = TreeWidgetItem(self,target)
                    self.fillItem(it, item)
                    self.fillItems(it, item)
                event.acceptProposedAction()    
class MyWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("window title")
        self.setGeometry(100,100,2000,700)
        self.ctr_wid = QWidget()
        self.ctr_lay = QHBoxLayout(self.ctr_wid)
        self.setCentralWidget(self.ctr_wid)
        self.tw = TreeWidget(self.ctr_wid)
        self.ctr_lay.addWidget(self.tw)
        self.tw.setDragEnabled(True)
        self.tw.setAcceptDrops(True)
        
        self.item1 = TreeWidgetItem(self.tw)
        self.item2 = TreeWidgetItem(self.tw)
        self.item1.setText(0,'1')
        self.item2.setText(0,'2')
        
if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = MyWindow()
    win.setGeometry(300, 300, 300, 300)
    win.show()
    sys.exit(app.exec_())
