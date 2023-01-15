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
from copy import deepcopy

class Indi(Enum):
    md = 0
    up = 1
    dw = 2
    
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
        self.typ_btn = None
        self.act_cb = None
        self.pos_cp = None
        self.setText(0,self.name)
        #if len(self.row)>2: #그룹이 아닐 경우
        self.set_widget(self.tw)

        self.setFlags(self.flags()|Qt.ItemIsEditable) #editable
        self.setCheckState(0,Qt.Checked) #col,state
        self.setExpanded(True)
    #group을 지웠을 때 child가 윗계층으로 올라가기
    def set_widget(self,tw):
        if self.row[2]:
            # ~ : 가능
            # ^ : 불가능
            self.setFlags(self.flags() ^ Qt.ItemIsDropEnabled)
            
            typ_txt,act_txt = self.row[2:4]
            self.act_cb = cp.ActCb(self.tw,typ_txt,act_txt)
            self.typ_btn = cp.TypBtn(self,typ_txt)
            self.act_cb.signal.connect(lambda:self.change_act())
            self.typ_btn.signal.connect(lambda:self.change_typ())
            tw.setItemWidget(self, 1, self.typ_btn)
            tw.setItemWidget(self, 2, self.act_cb)
            
            pos = self.row[4]
            if self.row[2] == "M":
                self.pos_cp = cp.PosWidget(pos)
                self.pos_cp.btn.clicked.connect(lambda ignore,f=self.pos_cp.get_pos:f())
                tw.setItemWidget(self, 3, self.pos_cp)
                
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
        
        typ_cur = self.typ_btn.text()
        new_typ = "K" if typ_cur == "M" else "M"
        for item in self.tw.act_items[new_typ]:
            self.act_cb.addItem(item)
        self.act_cb.setCurrentIndex(0)
            
        if  typ_cur == "K":
            self.pos_cp = cp.PosWidget("0.0")
            self.pos_cp.btn.clicked.connect(lambda ignore,f=self.pos_cp.get_pos:f())
            self.tw.setItemWidget(self,Head.pos.value,self.pos_cp) # typ을 M로 변경시 - pos 연동 생성
            self.typ_btn.setText("M")
            self.typ_btn.setIcon(QIcon("src/cursor.png"))
        elif typ_cur == "M":
            self.tw.removeItemWidget(self,Head.pos.value)
            self.typ_btn.setText("K")
            self.typ_btn.setIcon(QIcon("src/key.png"))
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
            self.tree.load(cmd.tr_str)
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
        self.header().setSectionResizeMode(QHeaderView.ResizeToContents)#adjust
        self.header().setCascadingSectionResizes(True)
        #self.header().setSectionResizeMode(5,QHeaderView.Stretch)#movable True
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
        self.act_items = {"M":["Click","Double","Long","Center","Scroll","Right","Drag","Move"], "K":["Copy","Paste","Select All","Typing"]}
        
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
                tw_it.setText(3,con)    
            self.insts.append(tw_it)
        self.itemChanged.connect(self.change_check)

    def set_icon(self,it):
        if self.isGroup(it):
            it.setIcon(0,QIcon("src/bag.png"))
        else:
            it.setIcon(0,QIcon("src/inst.png")) 
            

    def load(self,mem=""):
        self.inst_list = []
        self.disconnect()
        self.clear()
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        if mem:
            mem_list = mem.split("\n")
            for ix,m in enumerate(mem_list):
                mem_list[ix] = m.split(",")
            for _,row in enumerate(mem_list):
                p = ""
                p_str = row[0]
                name = row[1]
                if p_str == 'top':
                    tw_it = tr.TreeWidgetItem(self,self,row)
                    tw_it.p_name = 'top'
                    self.set_icon(tw_it)
                    tw_it.setText(0,name) # 없애보고 해보기
                else:
                    for inst in self.inst_list:
                        if inst.text(0) == p_str:
                            p = inst
                            tw_it = tr.TreeWidgetItem(self,p,row)
                            tw_it.p_name = p.text(0)
                            self.set_icon(tw_it)
                            tw_it.setText(0,name) # 없애보고 해보기
                            break
                    
                # parent에 string이 들어가면 안되고,이 이름을 가지는 widget을 불러와야한다
                # column에 widget이 들어가면 이 코드가 의미가 없을 듯
                if len(row) >2:
                    content = row[4]
                    if row[2] == "K":
                        tw_it.setText(3,content)    
                self.inst_list.append(tw_it)
        else:
            with open('ex.csv', 'rt') as f:
                reader = csv.reader(f)
                for _,row in enumerate(reader):
                    print(row)
                    p = ""
                    p_str = row[0]
                    name = row[1]
                    if p_str == 'top':
                        tw_it = tr.TreeWidgetItem(self,self,row)
                        tw_it.p_name = 'top'
                        self.set_icon(tw_it)
                        tw_it.setText(0,name) # 없애보고 해보기
                    else:
                        for inst in self.inst_list:
                            if inst.text(0) == p_str:
                                p = inst
                                tw_it = tr.TreeWidgetItem(self,p,row)
                                tw_it.p_name = p.text(0)
                                self.set_icon(tw_it)
                                tw_it.setText(0,name) # 없애보고 해보기
                                break
                        
                    # parent에 string이 들어가면 안되고,이 이름을 가지는 widget을 불러와야한다
                    # column에 widget이 들어가면 이 코드가 의미가 없을 듯
                    
                    if len(row) >2:
                        content = row[4]
                        if row[2] == "K":
                            tw_it.setText(3,content)       
                    self.inst_list.append(tw_it)
        self.itemChanged.connect(self.change_check)

    def set_cls_win(self):
        self.close() 
        # 프로그램 자체를 닫게해야함
        
    def recur_log(self,parent):
        for ix in range(parent.childCount()):
            ch = parent.child(ix)
            ch_vals = [ch.text(i) for i in range(self.columnCount())] 
            if ch.typ_btn:
                ch_vals[1] = ch.typ_btn.text()
                ch_vals[2] = ch.act_cb.currentText()
                if ch_vals[1] == "M":
                    ch_vals[3] = ch.pos_cp.coor.text()
                elif ch_vals[1] == "K":
                    ch_vals[3] = ch.text(3)
                    
            ch_vals.insert(0,parent.text(0))
            val_join = ','.join(ch_vals)
            self.log_txt += val_join
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
            tar = self.currentItem()
            if tar.typ_btn == None: # 다시
                for it in self.copy_buf:
                    # QTree->TreeWidgetItem?
                    new_it = TreeWidgetItem(self,tar)
                    new_it.pos_cp = it.pos_cp
                    new_it.act_cb = it.act_cb
                    new_it.typ_btn = it.typ_btn
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
        #group_act = QAction('Group',self)
        #group_act.triggered.connect(lambda:self.grouping(event))
        sel_exe = QAction('Execute',self)
        sel_exe.triggered.connect(lambda:self.excute_sel(event))
        self.menu.addAction(delete_act)
        self.menu.addAction(ungroup_act)
        #self.menu.addAction(group_act)
        self.menu.addAction(sel_exe)
        self.menu.popup(QCursor.pos())
    
    def exec_insts(self, inst_lst):      
        # inst_list 실행
        for inst in inst_lst:
            typ_cur = inst.typ_btn.Text()
            act_cur = inst.act_cb.currentText()
            if typ_cur == "M":
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
            elif typ_cur == "K":
                if act_cur == "Copy":
                    pag.hotkey('ctrl', 'c')
                elif act_cur == "Paste":
                    if inst.text(3):
                        pag.write(inst.text(3))
                    else:
                        pag.hotkey('ctrl', 'v')
                elif act_cur == "Select All":
                    pag.hotkey('ctrl', 'a')
                    
    def excute_sel(self,event):
        self.exec_insts(self.selectedItems())

    def grouping(self,event):
        pass
        
    # 나중에 sip 시도해보기
    def recur_delete(self,event):
        root = self.invisibleRootItem()
        for item in self.selectedItems():
            (item.parent() or root).removeChild(item)
    
    def ungrouping(self,event): 
        # 옮길 때 selected item은 지워야함
        # change parent 상황, ungrouping 상황 비교하기
        self.save_push_log()
        indicator = Indi.md.value
        root = self.invisibleRootItem()
        for it in self.selectedItems():
            for ix in range(it.childCount()):
                child = it.child(0) # change parent에서 takechild 수행하면서 child가 삭제되므로 0으로 받기
                new_p = it.parent()
                tar = it
                if self.isTop(tar):
                    self.change_parent(child, "top", Indi.md.value, tar)
                else:
                    self.change_parent(child, new_p, Indi.md.value, tar)
            
            # child 옮긴 후 ungrouping 폴더 지우기
            if it.p_name == "top":
                old_p = self
                ix = old_p.indexOfTopLevelItem(it)
                new_it = old_p.takeTopLevelItem(ix)
            else:
                old_p = it.parent()
                ix = old_p.indexOfChild(it)
                new_it = old_p.takeChild(ix)
                
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

    # 쓰이지 않음
    def move_itemwidget(self,item,tar,event=None):
        if event != None:
            event.setDropAction(Qt.MoveAction)
            # inst를 inst에 드롭하면 리턴시키기
            TreeWidget.dropEvent(self, event) # dropevent 이후 자식 사라짐
            
        new_p = tar.parent()
        indicator = Indi.md.value
        if indicator == Indi.md.value:
            if self.isGroup(tar):
                self.change_parent(item,tar,Indi.md.value,tar)
            else:
                return
        else:
            if self.isTop(tar):
                self.change_parent(item,"top",Indi.md.value,tar)
            else:
                self.change_parent(item,new_p,Indi.md.value,tar)
        # connect 잘 해줘야
        # item.typ_btn.signal.connect(lambda:item.change_typ())
        # 아이템이 그룹일 때
        # - M일때/K일때
        # 아이템이 명령일 떄
        # -Top일 때/아닐 때
        #if self.isGroup(item):
        #    item.typ_btn = ps.TypBtn(self,item.text(1))
        #    item.act_cb = ps.ActCb(self,item.text(1),item.text(2))
        #    self.setItemWidget(item, 1, item.typ_btn)
        #    self.setItemWidget(item, 2, item.act_cb)
        #    if item.text(1) == "M":
        #        coor = item.pos_cp.coor.text()
        #        item.pos_cp = ps.PosWidget(coor)
        #        # 이동해도, item을 새로 만드는 것이기 때문에, connect도 다시 해줘야한다
        #        # 추후 class init할 때 connect 하도록 수정할 필요있음
        #        item.pos_cp.btn.clicked.connect(lambda ignore,f=item.pos_cp.get_pos:f())                  
        #        self.setItemWidget(item, 3, item.pos_cp)
        #    item.typ_btn.signal.connect(lambda:item.change_typ())
        #else:
        #    item.p = tar
        #    if self.isTop(item):
        #        item.p_name = "top"
        #    else:
        #        item.p_name = tar.text(0) 
        #    # tar.insertChild(0,item) # 인덱스는 임시로 0
        #    
        #child_cnt = item.childCount()
        ## 단,group이어도 group 자신만 dropevent만하고, 자식들은 move_itemwidget 거치도록
        #if child_cnt:
        #    for idx in range(child_cnt):
        #        child = item.child(idx)
        #        #event를 param으로 넘겨도 되는지
        #        self.move_itemwidget(child,item,event)
            
    def isGroup(self,it):
        return True if it.row[2] == "" else False
    
    def isTop(self,it):
        return True if isinstance(it.parent(),NoneType) else False
    
    def change_parent(self, it, new_p, indi, tar, mod=""):
        tw = self
        # Step 01 : 독립 it 만들기
        if it.p_name == "top":
            old_p = self
            ix = old_p.indexOfTopLevelItem(it)
            new_it = old_p.takeTopLevelItem(ix)
        else:
            old_p = it.parent()
            ix = old_p.indexOfChild(it)
            new_it = old_p.takeChild(ix)
            
        # Step 02 : new_p에 잇기, p_name 재설정
        if new_p == "top":
            new_it.p_name = new_p
            if indi == Indi.md.value: #ungroup에만 쓰이고, item move에 안쓰임
                ix = self.indexOfTopLevelItem(tar)
                self.insertTopLevelItem(ix,new_it)
            elif indi == Indi.up.value:
                ix = self.indexOfTopLevelItem(tar)
                self.insertTopLevelItem(ix,new_it)
            else:
                ix = self.indexOfTopLevelItem(tar)
                self.insertTopLevelItem(ix+1,new_it)
        else:
            ix = new_p.indexOfChild(tar)
            new_it.p_name = new_p.name
            if indi == Indi.up.value:
                new_p.insertChild(ix,new_it)
            else:
                new_p.insertChild(ix+1,new_it)
                
        self.recur_set_widget(new_it,tw)
        #mod == Qt.ControlModifier:

    def recur_set_widget(self,it,tw):
        it.set_widget(tw)
        it.setExpanded(True)
        for ix in range(it.childCount()):
            ch = it.child(ix)
            self.recur_set_widget(ch,tw)

    def treeDropEvent(self, event):
        indicator = QAbstractItemView.dropIndicatorPosition(self)
        tar = self.itemAt(event.pos())
        new_p = tar.parent()

        self.save_push_log()
        
        if event.source() == self: 
            tar_p_lst, all_lst, node_lst = [],[],[]
            mod = event.keyboardModifiers()   
            items = self.selectedItems()    
            for it in items:
                all_lst.append(it.text(0))
                
            for it in items:
                if it.p_name not in all_lst:
                    node_lst.append(it)

            temp_p = tar.parent()
            while True:
                if not temp_p:
                    break
                else:
                    tar_p_lst.append(temp_p.name)
                    temp_p = temp_p.parent()
                    
            for node in node_lst:
                #print(tar.parent().name)
                #print(node_lst[0].p_name)
                if node.name in tar_p_lst:
                    return
                    
            for it in node_lst:
                if indicator == Indi.md.value:
                    if self.isGroup(tar):
                        self.change_parent(it,tar,indicator,tar,mod)
                    else:
                        return
                else:
                    self.change_parent(it,new_p,indicator,tar,mod)
                        
                event.acceptProposedAction()
            #if (modifiers & Qt.ControlModifier) and (modifiers & Qt.ShiftModifier):
            #    print("Control+Shift")   
    # 문제 : group,inst가 위계없이 items에 다 들어가는 중. (왜냐하면, group,inst를 구분하는 코드는 없고, text(1)을 기준으로 나누기 때문에) 중복을 제외하고 넘기기
    # n,0 (role은 0으로  고정하고 n은 0~4)
    
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
            for ix in range(self.topLevelItemCount()):
                top_it = self.topLevelItem(ix)
                if top_it:
                    insts.append(["top",top_it.text(0),"","","",""])
                    if top_it.childCount():
                        self.recur_get_info(insts,top_it)
            
            for inst in insts:
                writer.writerow(inst)
                
        csvfile.close()
        
    def save_as(self):
        return
    
    # top은 예외 recur은 마지막에
    def recur_get_info(self,insts,parent):
        for ix in range(parent.childCount()):
            inst = ["","","","",""]
            ch = parent.child(ix)
            print(type(ch))
            inst[0] = parent.text(0)
            inst[1] = ch.text(0)
            if ch.typ_btn:
                inst[2] = ch.typ_btn.text()
                if inst[2] == "M":
                    inst[3] = ch.act_cb.currentText()
                    inst[4] = ch.pos_cp.coor.text()
                else:
                    inst[3] = ch.act_cb.currentText()
                    inst[4] = ch.text(3)
            insts.append(inst)
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