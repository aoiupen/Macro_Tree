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

import itertools
#####icon log flexble
from requests import delete

#transfrom,flexible,pressed
#실행 코드 작성 -> UX 개선 + region, image 탐색 기능 추가
#group과 inst 앞에 서로 다른 아이콘
#group은 대문자 G
#inst는 문서그림
#Group으로 묶이거나, 하위
#content도 
#all 선택
#group해제는 우클릭해서 메뉴 팝업후 삭제 가능하도록
#getpos 영역 확대하기 + 멀티모니터 사용 고려
#image 검색을 사용할 경우 region 영역 버튼도 활성화하기 default는 전체영역

class Second(QWidget):
    def __init__(self,MainUi,btn):
        super().__init__()
        self.MainUi = MainUi
        self.setWindowTitle("Test")
        self.setWindowFlags(Qt.FramelessWindowHint)
        m = get_monitors()[0]
        self.resolution_width = m.width
        self.resolution_height = m.height
        self.label = QLabel("", self)
        self.offset = None
        self.quitSc1 = QShortcut(QKeySequence('ESC'), self)
        self.quitSc1.activated.connect(self.self_close)
        self.quitSc2 = QShortcut(QKeySequence('Ctrl+M'), self)
        self.quitSc2.activated.connect(self.set_maximize)
        self.quitSc3 = QShortcut(QKeySequence('Ctrl+S'), self)
        self.quitSc3.activated.connect(self.set_minimize)
        op = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(op)
        self.setAutoFillBackground(True)
        self.setWindowOpacity(0.3)
        self.set_maximize()
        self.offset = ""
        self.btn = btn
        
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
    
    def input_coor_to_btn(self,str):
        pass
    
    # pos -> treewidgetitem에 저장
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.offset = event.pos()
            x= str(self.offset.x())
            y= str(self.offset.y())
            coor = x + "," + y
            # treewidgetitem->poswidget->posbtn
            if isinstance(self.btn,PosBtn):
                self.btn.pos = coor
                self.btn.parent().pos_le.setText(coor)
                self.btn.setStyleSheet("color:black")               
                self.close()
            else:
                pos_pair = self.btn.pos_pair
                if len(pos_pair) == 2:
                    pos_pair = []
                pos_pair.append(coor)
                if len(pos_pair) == 2:
                    self.btn.setStyleSheet("color:black")
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

    # move to getpos.py later
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setPen(QPen(Qt.green, 8, Qt.SolidLine))
        # db.inst_dict
        painter.drawEllipse(40, 40, 40, 40)
        return

    def self_close(self):
        self.close()

#옮길때 pos coor 값 보존
class PosBtn(QPushButton):
    double_signal = pyqtSignal()
    def __init__(self,name):
        super().__init__()
        self.setText(name)
        self.clicked.connect(self.run)     
    def run(self):
        self.double_signal.emit()

class RegButton(QPushButton):
    def __init__(self,name):
        super().__init__()
        self.setText(name)
        self.pos_pair = []
        self.setFixedSize(QSize(50,20))
        self.setStyleSheet("color:red")
    
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
        #self.setStyleSheet("background-color: rgb(250,250,250);")

class TypCombo(QComboBox):
    typ_signal = pyqtSignal()
    def __init__(self,parent,typ):
        QComboBox.__init__(self)
        
        self.prnt = parent
        self.addItem("Mouse")
        self.addItem("Key")
        idx = lambda x : 0 if x == "Mouse" else 1
        self.setCurrentIndex(idx(typ))
        #self.setStyleSheet("background-color: rgb(250,250,250);")
        self.currentIndexChanged.connect(self.run)
        
    def run(self):
        self.typ_signal.emit()
        
class PosWidget(QWidget):
    pos_signal = pyqtSignal()
    def __init__(self,pos):
        QWidget.__init__(self)
        self.minimumSize().height()
        self.widget_lay = QHBoxLayout(self)
        self.widget_lay.setContentsMargins(0,0,0,0)
        self.widget_lay.setSpacing(0)
        self.pos_le = QLineEdit(pos,self)
        self.pos_le.setFixedWidth(80)
        self.pos_btn = PosBtn("pos")
        self.pos_btn.setFixedWidth(50)
        self.widget_lay.addWidget(self.pos_le)
        self.widget_lay.addWidget(self.pos_btn)
        self.pos_btn.clicked.connect(self.run)
        
    def run(self):
        self.pos_signal.emit()
                
    def get_pos(self):
        self.second = Second(self,self.pos_btn)
        self.second.show()
        
class resource_cl():
    newid = itertools.count()
    def __init__(self):
        self.id = resource_cl.newid()

class TreeWidgetItem(QTreeWidgetItem):
    def __init__(self,tw,parent,row=""):
        self.tw = tw
        self.row = row
        QTreeWidgetItem.__init__(self,parent)
        self.prnt = parent
        self.act_cbx = None
        self.typ_cbx = None

        if len(self.row)>2:#우측 treewidget 없앨 때 같이 지울 조건
            if self.row[2]:
                typ = self.row[2]
                self.typ_cbx = TypCombo(self,typ)
                self.tw.setItemWidget(self, 1, self.typ_cbx)
                #row[2]가 있으면 row[3]도 있으므로 if문 생략
                act = self.row[3]
                self.act_cbx = ActCombo(typ,act)
                self.tw.setItemWidget(self, 2, self.act_cbx)
                self.typ_cbx.typ_signal.connect(lambda:self.change_act(self.typ_cbx,self.act_cbx))
                pos = self.row[4]
                if self.row[2] == "Mouse":
                    self.pos_wdg = PosWidget(pos)
                    self.pos_wdg.pos_btn.clicked.connect(lambda ignore,f=self.pos_wdg.get_pos:f())
                    self.tw.setItemWidget(self, 3, self.pos_wdg)

        self.setFlags(self.flags()|Qt.ItemIsEditable) #editable
        self.setCheckState(0,Qt.Checked) #col,state
        self.setExpanded(True)
    #group을 지웠을 때 child가 윗계층으로 올라가기
     
    #signal의 class가 qobject를 상속할 때만 @pyqtSlot()을 달아주고, 아니면 달지 않는다
    #https://stackoverflow.com/questions/40325953/why-do-i-need-to-decorate-connected-slots-with-pyqtslot/40330912#40330912       
    def change_act(self,typ_cbx,act_cbx):
        #typ_cbx를 self.typ_cbx로 바꾸고 param 지우기
        self.tw.disconnect()
        if typ_cbx.currentText() == "Mouse":
            act_cbx.clear()
            act_cbx.addItem("Click")
            act_cbx.addItem("Double")
            act_cbx.addItem("Right")
            act_cbx.setCurrentIndex(0)
            self.setText(1,"Mouse")
            self.setText(2,"Click")
            self.pos_wdg = PosWidget("0,0")
            self.pos_wdg.pos_btn.clicked.connect(lambda ignore,f=self.pos_wdg.get_pos:f())
            self.tw.setItemWidget(self,3,self.pos_wdg) # typ을 mouse로 변경시 - pos 연동 생성
        elif typ_cbx.currentText() == "Key":
            act_cbx.clear()
            act_cbx.addItem("Copy")
            act_cbx.addItem("Paste")
            act_cbx.addItem("Delete")
            self.setText(1,"Key")
            self.setText(2,"Copy")
            act_cbx.setCurrentIndex(0)
            self.tw.removeItemWidget(self,3)
        ctr_widget = self.tw.parent()
        wid = ctr_widget.parent()
        self.tw.itemChanged.connect(wid.get_item) # typ을 key로 변경시 - pos 연동 삭제
#https://stackoverflow.com/questions/25559221/qtreewidgetitem-issue-items-set-using-setwidgetitem-are-dispearring-after-movin        
class TreeWidget(QTreeWidget):
    customMimeType = "application/x-customTreeWidgetdata"
    def __init__(self):
        super().__init__()
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.dropEvent = self.treeDropEvent
        self.setEditTriggers(QAbstractItemView.DoubleClicked)
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)
        #self.setContextMenuPolicy(Qt.CustomContextMenu) #비활성화시키면 contextmenuevent 동작됨
        self.customContextMenuRequested.connect(self.context_menu)

    def contextMenuEvent(self,event):
        self.menu = QMenu(self)
        delete_act = QAction('Delete',self)
        delete_act.triggered.connect(lambda:self.recur_delete(event))
        ungroup_act = QAction('Ungroup',self)
        ungroup_act.triggered.connect(lambda:self.ungrouping(event))
        self.menu.addAction(delete_act)
        self.menu.addAction(ungroup_act)
        self.menu.popup(QCursor.pos())
        
    # 나중에 sip 시도해보기
    def recur_delete(self,event):
        root = self.invisibleRootItem()
        for item in self.selectedItems():
            (item.parent() or root).removeChild(item)
    
    # cur의 child의 parent를 cur->cur.parent()로 바꾸기
    # cur의 ix와 parent를 뽑기
    # child_without_parent를 parent.addChild로 더하기
    # ungrouping 할 때 맨 위 or 아래로 내려가고, widget 풀리는 현상 발생
    def ungrouping(self,event):
        root = self.invisibleRootItem()
        for item in self.selectedItems():
            if isinstance(item.typ_cbx,NoneType):
                new_parent = item.parent()
                child_cnt = item.childCount()
                if child_cnt:
                    for idx in range(child_cnt):
                        item_without_parent = item.takeChild(idx)
                        #top일 때 nonetype이라 insertchild 안됨
                        #child를 top으로 만들어줘야함. 복잡하네...
                        if isinstance(item.parent(),NoneType):
                            ix = self.indexOfTopLevelItem(item)
                            self.insertTopLevelItem(ix,item_without_parent)
                            #item이 toplevel 몇번째인지
                        else:
                            item.parent().insertChild(idx,item_without_parent)

                        #root에 더할 때 index를 고려해서 넣기
                (item.parent() or root).removeChild(item)
            
    # custom일경우(나중에 공부). 옆에는 적용되던데 왜지...
    def context_menu(self, pos):
        index = self.indexAt(pos)
        
        if not index.isValid():
            return

        item = self.itemAt(pos)
        name = item.text(0)

        menu = QMenu()
        #quitAction = menu.addAction("Quit")
        #action = menu.exec_(self.mapToGlobal(pos))
        #if action == quitAction:
        #    qApp.quit()
        action = menu.addAction("action")
        action = menu.addAction(name)
        menu.addSeparator()
        action_1 = menu.addAction("Choix 1") # 뒤에 함수 param
        action_2 = menu.addAction("Choix 2")
        menu.addSeparator()
        action_3 = menu.addAction("Choix 3")
        menu.exec_(self.mapToGlobal(pos))
    
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

    def move_itemwidget(self,tw,event,drag_item):
        self.tw = tw
        event.setDropAction(Qt.MoveAction)
        QTreeWidget.dropEvent(self, event)
        # *drop event로 Data를 먼저 옮기고, if문 이하에서 item setting
        if drag_item.text(1):
            drag_item.typ_cbx = TypCombo(self,drag_item.text(1))
            drag_item.act_cbx = ActCombo(drag_item.text(1),drag_item.text(2))
            self.setItemWidget(drag_item, 1, drag_item.typ_cbx)
            self.setItemWidget(drag_item, 2, drag_item.act_cbx)
            if drag_item.text(1) == "Mouse":
                coor = drag_item.pos_wdg.pos_le.text()
                drag_item.pos_wdg = PosWidget(coor)
                # 이동해도, item을 새로 만드는 것이기 때문에, connect도 다시 해줘야한다.
                # 추후 class init할 때 connect 하도록 수정할 필요있음
                drag_item.pos_wdg.pos_btn.clicked.connect(lambda ignore,f=drag_item.pos_wdg.get_pos:f())                  
                self.setItemWidget(drag_item, 3, drag_item.pos_wdg)
            drag_item.typ_cbx.typ_signal.connect(lambda:drag_item.change_act(drag_item.typ_cbx,drag_item.act_cbx))
            child_cnt = drag_item.childCount()
            if child_cnt:
                for idx in range(child_cnt):
                    child = drag_item.child(idx)
                    #event를 param으로 넘겨도 되는지
                    self.tw.move_itemwidget(self.tw,event,child)
            
    #group간 종속기능 추가해야함
    #pos 따라가도록
    def treeDropEvent(self, event):
        # 현 treewidget으로 drop
        if event.source() == self:
            drag_item = self.currentItem()
            if drag_item.text(1):
                self.move_itemwidget(self,event,drag_item)
                #child도 같은 처리해줘야함
            
        # 타 widget으로 drop     
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
                            
    # 순수 recur만 분리하기. 지금은 write와 섞여있음   
    def recur_child(self,writer,parent):
        if parent.childCount():
            #써주는 상황 : top은 써주고 recursive, 막내는 recursive 마지막에, 중간은 써줄 기회가 없다
            #그러므로 top은 예외고, 중간과 막내는 써주는 상황을 통일시켜야 한다
            #recursive 가기 전에 해주는게 맞아 보인다
            for ch_num in range(parent.childCount()):
                ch_item = parent.child(ch_num)
                lst = [ch_item.text(i) for i in range(self.tw.columnCount())]
                if ch_item.text(1) == "Mouse":
                    lst[3] = ch_item.pos_wdg.pos_le.text()
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
                    tw_item.setText(3,pos)
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