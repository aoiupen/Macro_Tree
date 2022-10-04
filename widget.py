import csv
import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import pandas as pd

import pyautogui as pag
from openpyxl import load_workbook

import itertools

from requests import delete
#to do
#typcombo 변경시 checkbox 풀리는 문제, pyqtslot으로 해결해보기
#pos를 lineedit->button으로 : 더블클릭시 변경, 클릭시 getpos
#content도 
#all 선택

class PosBtn(QPushButton):
    double_signal = pyqtSignal()
    def __init__(self):
        super().__init__()
        self.clicked.connect(self.run)
        
    def run(self):
        self.double_signal.emit()
    
class ActCombo(QComboBox):
    def __init__(self,typ,act):
        QComboBox.__init__(self)
        if typ == "Mouse":
            self.addItem("Click")
            self.addItem("Double")
            self.addItem("Right")
            if act == "Click":
                self.setCurrentIndex(0)
            elif act == "Double":
                self.setCurrentIndex(1)
            else:
                self.setCurrentIndex(2)
        elif typ == "Key":
            self.addItem("Copy")
            self.addItem("Paste")
            self.addItem("Delete")
            if act == "Copy":
                self.setCurrentIndex(0)
            elif act == "Paste":
                self.setCurrentIndex(1)
            else:
                self.setCurrentIndex(2)    
        self.setStyleSheet("background-color: rgb(250,250,250);")

class TypCombo(QComboBox):
    typ_signal = pyqtSignal()
    def __init__(self,parent,typ):
        QComboBox.__init__(self)
        
        self.prnt = parent
        self.addItem("Mouse")
        self.addItem("Key")
        idx = lambda x : 0 if x == "Mouse" else 1
        self.setCurrentIndex(idx(typ))
        self.setStyleSheet("background-color: rgb(250,250,250);")
        self.currentIndexChanged.connect(self.run)
        
    def run(self):
        self.typ_signal.emit()
    
class resource_cl():
    newid = itertools.count()
    def __init__(self):
        self.id = resource_cl.newid()

class TreeWidgetItem(QTreeWidgetItem):
    def __init__(self,tw,parent,row=""):
        self.tw = tw
        QTreeWidgetItem.__init__(self,parent)
        self.prnt = parent
        if len(row)>2:#우측 treewidget 없앨 때 같이 지울 조건
            if row[2]:
                typ = row[2]
                self.typ_cbx = TypCombo(self,typ)
                self.tw.setItemWidget(self, 1, self.typ_cbx)
                #row[2]가 있으면 row[3]도 있으므로 if문 생략
                act = row[3]
                self.act_cbx = ActCombo(typ,act)
                self.tw.setItemWidget(self, 2, self.act_cbx)
                self.typ_cbx.typ_signal.connect(lambda:self.change_act(self.typ_cbx,self.act_cbx))
                pos = row[4]
                
                if row[2] == "Mouse":
                    self.widget = QWidget()
                    self.widget.minimumSize().height()
                    self.widget_lay = QHBoxLayout(self.widget)
                    self.widget_lay.setContentsMargins(0,0,0,0)
                    self.widget_lay.setSpacing(0)
                    self.pos_le = QLineEdit(pos)
                    self.pos_le.setFixedWidth(80)
                    self.pos_btn = QPushButton("pos")
                    self.pos_btn.setFixedWidth(50)
                    self.widget_lay.addWidget(self.pos_le)
                    self.widget_lay.addWidget(self.pos_btn)
                    self.tw.setItemWidget(self, 3, self.widget)
                    
        self.setFlags(self.flags()|Qt.ItemIsEditable) #editable
        self.setCheckState(0,Qt.Checked)#col,state
        self.setExpanded(True)
     
    #signal의 class가 qobject를 상속할 때만 @pyqtSlot()을 달아주고, 아니면 달지 않는다
    #https://stackoverflow.com/questions/40325953/why-do-i-need-to-decorate-connected-slots-with-pyqtslot/40330912#40330912       
    def change_act(self,typ_cbx,act_cbx):
        self.tw.disconnect()
        if typ_cbx.currentText() == "Mouse":
            act_cbx.clear()
            act_cbx.addItem("Click")
            act_cbx.addItem("Double")
            act_cbx.addItem("Right")
            act_cbx.setCurrentIndex(0)
            self.setText(1,"Mouse")
            self.setText(2,"Click")
        elif typ_cbx.currentText() == "Key":
            act_cbx.clear()
            act_cbx.addItem("Copy")
            act_cbx.addItem("Paste")
            act_cbx.addItem("Delete")
            self.setText(1,"Key")
            self.setText(2,"Copy")
            act_cbx.setCurrentIndex(0)
        ctr_widget = self.tw.parent()
        wid = ctr_widget.parent()
        self.tw.itemChanged.connect(wid.get_item)
        
class TreeWidget(QTreeWidget):
    customMimeType = "application/x-customTreeWidgetdata"
    def __init__(self):
        super().__init__()
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.setEditTriggers(QAbstractItemView.DoubleClicked)
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)

        #self.itemClicked.connect(self.onItemClicked)
    
    def mimeTypes(self):
        mimetypes = QTreeWidget.mimeTypes(self)
        mimetypes.append(TreeWidget.customMimeType)
        return mimetypes

    def startDrag(self, supportedActions):
        drag = QDrag(self)
        mimedata = self.model().mimeData(self.selectedIndexes())

        encoded = QByteArray()
        stream = QDataStream(encoded, QIODevice.WriteOnly)
        self.encodeData(self.selectedItems(), stream)
        mimedata.setData(TreeWidget.customMimeType, encoded)

        drag.setMimeData(mimedata)
        drag.exec_(supportedActions)

    def dropEvent(self, event):
        if event.source() == self:
            event.setDropAction(Qt.MoveAction)
            QTreeWidget.dropEvent(self, event)
        elif isinstance(event.source(), QTreeWidget):
            if event.mimeData().hasFormat(TreeWidget.customMimeType):
                encoded = event.mimeData().data(TreeWidget.customMimeType)
                parent = self.itemAt(event.pos())
                items = self.decodeData(encoded, event.source())
                for it in items:
                    #QTree->TreeWidgetItem?
                    item = QTreeWidgetItem(parent)
                    self.fillItem(it, item)
                    self.fillItems(it, item)
                event.acceptProposedAction()

    def fillItem(self, inItem, outItem):
        for col in range(inItem.columnCount()):
            for key in range(Qt.UserRole):
                role = Qt.ItemDataRole(key)
                outItem.setData(col, role, inItem.data(col, role))

    def fillItems(self, itFrom, itTo):
        for ix in range(itFrom.childCount()):
            it = QTreeWidgetItem(itTo)
            ch = itFrom.child(ix)
            self.fillItem(ch, it)
            self.fillItems(ch, it)

    def encodeData(self, items, stream):
        stream.writeInt32(len(items))
        for item in items:
            p = item
            rows = []
            while p is not None:
                rows.append(self.indexFromItem(p).row())
                p = p.parent()
            stream.writeInt32(len(rows))
            for row in reversed(rows):
                stream.writeInt32(row)
        return stream

    def decodeData(self, encoded, tree):
        items = []
        rows = []
        stream = QDataStream(encoded, QIODevice.ReadOnly)
        while not stream.atEnd():
            nItems = stream.readInt32()
            for i in range(nItems):
                path = stream.readInt32()
                row = []
                for j in range(path):
                    row.append(stream.readInt32())
                rows.append(row)

        for row in rows:
            it = tree.topLevelItem(row[0])
            for ix in row[1:]:
                it = it.child(ix)
            items.append(it)
        return items

    @pyqtSlot(TreeWidgetItem, int)
    def onItemClicked(self, it, col):
        pass
        #print(it, col, it.text(col))
    
class MyWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("window title")
        self.setGeometry(100,100,2000,700)
        self.ctr_wid = QWidget()
        self.ctr_lay = QHBoxLayout(self.ctr_wid)
        self.setCentralWidget(self.ctr_wid)
        
        saveAction = QAction('Save', self)
        saveAction.setShortcut('Ctrl+S')
        saveAction.setStatusTip('Save application')
        loadAction = QAction('Load', self)
        loadAction.setShortcut('Ctrl+O')
        loadAction.setStatusTip('Load application')
        exitAction = QAction('Exit', self)
        exitAction.setShortcut('Ctrl+Q')
        exitAction.setStatusTip('Exit application')

        menubar = self.menuBar()
        menubar.setNativeMenuBar(False)
        filemenu = menubar.addMenu('&File')
        filemenu.addAction(loadAction)
        filemenu.addAction(saveAction)
        filemenu.addAction(exitAction)
        
        loadAction.triggered.connect(self.load)
        saveAction.triggered.connect(self.save)
        exitAction.triggered.connect(self.self_close)
        
        self.tw = TreeWidget()
        self.tw.setColumnCount(5)
        self.tw.setHeaderLabels(["Name","Type","Act","Pos","Content"])
                
        self.ctr_lay.addWidget(self.tw)
    
        self.tw2 = TreeWidget()
        self.tw2.setColumnCount(2)
        self.tw2.setHeaderLabels(["Name","List"])
        val_1 = TreeWidgetItem(self.tw2,self.tw2)
        val_1.setText(0,"val_a")
        val_1.setText(1,"a,b,c,d,e,f,g,h,i,j,k")
        val_1.setFlags(val_1.flags()|Qt.ItemIsEditable) #editable
        
        val_2 = TreeWidgetItem(self.tw2,self.tw2)
        val_2.setText(0,"val_a")
        val_2.setText(1,"a,b,c,d,e,f,g,h,i,j,k")
        val_2.setFlags(val_2.flags()|Qt.ItemIsEditable) #editable
        
        val_3 = TreeWidgetItem(self.tw2,self.tw2)
        val_3.setText(0,"val_a")
        val_3.setText(1,"a,b,c,d,e,f,g,h,i,j,k")
        val_3.setFlags(val_3.flags()|Qt.ItemIsEditable) #editable

        self.tw.header().setStretchLastSection(True)
        self.tw.header().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.tw2.header().setStretchLastSection(True)
        self.tw2.header().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.ctr_lay.addWidget(self.tw2)
        self.adjustSize()
        
        #with open('ex.csv', 'rt') as f:
        #        reader = csv.reader(f)
        #        for row in reader:
        #            item = TreeWidgetItem(row)#부모설정.결국
        self.insts = []
        self.load()
        self.tw.itemChanged.connect(self.get_item)
       
    def check_child(self,cur,col):
        if col == 0:
            ch_num = cur.childCount()
            if ch_num:
                for num in range(ch_num):
                    cur.child(num).setCheckState(0, Qt.Checked)
                    self.check_child(cur.child(num),col)
                    
    def uncheck_child(self,cur,col):
        if col == 0:
            ch_num = cur.childCount()
            if ch_num:
                for num in range(ch_num):
                    cur.child(num).setCheckState(0, Qt.Unchecked)
                    self.uncheck_child(cur.child(num),col)

    def uncheck_parent(self,cur,col):
        if cur.parent():
            cur.parent().setCheckState(0, Qt.Unchecked)
            self.uncheck_parent(cur.parent(),col)
    
    def check_parent(self,cur,col):
        # 나와 동료가 full check -> 부모도 check
        parent = cur.parent()
        sbl_true = True
        if parent:
            sbl_num = parent.childCount()
            if sbl_num:
                for num in range(sbl_num):
                    if parent.child(num).checkState(col) == Qt.Unchecked: #col을 적어줘야함
                        sbl_true = False
                        break
            if sbl_true:
                parent.setCheckState(0, Qt.Checked)
                self.check_parent(parent,col)
    
    def get_item(self,cur,col):
        if cur.checkState(col) == Qt.Checked:
            self.check_child(cur,col) # 자식 전체 check
            self.check_parent(cur,col) # 동료 full check-> 부모 check                                  
        else:
            self.uncheck_child(cur,col) # 자식 전체 uncheck
            self.tw.blockSignals(True) # itemChanged 시그널 발생 막기
            self.uncheck_parent(cur,col) # 부모 전체 uncheck until
            self.tw.blockSignals(False)
            
    def save(self):
        with open('ex.csv', 'wt') as csvfile:
            col_cnt = self.tw.columnCount()
            header =  [self.tw.headerItem().text(col)
                      for col in range(col_cnt)]
            writer = csv.writer(
                    csvfile, dialect='excel', lineterminator='\n')
            #writer.writerow(header)
            top_cnt = self.tw.topLevelItemCount()
            if top_cnt:
                for i in range(top_cnt):
                    top_it = self.tw.topLevelItem(i)
                    if top_it:
                        writer.writerow(["top",top_it.text(0),"","","",""])
                        if top_it.childCount():
                            self.recur_child(writer,top_it)
        
    def recur_child(self,writer,parent):
        if parent.childCount():
            #써주는 상황 : top은 써주고 recursive, 막내는 recursive 마지막에, 중간은 써줄 기회가 없다
            #그러므로 top은 예외고, 중간과 막내는 써주는 상황을 통일시켜야 한다
            #recursive 가기 전에 해주는게 맞아 보인다
            for ch_num in range(parent.childCount()):
                lst = [parent.child(ch_num).text(i) for i in range(self.tw.columnCount())]
                lst.insert(0,parent.text(0))     
                writer.writerow(lst)
                self.recur_child(writer,parent.child(ch_num))
        return
         
    def load(self):
        self.tw.disconnect()
        self.tw.clear()
        with open('ex.csv', 'rt') as f:
            reader = csv.reader(f)
            self.insts=[]
            for idx,row in enumerate(reader):
                parent = ""

                parent_str = row[0]
                name = row[1]
                if parent_str == 'top':
                    parent = self.tw
                    tw_item = TreeWidgetItem(self.tw,parent,row)
                    tw_item.setText(0,name)
                else:
                    for inst in self.insts:
                        if inst.text(0) == parent_str:   
                            parent = inst                        
                            tw_item = TreeWidgetItem(self.tw,parent,row)
                            tw_item.setText(0,name)
                            break
                    
                #parent에 string이 들어가면 안되고,이 이름을 가지는 widget을 불러와야한다
                #column에 widget이 들어가면 이 코드가 의미가 없을 듯
                if len(row) >2:
                    typ = row[2]
                    act = row[3]
                    pos = row[4]
                    content = row[5]
                    tw_item.setText(1,typ)
                    tw_item.setText(2,act)
                    #tw_item.setText(3,pos)
                    tw_item.setText(4,content)    
                self.insts.append(tw_item)
        self.tw.itemChanged.connect(self.get_item)

    def self_close(self):
        self.close() 

                
if __name__ == "__main__":
    app = QApplication(sys.argv)
    main = MyWindow()
    main.show()
    app.exec_()