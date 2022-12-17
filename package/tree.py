import csv
import pyautogui as pag
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from package import pos as ps
from package import compo as cp
from package import tree as tr
from types import NoneType
from enum import Enum

class Head(Enum):
    non = 0
    typ = 1
    act = 2
    pos = 3
    
class TreeWidgetItem(QTreeWidgetItem):
    def __init__(self,tw,parent,row=""):
        QTreeWidgetItem.__init__(self,parent) # 부모 지정하는 단계
        self.tw = tw
        self.row = row
        self.p_name = row[0]        
        self.name = row[1]
        self.typ_cb = None
        self.act_cb = None
        self.pos_cp = None
        
        self.setText(0,self.name)
        #if len(self.row)>2: #그룹이 아닐 경우
        if self.row[2]:
            # ~ : 가능
            # ^ : 불가능
            self.setFlags(self.flags() ^ Qt.ItemIsDropEnabled)
            
            typ_txt,act_txt = self.row[2:4]
            self.typ_cb = cp.TypCb(self,typ_txt)
            self.act_cb = cp.ActCb(typ_txt,act_txt)
            self.typ_cb.signal.connect(lambda:self.change_typ())
            self.act_cb.signal.connect(lambda:self.change_act())
            self.tw.setItemWidget(self, 1, self.typ_cb)
            self.tw.setItemWidget(self, 2, self.act_cb)
            
            pos = self.row[4]
            if self.row[2] == "Mouse":
                self.pos_cp = cp.PosWidget(pos)
                self.pos_cp.btn.clicked.connect(lambda ignore,f=self.pos_cp.get_pos:f())
                self.tw.setItemWidget(self, 3, self.pos_cp)

        self.setFlags(self.flags()|Qt.ItemIsEditable) #editable
        self.setCheckState(0,Qt.Checked) #col,state
        self.setExpanded(True)
    #group을 지웠을 때 child가 윗계층으로 올라가기

    def change_act(self):
        #self.tw.disconnect()
        #if act_cb.currentText() == "Double":
        pass
     
    #signal의 class가 qobject를 상속할 때만 @pyqtSlot()을 달아주고, 아니면 달지 않는다
    #https://stackoverflow.com/questions/40325953/why-do-i-need-to-decorate-connected-slots-with-pyqtslot/40330912#40330912       
    def change_typ(self):
        self.tw.save_push_log()
        self.tw.disconnect()
        self.act_cb.clear()
        
        typ_cur = self.typ_cb.currentText()
        for item in self.tw.act_items[typ_cur]:
            self.act_cb.addItem(item)
            
        if  typ_cur == "Mouse":
            self.act_cb.setCurrentIndex(0)
            self.pos_cp = cp.PosWidget("0,0")
            self.pos_cp.btn.clicked.connect(lambda ignore,f=self.pos_cp.get_pos:f())
            self.tw.setItemWidget(self,Head.pos.value,self.pos_cp) # typ을 mouse로 변경시 - pos 연동 생성
        elif typ_cur == "Key":
            for item in self.tw.act_items[typ_cur]:
                self.act_cb.addItem(item)
            self.act_cb.setCurrentIndex(0)
            self.tw.removeItemWidget(self,Head.pos.value)
        self.tw.itemChanged.connect(self.tw.change_check) # typ을 key로 변경시 - pos 연동 삭제
        self.tw.setFocus()
        
class TreeUndoCommand(QUndoCommand):
    def __init__(self,tree,tr_str,stack):
        super().__init__()
        self.tree = tree
        self.stack = stack
        self.tr_str = tr_str
    
    def redo(self):
        pass
    
    def undo(self):
        # undo할 때 stack에서 1개를 꺼낸다
        # 정확히는 마지막 tree값을 취하고, 현 index를 -1 시킨다
        # undo,redo 외의 새로운 작업이 발생하면 index를 -1 뒤의 tree는 날리고,
        # 새로운 작업을 stack에 쌓는다
        # 그러므로 load_log에 들어갈 인자는 stack에서 꺼낸 tree여야한다
        ix = self.stack.index()
        cmd = self.stack.command(ix-1)
        if not isinstance(cmd,NoneType):
            self.tree.load_log(cmd.tr_str)
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
        self.header().setSectionResizeMode(QHeaderView.Interactive)
        self.header().setCascadingSectionResizes(True)
        self.header().setSectionsMovable(True)
        #self.setContextMenuPolicy(Qt.CustomContextMenu) #비활성화시키면 contextmenuevent 동작됨
        self.customContextMenuRequested.connect(self.context_menu)
        self.copy_buf = []
        self.log_lst = []
        self.log_txt = ""
        self.inst_list=[]
        self.undoStack = QUndoStack(self)
        self.undoStack.setIndex(0)
        self.cnt = 0
        self.header = [self.headerItem().text(col) for col in range(self.columnCount())]
        self.act_items = {"Mouse":["Click","Double","Right","Drag","Move"], "Key":["Copy","Paste","Select_All"]}
        #self.setStyleSheet("TreeWidget::item:selected"
        #    "{"
        #    "background-color : #d9fffb;"
        #    "selection-color : #000000;"
        #    "}")

    def mousePressEvent(self, event):
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
        self.log_txt = ""
        for i in range(self.topLevelItemCount()):
            top_it = self.topLevelItem(i)
            if top_it:
                self.log_txt += ','.join(["top",top_it.text(0),"","","",""])
                self.log_txt += '\n'
                if top_it.childCount():
                    self.recur_log(top_it)
        self.log_txt = self.log_txt.rstrip('\n')
        return self.log_txt
        
    def load_log(self,tr_str):
        # stack에서 해당 index에 해당하는 tree를 꺼내온다
        self.disconnect()
        self.clear()
        reader = list(tr_str.split('\n'))
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
                tw_it = TreeWidgetItem(self,parent,row)
                tw_it.p_name = 'top'
                tw_it.setText(0,name)
            else:
                for inst in self.insts:
                    if inst.text(0) == parent_str:   
                        parent = inst                        
                        tw_it = TreeWidgetItem(self,parent,row)
                        tw_it.p_name = parent.text(0)
                        tw_it.setText(0,name)
                        break
            
            #parent에 string이 들어가면 안되고,이 이름을 가지는 widget을 불러와야한다
            #column에 widget이 들어가면 이 코드가 의미가 없을 듯
            
            if len(row) >2:
                con = row[5]
                tw_it.setText(4,con)    
            self.insts.append(tw_it)
        self.itemChanged.connect(self.change_check)

    def load(self):
        self.disconnect()
        self.clear()
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        with open('ex.csv', 'rt') as f:
            reader = csv.reader(f)
            for _,row in enumerate(reader):
                print(row)
                p = ""
                p_str = row[0]
                name = row[1]
                if p_str == 'top':
                    p = self
                    tw_it = tr.TreeWidgetItem(self,p,row)
                    tw_it.p_name = 'top'
                    tw_it.setText(0,name)
                else:
                    for inst in self.inst_list:
                        if inst.text(0) == p_str:
                            p = inst
                            tw_it = tr.TreeWidgetItem(self,p,row)
                            tw_it.p_name = p.text(0)
                            tw_it.setText(0,name)
                            break
                    
                # parent에 string이 들어가면 안되고,이 이름을 가지는 widget을 불러와야한다
                # column에 widget이 들어가면 이 코드가 의미가 없을 듯
                
                if len(row) >2:
                    content = row[5]
                    tw_it.setText(4,content)    
                self.inst_list.append(tw_it)
        self.itemChanged.connect(self.change_check)

    def set_cls_win(self):
        self.close() 
        # 프로그램 자체를 닫게해야함
        
    def recur_log(self,parent):
        for ix in range(parent.childCount()):
            ch = parent.child(ix)
            ch_vals = [ch.text(i) for i in range(self.columnCount())] 
            if ch_vals[1]:
                ch_vals[2] = ch.act_cb.currentText()
                if ch_vals[1] == "Mouse":
                    ch_vals[3] = "\"" + ch.pos_cp.coor.text() + "\""
            ch_vals.insert(0,parent.text(0))   
            self.log_txt += ','.join(ch_vals)
            self.log_txt += '\n' #추후 widget으로 접근하는 방식도 고려
            if ch.childCount():
                self.recur_log(ch)
    
    def save_push_log(self):
        tr_str = self.save_log() 
        cmd = TreeUndoCommand(self,tr_str,self.undoStack)
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
            p_lst = []
            for item in self.copy_buf:
                p_lst.append(item.p_name)
            name_lst = []
            for item in self.copy_buf:
                name_lst.append(item.text(0))
            main_lst = []
            for item in self.copy_buf:
                if item.p_name not in name_lst:
                    main_lst.append(item)
            self.copy_buf = main_lst
        elif event.matches(QKeySequence.Paste):
            self.save_push_log()
            # 붙여넣기 할 때 다중선택이 가능한지?
            # 우선은 다중선택 생각하지 않고
            # 이동과 같은 방식
            trg = self.currentItem()
            if trg.typ_cb == None:
                for it in self.copy_buf:
                    # QTree->TreeWidgetItem?
                    new_it = TreeWidgetItem(self,trg)
                    new_it.pos_cp = it.pos_cp
                    new_it.act_cb = it.act_cb
                    new_it.typ_cb = it.typ_cb
                    print(111)
                    # self.fillItem(it, new_it)
                    # self.fillItems(it, new_it)
                print("Paste")
        elif event.matches(QKeySequence.Undo):
            self.undoStack.undo()
        else:
            super().keyPressEvent(event)
            
    def contextMenuEvent(self,event):
        self.menu = QMenu(self)
        act_list = []
        delete_act = QAction('Delete',self)
        delete_act.triggered.connect(lambda:self.recur_delete(event))
        ungroup_act = QAction('Ungroup',self)
        ungroup_act.triggered.connect(lambda:self.ungrouping(event))
        group_act = QAction('Group',self)
        group_act.triggered.connect(lambda:self.grouping(event))
        sel_exe = QAction('Execute',self)
        sel_exe.triggered.connect(lambda:self.excute_sel(event))
        self.menu.addAction(delete_act)
        self.menu.addAction(ungroup_act)
        self.menu.addAction(group_act)
        self.menu.addAction(sel_exe)
        self.menu.popup(QCursor.pos())
    
    def exec_insts(self, inst_lst):      
        # inst_list 실행
        for inst in inst_lst:
            typ_cur = inst.typ_cb.currentText()
            act_cur = inst.act_cb.currentText()
            if typ_cur == "Mouse":
                x,y = inst.pos_cp.coor.text().split(',')
                if act_cur == "Click":
                    pag.click(x=int(x),y=int(y),clicks=1)
                elif act_cur == "Right":
                    pag.rightClick(x=int(x),y=int(y))
                elif act_cur == "Double":
                    pag.click(x=int(x),y=int(y),clicks=3,interval=0.1) 
                elif act_cur == "Drag":
                    pag.moveTo(x=1639,y=259) # region으로 해야할 듯
                    pag.dragTo(int(x),int(y),0.2)
                elif act_cur == "Move":
                    pag.moveTo(x=int(x),y=int(y))
            elif typ_cur == "Key":
                if act_cur == "Copy":
                    pag.hotkey('ctrl', 'c')
                elif act_cur == "Paste":
                    if inst.text(4):
                        pag.write(inst.text(4))
                    else:
                        pag.hotkey('ctrl', 'v')
                elif act_cur == "Select All":
                    pag.hotkey('ctrl', 'a')
                    
    def excute_sel(self,event):
        self.exec_insts(self.selectedItems())

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
            if isinstance(item.typ_cb,NoneType):
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
                            item_without_parent.p_name = "top"
                            self.move_itemwidget(self,item_without_parent,new_parent)
                            #삭제하는법은?
                            #move_item
                            #item이 toplevel 몇번째인지
                        else:
                            new_parent.insertChild(idx,item_without_parent)
                            item_without_parent.p_name = new_parent.text(0)
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
    
    def move_itemwidget(self,drag_item,trg,event=None):
        if event != None:
            event.setDropAction(Qt.MoveAction)
            # drag item이 inst이고, drop하려는 위치가 inst이면 return 시키기
            TreeWidget.dropEvent(self, event) # dropevent 이후 자식 사라짐
            print(drag_item.childCount())
        # *drop event로 Data를 먼저 옮기고, if문 이하에서 item setting
        if not drag_item.text(1): # Group이면 부모 재설정 new_parent(trg)인자를 받아서
            drag_item.p = trg
            if isinstance(trg,NoneType):
                drag_item.p_name = "top"
            else:
                drag_item.p_name = trg.text(0) 
            # trg.insertChild(0,drag_item) # 인덱스는 임시로 0
        elif drag_item.text(1):
            drag_item.typ_cb = ps.TypCb(self,drag_item.text(1))
            drag_item.act_cb = ps.ActCb(drag_item.text(1),drag_item.text(2))
            self.setItemWidget(drag_item, 1, drag_item.typ_cb)
            self.setItemWidget(drag_item, 2, drag_item.act_cb)
            if drag_item.text(1) == "Mouse":
                coor = drag_item.pos_cp.coor.text()
                drag_item.pos_cp = ps.PosWidget(coor)
                # 이동해도, item을 새로 만드는 것이기 때문에, connect도 다시 해줘야한다
                # 추후 class init할 때 connect 하도록 수정할 필요있음
                drag_item.pos_cp.btn.clicked.connect(lambda ignore,f=drag_item.pos_cp.get_pos:f())                  
                self.setItemWidget(drag_item, 3, drag_item.pos_cp)
            drag_item.typ_cb.signal.connect(lambda:drag_item.change_typ())
        child_cnt = drag_item.childCount()
        # 단,group이어도 group 자신만 dropevent만하고, 자식들은 move_itemwidget 거치도록
        if child_cnt:
            for idx in range(child_cnt):
                child = drag_item.child(idx)
                #event를 param으로 넘겨도 되는지
                self.move_itemwidget(self,child,drag_item,event)
            
    #group간 종속기능 가능
    #pos 따라가도록
    
    def proc_drop(self,p,trg,trg_ix,it,mod=Qt.NoModifier):

        root = QTreeWidget.invisibleRootItem(self)
        if isinstance(p.parent(),NoneType):
            self.insertTopLevelItem(trg_ix,it)
        else:
            typ_v = it.typ_cb.currentText()
            act_v = it.act_cb.currentText()
            pos_v = ""
            if typ_v == "Mouse":
                pos_v = it.pos_cp.coor.text()
            new_it = TreeWidgetItem(self,p,[it.p_name, it.name, typ_v, act_v, pos_v, ''])

            #print(it.typ_cb.currentData())
            ##new_it.typ_cb = cp.TypCb(self,it.typ_cb.currentData())
            #it.typ_cb = cp.TypCb(self,"Mouse")
            #
            #self.setItemWidget(new_it, 1, new_it.typ_cb)
            #self.setItemWidget(new_it, 2, new_it.act_cb)
            #self.setItemWidget(new_it, 3, it.pos_cp)

            #self.fillItem(it, new_it)
            #self.fillItems(it, new_it)
            #trg.insertChild(trg_ix,new_it)
        if mod == Qt.NoModifier:
            (it.parent() or root).removeChild(it)
    
    def treeDropEvent(self, event):
        indicator = QAbstractItemView.dropIndicatorPosition(self)
        trg = self.itemAt(event.pos())
        trg_ix = self.indexAt(event.pos()).row()
        p = trg.parent()
        print(trg)
        print(p)
        if not p:
            p = self.topLevelItem(0)
        self.save_push_log()
        
        if event.source() == self: 
            p_lst = []
            name_lst = [] 
            main_lst = []
            modi = event.keyboardModifiers()   
            
            for it in self.selectedItems():
                p_lst.append(it.p_name)
                name_lst.append(it.text(0))
                
            for it in self.selectedItems():
                if it.p_name not in name_lst:
                    main_lst.append(it)

            for it in main_lst:
                print(it.typ_cb.currentData())
                if indicator == 0:
                    if trg.typ_cb == None:
                        self.proc_drop(p,trg,trg_ix,it,modi)
                elif indicator == 1:
                    print(1)
                    self.proc_drop(p,p,trg_ix,it,modi)
                elif indicator == 2:
                    self.proc_drop(p,p,trg_ix+1,it,modi)
                else:
                    pass
                event.acceptProposedAction()
            #if (modifiers & Qt.ControlModifier) and (modifiers & Qt.ShiftModifier):
            #    print("Control+Shift")
        elif isinstance(event.source(), QTreeWidget): # 타 widget으로 drop  
            if event.mimeData().hasFormat(TreeWidget.customMimeType):
                encoded = event.mimeData().data(TreeWidget.customMimeType)
                items = self.decodeData(encoded, event.source())
                for it in items:
                    # QTree->TreeWidgetItem?
                    new_it = TreeWidgetItem(self,trg)
                    new_it.pos_cp = it.pos_cp
                    new_it.act_cb = it.act_cb
                    new_it.typ_cb = it.typ_cb
                    
                    #self.fillItem(it, new_it)
                    #self.fillItems(it, new_it)
                event.acceptProposedAction()
                
    # 문제 : group,inst가 위계없이 items에 다 들어가는 중. (왜냐하면, group,inst를 구분하는 코드는 없고, text(1)을 기준으로 나누기 때문에) 중복을 제외하고 넘기기
    # n,0 (role은 0으로  고정하고 n은 0~4)
    def fillItem(self, inItem, outItem):
        for col in range(inItem.columnCount()):
            for key in range(Qt.UserRole):
                role = Qt.ItemDataRole(key)
                outItem.setData(col, role, inItem.data(col, role))
                
        # *drop event로 Data를 먼저 옮기고, if문 이하에서 item setting
        print(inItem.typ_cb)
        print(inItem.act_cb)
        print(inItem.pos_cp)
        if not outItem.typ_cb: # Group이면 부모 재설정 new_parent(trg)인자를 받아서
            #outItem.p = trg
            outItem.p_name = outItem.text(0) 
            #trg.insertChild(0,drag_item) # 인덱스는 임시로 0
        else:
            outItem.typ_cb = ps.TypCb(self,outItem.text(1))
            outItem.act_cb = ps.ActCb(outItem.text(1),outItem.text(2))
            self.setItemWidget(outItem, 1, outItem.typ_cb)
            self.setItemWidget(outItem, 2, outItem.act_cb)
            if outItem.text(1) == "Mouse":
                coor = outItem.text(3)
                outItem.pos_cp = ps.PosWidget(coor)
                # 이동해도, item을 새로 만드는 것이기 때문에, connect도 다시 해줘야한다.
                # 추후 class init할 때 connect 하도록 수정할 필요있음
                outItem.pos_cp.btn.clicked.connect(lambda ignore,f=outItem.pos_cp.get_pos:f())                  
                self.setItemWidget(outItem, 3, outItem.pos_cp)
            outItem.typ_cb.signal.connect(lambda:outItem.change_typ())
        child_cnt = outItem.childCount()
        # 단,group이어도 group 자신만 dropevent만하고, 자식들은 move_itemwidget 거치도록       

    def fillItems(self, itFrom, itTo):
        for ix in range(itFrom.childCount()):
            ch = itFrom.child(ix)
            it = TreeWidgetItem(self,itTo)
            it.pos_cp = ch.pos_cp
            it.act_cb = ch.act_cb
            it.typ_cb = ch.typ_cb
            #self.fillItem(ch, it)
            #self.fillItems(ch, it)

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

    def exec_inst(self): # inst_list 수집
        # 미리 수집을 해놓야야한다. item 변할 때마다. 그래서 아래 함수를 없애고, exec_insts만 존재하게 한다
        inst_lst = []
        for ix in range(self.topLevelItemCount()):
            t_it = self.topLevelItem(ix)
            if t_it:
                if t_it.checkState(0) == Qt.Checked: # check 된 것만 돌기
                    if t_it.text(1):
                        inst_lst.append(t_it)
                    else:
                        if t_it.childCount():
                            self.recur_child_exec(t_it,inst_lst)
        self.exec_insts(inst_lst)
        
    def check_child(self,cur,col):
        if col == 0:
            for num in range(cur.childCount()):
                cur.child(num).setCheckState(0, Qt.Checked)
                self.check_child(cur.child(num),col)

    def uncheck_child(self,cur,col):
        if col == 0:
            for num in range(cur.childCount()):
                ch = cur.child(num)
                ch.setCheckState(0, Qt.Unchecked)
                self.uncheck_child(ch,col)

    def uncheck_parent(self,cur,col):
        p = cur.parent()
        if p:
            p.setCheckState(0, Qt.Unchecked)
            self.uncheck_parent(p,col)

    def check_parent(self,cur,col):
        # 추가 조건 : 나와 동료가 full check -> 부모도 check
        sbl_true = True
        p = cur.parent()
        if p:
            for ix in range(p.childCount()):
                sbl = p.child(ix)
                if sbl.checkState(col) == Qt.Unchecked: #col을 적어줘야함
                    sbl_true = False
                    break
            if sbl_true:
                p.setCheckState(0, Qt.Checked)
                self.check_parent(p,col)

    def change_check(self,cur,col):
        self.blockSignals(True)
        if cur.checkState(col) == Qt.Checked:
            self.check_child(cur,col) # 자식 전체 check
            self.check_parent(cur,col) # 동료 full check-> 부모 check                                  
        else:
            self.uncheck_child(cur,col) # 자식 전체 uncheck
            self.blockSignals(True) # itemChanged 시그널 발생 막기
            self.uncheck_parent(cur,col) # 부모 전체 uncheck until
            self.blockSignals(False)
        self.setFocus()
        self.save_log()
        self.blockSignals(False)
            
    def save(self):
        with open('ex.csv', 'wt') as csvfile:
            writer = csv.writer(csvfile, dialect='excel', lineterminator='\n')
            # writer.writerow(self.header)
            insts = []
            for ix in range(self.tw.topLevelItemCount()):
                t_it = self.tw.topLevelItem(ix)
                if t_it:
                    insts.append(["top",t_it.text(0),"","","",""])
                    if t_it.childCount():
                        self.recur_get_info(insts,t_it)
            
            for inst in insts:
                writer.writerow(inst)
                
        csvfile.close()
                        
    # top은 예외
    # recur은 마지막에
    def recur_get_info(self,insts,parent):
        for ix in range(parent.childCount()):
            ch = parent.child(ix)
            if ch.text(1):
                ch.setText(2,ch.act_cb.currentText())
                if ch.text(1) == "Mouse":
                    ch.setText(3,ch.pos_cp.coor.text())
            ch.setText(0,parent.text(0))
            insts.append([ch.text(i) for i in range(self.tw.columnCount())])
            self.recur_get_info(insts,ch)
        return
    
    def recur_child_exec(self,parent,lst):
        for ix in range(parent.childCount()):
            ch = parent.child(ix)
            if ch.checkState(0) == Qt.Checked: # Check 된 것만 돌기
                if ch.text(1): # type 존재할 때
                    lst.append(ch)
                else:
                    if ch.childCount():
                        self.recur_child_exec(ch,lst)
                        
            #if event.mimeData().hasFormat(TreeWidget.customMimeType):
            #    encoded = event.mimeData().data(TreeWidget.customMimeType)
            #    items = self.decodeData(encoded, event.source())
            #    # problem : 복수 선택 후 복사할 때 child가 중복 복사되는 문제
            #    # solution : 선택된 것들의 이름 모으기, 부모 모으기
            #    # -> 내 부모의 이름이 이름안에 있으면 난 안됨
            #    # selected item에 col에 반영되지 않는 parent 정보가 있으면 편한데,
            #    # 지금은 우선 번거롭더라도 selected items에서 prnt_str으로 parent 이름을 받자