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

# 기획 의도 : 프로그램 자체에 보안 관련 사항을 담지 않고,
# 구체적 내용은 사용자가 커스터마이징하게 하며,
# 특정 PC 환경에 종속되지 않아 범용 보급이 가능한 프로그램 개발
# 기술 : Customizing을 통한 Pyqt 이해도

# 기획
# 실행하면 최소화. 끝나면 최대화 (옵션화)
# 컨셉 : transfrom,flexible,pressed
# Tree : all 선택
# Tree : inst 추가 삭제
# Tree : lock 기능 : locked 되면 실행시 돌지 않는다(일종의 주석처리)
# Tree : group과 inst 앞에 서로 다른 아이콘, group은 대문자 G, inst는 문서그림
# Tree : 한단계 올릴 때 맨 아래로 내려가는 문제, 최상위 단계로 올릴 시 순서가 root 밑으로 쌓이는 문제
# Tree : top으로 올리는 기능 *** 최상위에 Root 폴더를 놓아야하나
# Tree-Grouping : 위계 문제. 체크박스처럼. 폴더+child일부 선택해도 폴더는 선택 안되도록
# Tree-Groupring : 우클릭 context에 복수 선택 후 group 기능 추가
# Tree-Groupring : 그룹 or inst 우클릭 -> 실행 # 그룹 + 그룹에속한 inst인 경우의 조건필요함
# Ux : image 검색을 사용할 경우 region 영역 버튼도 활성화하기 default는 전체영역
# Second : getpos 영역 확대하기 + 멀티모니터 사용 고려
# Strategy : 실행 코드 작성 -> UX 개선 + region, image 탐색 기능 추가
# Simulation : 시뮬레이션 기능 : pos를 클릭할 때 스크린샷도 같이
# mimedata encode, decode 할 지, selected items로 할지. 그리고 cbx를 새로 만들어줄지, deepcopy 할지
# content 뒤에 sleep(delay) 넣기
# 선택한 것만 우측 메뉴로 execute하기
# pos 와 lineedit 통합

# 진행
# Tree : ctrl 누른 상태에서는 선택된 아이템을 재클릭 후 release할 때 선택해제되도록 
# Tree : 그룹을 한단계 위로 이동시 그룹은 이동 안되고, inst는 top 바로 아래 depth2까지만 가능
# Tree : Content 적용하기
# Tree : Image로 pos 찾기 : Image 등록된 경우 Image라는 폰트가 노란 2겹테두리, 글씨 검정색으로 바뀜
# Tree : Root 폴더는 건드리지 않기
# Tree : Grouping

# 완료
# Tree-Ungrouping : top을 ungroup할때 or ungroup 후 top으로 올라갈 때 widget 풀림
# Func-Ctrl+Z : 매 동작마다 logsave를 해서 리스트 변수에 저장, 끝에 도달하면, undo 비활성화 redo 마찬가지
# Tree : Copy,Paste by 키보드 : 다중선택이면 마지막으로 선택된 Item의 현재 경로에 복제
# Tree : 다중선택 후 delete
# Tree : Check된 inst만 실행
# Acting : Move 기능
# Tree,Acting : Drag 기능
# Tree : Ctrl+left click시 복사 붙여넣기 되도록 + 여러개 선택시 모두 복사 되기

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
    act_signal = pyqtSignal()
    def __init__(self,typ,act):
        QComboBox.__init__(self)
        if typ == "Mouse":
            self.addItem("Click")
            self.addItem("Double")
            self.addItem("Right")
            self.addItem("Drag")
            self.addItem("Move")
            if act == "Click":
                self.setCurrentIndex(0)
            elif act == "Double":
                self.setCurrentIndex(1)
            elif act == "Right":
                self.setCurrentIndex(2)
            elif act == "Drag":
                self.setCurrentIndex(3)
            else:
                self.setCurrentIndex(4)
        elif typ == "Key":
            self.addItem("Copy")
            self.addItem("Paste")
            self.addItem("Select All")
            if act == "Copy":
                self.setCurrentIndex(0)
            elif act == "Paste":
                self.setCurrentIndex(1)
            else:
                self.setCurrentIndex(2)    
        #self.setStyleSheet("background-color: rgb(250,250,250);")
        self.currentIndexChanged.connect(self.run)
        
    def run(self):
        self.act_signal.emit()

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
        QTreeWidgetItem.__init__(self,parent)
        self.tw = tw
        self.row = row
        self.prnt = parent
        self.prnt_name = ""
        self.act_cbx = None
        self.typ_cbx = None
        self.pos_wdg = None

        if len(self.row)>2: # 우측 treewidget 없앨 때 같이 지울 조건
            if self.row[2]:
                #~ ^ 차이
                self.setFlags(self.flags() ^ Qt.ItemIsDropEnabled) #inst에는 inst를 drop할 수 없음
                typ = self.row[2]
                self.typ_cbx = TypCombo(self,typ)
                self.tw.setItemWidget(self, 1, self.typ_cbx)
                #row[2]가 있으면 row[3]도 있으므로 if문 생략
                act = self.row[3]
                self.act_cbx = ActCombo(typ,act)
                self.tw.setItemWidget(self, 2, self.act_cbx)
                self.typ_cbx.typ_signal.connect(lambda:self.change_typ(self.typ_cbx,self.act_cbx))
                self.act_cbx.act_signal.connect(lambda:self.change_act(self.act_cbx))
                pos = self.row[4]
                if self.row[2] == "Mouse":
                    self.pos_wdg = PosWidget(pos)
                    self.pos_wdg.pos_btn.clicked.connect(lambda ignore,f=self.pos_wdg.get_pos:f())
                    self.tw.setItemWidget(self, 3, self.pos_wdg)

        self.setFlags(self.flags()|Qt.ItemIsEditable) #editable
        self.setCheckState(0,Qt.Checked) #col,state
        self.setExpanded(True)
    #group을 지웠을 때 child가 윗계층으로 올라가기
  
    def change_act(self,act_cbx):
        #self.tw.disconnect()
        #if act_cbx.currentText() == "Double":
            
        pass
     
    #signal의 class가 qobject를 상속할 때만 @pyqtSlot()을 달아주고, 아니면 달지 않는다
    #https://stackoverflow.com/questions/40325953/why-do-i-need-to-decorate-connected-slots-with-pyqtslot/40330912#40330912       
    def change_typ(self,typ_cbx,act_cbx):
        #typ_cbx를 self.typ_cbx로 바꾸고 param 지우기
        self.tw.disconnect()
        if typ_cbx.currentText() == "Mouse":
            act_cbx.clear()
            act_cbx.addItem("Click")
            act_cbx.addItem("Double")
            act_cbx.addItem("Right")
            act_cbx.addItem("Drag")
            act_cbx.addItem("Move")
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
            act_cbx.addItem("Select All")
            self.setText(1,"Key")
            self.setText(2,"Copy")
            act_cbx.setCurrentIndex(0)
            self.tw.removeItemWidget(self,3)
            self.setText(3,"") # pos widget 지운 후 treewidget의 pos data 삭제
        ctr_widget = self.tw.parent()
        wid = ctr_widget.parent()
        self.tw.itemChanged.connect(wid.get_item) # typ을 key로 변경시 - pos 연동 삭제
        
class TreeUndoCommand(QUndoCommand):
    def __init__(self,tree,tree_str,stack):
        super().__init__()
        self.tree = tree
        self.stack = stack
        self.tree_str = tree_str
    
    def redo(self):
        pass
    
    def undo(self):
        # undo할 때 stack에서 1개를 꺼낸다
        # 정확히는 마지막 tree값을 취하고, 현 index를 -1 시킨다
        # undo,redo 외의 새로운 작업이 발생하면 index를 -1 뒤의 tree는 날리고,
        # 새로운 작업을 stack에 쌓는다
        # 그러므로 load_log에 들어갈 인자는 stack에서 꺼낸 tree여야한다
        idx = self.stack.index()
        cmd = self.stack.command(idx-1)
        if not isinstance(cmd,NoneType):
            self.tree.load_log(cmd.tree_str)
            print(cmd.tree_str)
        pass

#https://stackoverflow.com/questions/25559221/qtreewidgetitem-issue-items-set-using-setwidgetitem-are-dispearring-after-movin        
class TreeWidget(QTreeWidget):
    customMimeType = "application/x-customTreeWidgetdata"
    def __init__(self,parent):
        super().__init__()
        self.win = parent
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.dropEvent = self.treeDropEvent
        self.setEditTriggers(QAbstractItemView.DoubleClicked)
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)
        #self.setContextMenuPolicy(Qt.CustomContextMenu) #비활성화시키면 contextmenuevent 동작됨
        self.customContextMenuRequested.connect(self.context_menu)
        self.copy_buf = []
        self.log_lst = []
        self.log_str = ""
        self.undoStack = QUndoStack(self)
        self.undoStack.setIndex(0)
        self.cnt = 0
        #self.setStyleSheet("TreeWidget::item:selected"
        #    "{"
        #    "background-color : #d9fffb;"
        #    "selection-color : #000000;"
        #    "}")

    def mousePressEvent(self, event):
        print(event.modifiers())
        if event.modifiers() == Qt.ControlModifier:
            return
        return super().mousePressEvent(event)
    
    def mouseReleaseEvent(self, event):
        if event.modifiers() == Qt.ControlModifier:
            # 위에서 Select했던 item을 여기로 넘겨줘야함
            super().mousePressEvent(event)
            items = self.currentItem()
            if items:
                self.setCurrentItem(items)
            else:
                pass
        return super().mouseReleaseEvent(event)

    def save_log(self):
        self.log_str = ""
        col_cnt = self.columnCount()
        top_cnt = self.topLevelItemCount()
        if top_cnt:
            for i in range(top_cnt):
                top_it = self.topLevelItem(i)
                if top_it:        
                    self.log_str += ','.join(["top",top_it.text(0),"","","",""])
                    self.log_str += '\n'
                    if top_it.childCount():
                        self.recur_log(top_it)
        self.log_str = self.log_str.rstrip('\n')
        return self.log_str
        
    def load_log(self,tree_str):
        # stack에서 해당 index에 해당하는 tree를 꺼내온다
        self.disconnect()
        self.clear()
        reader = list(tree_str.split('\n'))
        for i,row in enumerate(reader):
            row = row.split(',')
            if len(row) == 7:
                row[4] = (row[4]+","+row[5]).strip("\"")
                row[5] = ""
                row.pop()
            reader[i] = row
        self.insts=[]
        
        for idx,row in enumerate(reader):
            parent = ""
            parent_str = row[0]
            name = row[1]
            if parent_str == 'top':
                parent = self
                tw_item = TreeWidgetItem(self,parent,row)
                tw_item.prnt_name = 'top'
                tw_item.setText(0,name)
            else:
                for inst in self.insts:
                    if inst.text(0) == parent_str:   
                        parent = inst                        
                        tw_item = TreeWidgetItem(self,parent,row)
                        tw_item.prnt_name = parent.text(0)
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
        self.itemChanged.connect(self.win.get_item)

    def recur_log(self,parent):
        for ch_num in range(parent.childCount()):
            ch_it = parent.child(ch_num)
            
            row = [ch_it.text(i) for i in range(self.columnCount())] 
            if ch_it.text(1):
                row[2] = ch_it.act_cbx.currentText()
                if ch_it.text(1) == "Mouse":
                    row[3] = "\""+ch_it.pos_wdg.pos_le.text()+"\""
            row.insert(0,parent.text(0))   
            self.log_str += ','.join(row)
            self.log_str += '\n' #추후 widget으로 접근하는 방식도 고려
            if ch_it.childCount():
                self.recur_log(ch_it)
    
    def save_push_log(self):
        tree_str = self.save_log() 
        cmd = TreeUndoCommand(self,tree_str,self.undoStack)
        self.undoStack.push(cmd)                    
                    
    def keyPressEvent(self, event):
        root = self.invisibleRootItem()
        if event.key() == Qt.Key_Delete:  
            # undo하기 위해 실행직전 상태를 save 한다 
            self.save_push_log()
            cur_its = self.selectedItems()
            for cur_it in cur_its:
                (cur_it.parent() or root).removeChild(cur_it)
        elif event.matches(QKeySequence.Copy):
            self.copy_buf = self.selectedItems()
            prnt_lst = []
            for item in self.copy_buf:
                prnt_lst.append(item.prnt_name)
            name_lst = []
            for item in self.copy_buf:
                name_lst.append(item.text(0))
            main_lst = []
            for item in self.copy_buf:
                if item.prnt_name not in name_lst:
                    main_lst.append(item)
            self.copy_buf = main_lst
        elif event.matches(QKeySequence.Paste):
            self.save_push_log()
             # 붙여넣기 할 때 다중선택이 가능한지?
             # 우선은 다중선택 생각하지 않고
             # 이동과 같은 방식
            target = self.currentItem()
            if target.typ_cbx == None:
                for it in self.copy_buf:
                    # QTree->TreeWidgetItem?
                    item = TreeWidgetItem(self,target)
                    self.fillItem(it, item)
                    self.fillItems(it, item)
                print("Paste")
        elif event.matches(QKeySequence.Undo):
            self.undoStack.undo()
        else:
            super().keyPressEvent(event)
            
    def contextMenuEvent(self,event):
        self.menu = QMenu(self)
        delete_act = QAction('Delete',self)
        delete_act.triggered.connect(lambda:self.recur_delete(event))
        ungroup_act = QAction('Ungroup',self)
        ungroup_act.triggered.connect(lambda:self.ungrouping(event))
        group_act = QAction('Group',self)
        group_act.triggered.connect(lambda:self.grouping(event))
        self.menu.addAction(delete_act)
        self.menu.addAction(ungroup_act)
        self.menu.addAction(group_act)
        self.menu.popup(QCursor.pos())
    
    def grouping(self,event):
        # selected items -> 마지막에 선택된 item의 부모 밑에 Group 폴더를 만듦
        # selected items는 기존의 위치에서 삭제됨
        # selected items들에서 item without parent 뽑아냄
        # 현재의 parent에서 새로 group 생성(생성후에 lineedit 수정 상태로)
        # 새로 생성한 group가 addchild(item without parent)하기 
        pass
        
    # 나중에 sip 시도해보기
    def recur_delete(self,event):
        root = self.invisibleRootItem()
        for item in self.selectedItems():
            print(item)
            (item.parent() or root).removeChild(item)
    
    # cur의 child의 parent를 cur->cur.parent()로 바꾸기
    # cur의 ix와 parent를 뽑기
    # child_without_parent를 parent.addChild로 더하기
    # ungrouping 한 후 widget 풀리는 현상 발생
    def ungrouping(self,event):
        self.save_push_log()
        root = self.invisibleRootItem()
        for item in self.selectedItems():
            # inst에 ungroup 하면 바깥으로 빠져나오는 기능 추가
            if isinstance(item.typ_cbx,NoneType):
                new_parent = item.parent()
                child_cnt = item.childCount()
                if child_cnt:
                    for idx in range(child_cnt):
                        #child가 하나씩 사라지므로 마지막 idx일때 1개만 남음
                        #그러므로 최신 child를 지우도록 인자를 0 둠
                        item_without_parent = item.takeChild(0)
                        #top일 때 nonetype이라 insertchild 안됨
                        #child를 top으로 만들어줘야함. 복잡하네...
                        if isinstance(new_parent,NoneType):
                            ix = self.indexOfTopLevelItem(item)
                            self.insertTopLevelItem(ix,item_without_parent)   
                            item_without_parent.prnt_name = "top"
                            self.move_itemwidget(self,item_without_parent,new_parent)
                            #삭제하는법은?
                            #move_item
                            #item이 toplevel 몇번째인지
                        else:
                            new_parent.insertChild(idx,item_without_parent)
                            item_without_parent.prnt_name = new_parent.text(0)
                            self.move_itemwidget(self,item_without_parent,new_parent)
                (new_parent or root).removeChild(item) # 오류 있을수도 있음
            
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
    '''
    def startDrag(self, supportedActions):
        drag = QDrag(self)
        
        #drag.setPixmap(QPixmap("pic.PNG"))
        pixmap = QPixmap(self.viewport().visibleRegion().boundingRect().size())
        pixmap.fill(Qt.transparent)
        painter = QPainter(pixmap)
        painter.drawPixmap(self.rect(),self.grab())
        painter.end()
        drag.setPixmap(pixmap)
        #drag.setHotSpot(event.pos())
        
        mimedata = self.model().mimeData(self.selectedIndexes())
        encoded = QByteArray()
        stream = QDataStream(encoded, QIODevice.WriteOnly)
        self.encodeData(self.selectedItems(), stream)
        mimedata.setData(TreeWidget.customMimeType, encoded)
        drag.setMimeData(mimedata)
        drag.exec_(supportedActions)
        '''
    
    def move_itemwidget(self,tw,drag_item,target,event=None):
        self.tw = tw
        if event != None:
            event.setDropAction(Qt.MoveAction)
            # drag item이 inst이고, drop하려는 위치가 inst이면 return 시키기
            TreeWidget.dropEvent(self, event) # dropevent 이후 자식 사라짐
            print(drag_item.childCount())
        # *drop event로 Data를 먼저 옮기고, if문 이하에서 item setting
        if not drag_item.text(1): # Group이면 부모 재설정 new_parent(target)인자를 받아서
            drag_item.prnt = target
            if isinstance(target,NoneType):
                drag_item.prnt_name = "top"
            else:
                drag_item.prnt_name = target.text(0) 
            #target.insertChild(0,drag_item) # 인덱스는 임시로 0
        elif drag_item.text(1):
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
            drag_item.typ_cbx.typ_signal.connect(lambda:drag_item.change_typ(drag_item.typ_cbx,drag_item.act_cbx))
        child_cnt = drag_item.childCount()
        # 단,group이어도 group 자신만 dropevent만하고, 자식들은 move_itemwidget 거치도록
        if child_cnt:
            for idx in range(child_cnt):
                child = drag_item.child(idx)
                #event를 param으로 넘겨도 되는지
                self.tw.move_itemwidget(self.tw,child,drag_item,event)
            
    #group간 종속기능 가능
    #pos 따라가도록
    def treeDropEvent(self, event):
        target = self.itemAt(event.pos())
        # 현 treewidget으로 drop
        root = self.invisibleRootItem()
        self.save_push_log()        
        if event.source() == self:
            modifiers = event.keyboardModifiers()   
            #if event.mimeData().hasFormat(TreeWidget.customMimeType):
            #    encoded = event.mimeData().data(TreeWidget.customMimeType)
            #    items = self.decodeData(encoded, event.source())
            #    # problem : 복수 선택 후 복사할 때 child가 중복 복사되는 문제
            #    # solution : 선택된 것들의 이름 모으기, 부모 모으기
            #    # -> 내 부모의 이름이 이름안에 있으면 난 안됨
            #    # selected item에 col에 반영되지 않는 parent 정보가 있으면 편한데,
            #    # 지금은 우선 번거롭더라도 selected items에서 prnt_str으로 parent 이름을 받자
            prnt_lst = []
            for sel_item in self.selectedItems():
                prnt_lst.append(sel_item.prnt_name)
            name_lst = []
            for item in self.selectedItems():
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
    # 문제 : group,inst가 위계없이 items에 다 들어가는 중. (왜냐하면, group,inst를 구분하는 코드는 없고, text(1)을 기준으로 나누기 때문에) 중복을 제외하고 넘기기
    # n,0 (role은 0으로  고정하고 n은 0~4)
    def fillItem(self, inItem, outItem):
        for col in range(inItem.columnCount()):
            for key in range(Qt.UserRole):
                role = Qt.ItemDataRole(key)
                outItem.setData(col, role, inItem.data(col, role))
                
        # *drop event로 Data를 먼저 옮기고, if문 이하에서 item setting
        if not outItem.text(1): # Group이면 부모 재설정 new_parent(target)인자를 받아서
            #outItem.prnt = target
            outItem.prnt_name = outItem.text(0) 
            #target.insertChild(0,drag_item) # 인덱스는 임시로 0
        elif outItem.text(1):
            outItem.typ_cbx = TypCombo(self,outItem.text(1))
            outItem.act_cbx = ActCombo(outItem.text(1),outItem.text(2))
            self.setItemWidget(outItem, 1, outItem.typ_cbx)
            self.setItemWidget(outItem, 2, outItem.act_cbx)
            if outItem.text(1) == "Mouse":
                coor = outItem.text(3)
                outItem.pos_wdg = PosWidget(coor)
                # 이동해도, item을 새로 만드는 것이기 때문에, connect도 다시 해줘야한다.
                # 추후 class init할 때 connect 하도록 수정할 필요있음
                outItem.pos_wdg.pos_btn.clicked.connect(lambda ignore,f=outItem.pos_wdg.get_pos:f())                  
                self.setItemWidget(outItem, 3, outItem.pos_wdg)
            outItem.typ_cbx.typ_signal.connect(lambda:outItem.change_typ(outItem.typ_cbx,outItem.act_cbx))
        child_cnt = outItem.childCount()
        # 단,group이어도 group 자신만 dropevent만하고, 자식들은 move_itemwidget 거치도록       

    def fillItems(self, itFrom, itTo):
        for ix in range(itFrom.childCount()):
            ch = itFrom.child(ix)
            it = TreeWidgetItem(self,itTo)
            
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
            print(row)
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
        execAction = QAction('Execute', self)
        execAction.setStatusTip('Execute application')
        exitAction = QAction('Exit', self)
        exitAction.setShortcut('Ctrl+Q')
        exitAction.setStatusTip('Exit application')

        menubar = self.menuBar()
        menubar.setNativeMenuBar(False)
        filemenu = menubar.addMenu('&File')
        filemenu.addAction(loadAction)
        filemenu.addAction(saveAction)
        filemenu.addAction(execAction)
        filemenu.addAction(exitAction)
        
        loadAction.triggered.connect(self.load)
        saveAction.triggered.connect(self.save)
        execAction.triggered.connect(self.exec_inst)
        exitAction.triggered.connect(self.self_close)
        
        self.tw = TreeWidget(self)
        self.tw.setColumnCount(5)
        self.tw.setHeaderLabels(["Name","Type","Act","Pos","Content"])
                
        self.ctr_lay.addWidget(self.tw)
    
        self.tw2 = TreeWidget(self)
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
            csvfile.close()
                            
    def exec_inst(self):
        # inst_list 수집
        top_cnt = self.tw.topLevelItemCount()
        inst_lst = []
        if top_cnt:
            for i in range(top_cnt):
                top_it = self.tw.topLevelItem(i)
                if top_it:
                    if top_it.checkState(0) == Qt.Checked: # check 된 것만 돌기
                        if top_it.text(1):
                            inst_lst.append(top_it)
                        else:
                            if top_it.childCount():
                                self.recur_child_exec(top_it,inst_lst)
        # inst_list 실행
        for inst in inst_lst:
            typ = inst.typ_cbx.currentText()
            if typ == "Mouse":
                x,y = inst.pos_wdg.pos_le.text().split(',')
                act = inst.act_cbx.currentText()
                if act == "Click":
                    pag.click(x=int(x),y=int(y),clicks=1)
                elif act == "Right":
                    pag.rightClick(x=int(x),y=int(y))
                elif act == "Double":
                    pag.click(x=int(x),y=int(y),clicks=3,interval=0.1) 
                elif act == "Drag":
                    pag.moveTo(x=1639,y=259)
                    pag.dragTo(int(x),int(y),0.2)
                elif act == "Move":
                    pag.moveTo(x=int(x),y=int(y))
            elif typ == "Key":
                if act == "Copy":
                    pag.hotkey('ctrl', 'c')
                elif act == "Paste":
                    pag.hotkey('ctrl', 'v')
                elif act == "Select All":
                    pag.hotkey('ctrl', 'a')
    
    def recur_child_exec(self,parent,lst):
        if parent.childCount():
            for ch_num in range(parent.childCount()):
                ch_it = parent.child(ch_num)
                if ch_it.checkState(0) == Qt.Checked: # Check 된 것만 돌기
                    if ch_it.text(1):
                        lst.append(ch_it)
                    else:
                        if ch_it.childCount():
                            self.recur_child_exec(ch_it,lst)
                
    # 순수 recur만 분리하기. 지금은 write와 섞여있음   
    def recur_child(self,writer,parent):
        if parent.childCount():
            #써주는 상황 : top은 써주고 recursive, 막내는 recursive 마지막에, 중간은 써줄 기회가 없다
            #그러므로 top은 예외고, 중간과 막내는 써주는 상황을 통일시켜야 한다
            #recursive 가기 전에 해주는게 맞아 보인다
            for ch_num in range(parent.childCount()):
                ch_it = parent.child(ch_num)
                lst = [ch_it.text(i) for i in range(self.tw.columnCount())] #text로 접근하기보다, widget으로 접근하는게 맞음
                if ch_it.text(1):
                    lst[2] = ch_it.act_cbx.currentText()
                    if ch_it.text(1) == "Mouse":
                        lst[3] = ch_it.pos_wdg.pos_le.text()
                lst.insert(0,parent.text(0))   
                writer.writerow(lst)
                self.recur_child(writer,parent.child(ch_num))
        return
    '''
    def write_csv(self,parent,ch_it):
        lst = [ch_it.text(i) for i in range(self.tw.columnCount())] #text로 접근하기보다, widget으로 접근하는게 맞음
        if ch_it.text(1) == "Mouse":
            lst[3] = ch_it.pos_wdg.pos_le.text()
        lst.insert(0,parent.text(0))     
        writer.writerow(lst)
    '''
         
    def load(self):
        self.tw.disconnect()
        self.tw.clear()
        self.tw.setDragEnabled(True)
        self.tw.setAcceptDrops(True)
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
                    tw_item.prnt_name = 'top'
                    tw_item.setText(0,name)
                else:
                    for inst in self.insts:
                        if inst.text(0) == parent_str:   
                            parent = inst                        
                            tw_item = TreeWidgetItem(self.tw,parent,row)
                            tw_item.prnt_name = parent.text(0)
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