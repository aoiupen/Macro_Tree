import csv
import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

import pyautogui as pag
from openpyxl import load_workbook

import itertools
#id관리
class resource_cl():
    newid = itertools.count()
    def __init__(self):
        self.id = resource_cl.newid()

class TreeWidgetItem(QTreeWidgetItem):
    def __init__(self,parent,name=""):
        QTreeWidgetItem.__init__(self,parent)
        self.prnt = parent
        self.name = name
        self.setFlags(self.flags()|Qt.ItemIsEditable) #editable
        self.setCheckState(0,Qt.Checked)#col,state
        self.setExpanded(True)

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
        print(it, col, it.text(col))


class MyWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("window title")
        self.setGeometry(100,100,1300,700)
        self.ctr_wid = QWidget()
        self.ctr_lay = QHBoxLayout(self.ctr_wid)
        self.setCentralWidget(self.ctr_wid)
        
        self.tw = TreeWidget()
        self.tw.setColumnCount(5)
        self.tw.setHeaderLabels(["Name","Type","Act","Pos","Content"])
                
        self.ctr_lay.addWidget(self.tw)
        
        self.tw2 = TreeWidget()
        self.tw2.setColumnCount(2)
        self.tw2.setHeaderLabels(["Name","List"])
        val_1 = TreeWidgetItem(self.tw2)
        val_1.setText(0,"val_a")
        val_1.setText(1,"a,b,c,d,e,f,g,h,i,j,k")
        val_1.setFlags(val_1.flags()|Qt.ItemIsEditable) #editable
        
        val_2 = TreeWidgetItem(self.tw2)
        val_2.setText(0,"val_a")
        val_2.setText(1,"a,b,c,d,e,f,g,h,i,j,k")
        val_2.setFlags(val_2.flags()|Qt.ItemIsEditable) #editable
        
        val_3 = TreeWidgetItem(self.tw2)
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
                        writer.writerow(["top",top_it.text(0)])
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
        with open('ex.csv', 'rt') as f:
            reader = csv.reader(f)
            for row in reader:
                parent = ""

                parent_str = row[0]
                name = row[1]
                if parent_str == 'top':
                    parent = self.tw
                    tw_item = TreeWidgetItem(parent,parent_str)
                    tw_item.setText(0,name)
                else:
                    for inst in self.insts:
                        if inst.text(0) == parent_str:   
                            parent = inst                        
                            tw_item = TreeWidgetItem(parent,parent_str)
                            tw_item.setText(0,name)
                #parent에 string이 들어가면 안되고,이 이름을 가지는 widget을 불러와야한다
                
                if len(row) >2:
                    typ = row[2]
                    act = row[3]
                    pos = row[4]
                    content = row[5]

                    tw_item.setText(1,typ)
                    tw_item.setText(2,act)
                    tw_item.setText(3,pos)
                    tw_item.setText(4,content)    
                self.insts.append(tw_item)


                
if __name__ == "__main__":
    app = QApplication(sys.argv)
    main = MyWindow()
    main.show()
    app.exec_()