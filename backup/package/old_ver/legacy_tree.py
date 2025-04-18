import csv
import pyautogui as pag
from types import NoneType
from enum import Enum
from copy import deepcopy
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from package import pos as ps
from package.components import compo as cp
from package.old_ver import legacy_tree as tr
from package.resources import *
import copy

class Indi(Enum):
    md = 0
    up = 1
    dw = 2
    
class Head(Enum):
    non = 0
    inp = 1
    pos = 2
    sub = 3

class TreeWidgetItem(QTreeWidgetItem):
    def __init__(self,tw,parent=None,row=""):
        QTreeWidgetItem.__init__(self, parent) # 부모 지정하는 단계
        # Set Tree
        self.tw = tw
        self.inp_tog = None
        self.sub_wid = None
        self.sub_tog = None
        self.body = [self.inp_tog, self.sub_wid, self.sub_tog]
        
        # Unpacking row : parent, name, inp, sub, sub_con, typ
        self.prnt = row[0]
        self.name = row[1]
        self.inp = row[2]
        self.sub_con = row[3]
        self.sub = row[4]
        self.typ = "G" if self.is_group() else "I"
        
        # Column 1 : Check, typ, name
        self.setCheckState(0, Qt.CheckState.Checked) # 이것도 csv에 저장해야함
        self.setIcon(0, QIcon(rsc[self.typ]["icon"]))
        self.setText(0, self.name)
        self.setFlags(self.flags() | Qt.ItemIsEditable) # editable
        self.setExpanded(True)
            
        # Column 2~5 : inp,sub,sub_con
        if self.is_inst():
            self.set_widget(self.tw)
    
    @property
    def sub_con(self):
        if self.__sub_con:
            return self.__sub_con
        else:
            return "Empty"
        
    @sub_con.setter    
    def sub_con(self,value):
        self.__sub_con = value
        
    
    # Rules : group을 지웠을 때 child가 윗계층으로 올라가기
    def set_widget(self,tw):
        self.setFlags(self.flags() ^ Qt.ItemIsDropEnabled) # ~ : 가능 / ^ : 불가능
        
        # 1 input
        self.inp_tog = cp.InpTogBtn(self,self.inp)
        self.inp_tog.signal.connect(lambda:self.toggle_input())
        
        # 2 sub_con
        if self.inp == "M":
            x, y =  self.sub_con.split(",")
            self.sub_wid = cp.PosWidget(x, y)
            tw.setItemWidget(self, 2, self.sub_wid)
        else:
            if self.sub == "typing":
                self.sub_wid = QLineEdit()
            else: # self.sub == "copy" or "paste"
                self.sub_wid = QLabel()
            self.sub_wid.setText(self.sub_con)
            self.sub_wid.setFixedSize(115,25)

        # 3 sub
        self.sub_tog = cp.SubTogBtn(self,self.inp,self.sub) # group일때는 버튼을 비활성화+색상변경
        self.sub_tog.signal.connect(lambda:self.toggle_subact())
        # 4. Set
        tw.setItemWidget(self, 1, self.inp_tog)
        tw.setItemWidget(self, 2, self.sub_wid)
        tw.setItemWidget(self, 3, self.sub_tog)
        
    def connect_change_event():
        pass
        
    def is_group(self):
        return True if self.inp == "" else False
    
    def is_inst(self):
        return False if self.inp == "" else True
    
    def is_top(self):
        return True if isinstance(self.parent(), NoneType) else False
  
    #signal의 class가 qobject를 상속할 때만 @pyqtSlot()을 달아주고, 아니면 달지 않는다
    #https://stackoverflow.com/questions/40325953/why-do-i-need-to-decorate-connected-slots-with-pyqtslot/40330912#40330912
    # 매번 cp를 생성하지 말고, 숨기고 드러내는 방식으로 변경해야함       
    def toggle_input(self):
        self.inp = next(self.inp_tog.iters)
        self.inp_tog.setIcon(QIcon(rsc[self.inp]["icon"]))
        
        if self.inp == "K":
            self.inp_tog.cur = "K"
            self.sub_tog.cur = "typing"
            self.sub_wid = QLineEdit()
            self.sub_wid.setFixedSize(115,25)
            self.sub_wid.setText("Empty")
            self.tw.setItemWidget(self, Head.pos.value, self.sub_wid)
        else:
            self.inp_tog.cur = "M"
            self.inp_tog.cur = "click"
            self.sub_wid = cp.PosWidget(0,0)
            self.tw.setItemWidget(self, Head.pos.value, self.sub_wid)
        
        # Changing Subact
        self.sub_tog.iters = copy.deepcopy(rsc[self.inp]["subacts"])
        self.sub = next(self.sub_tog.iters)
        self.sub_tog.setIcon(QIcon(rsc[self.sub]["icon"]))

        self.finish_tog()
    
    def toggle_subact(self): # 난독 코드 가능성. 수정 필요
        self.sub = next(self.sub_tog.iters)
        self.sub_tog.setIcon(QIcon(rsc[self.sub]["icon"]))
        
        if self.inp == "K":
            last_txt = self.sub_wid.text()
            self.tw.removeItemWidget(self,Head.pos.value)
            if self.sub == "typing":
                self.sub_wid = QLineEdit()
                self.sub_wid.setFixedSize(115,25)
            else:
                self.sub_wid = QLabel(last_txt)
            self.sub_wid.setText(last_txt)
            self.tw.setItemWidget(self, 2, self.sub_wid)

        self.finish_tog()
    
    def finish_tog(self):
        self.tw.snapshot() # 현상황 log 저장
        self.tw.disconnect()        
        self.tw.itemChanged.connect(self.tw.change_check) # cur M -> K : pos 연동 삭제
        self.tw.setFocus()
                
class TreeUndoCommand(QUndoCommand):
    def __init__(self,tree,tr_str,stack):
        super().__init__()
        self.tr = tree
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
        if not isinstance(cmd, NoneType):
            self.tr.load_log_from_logs(cmd.tr_str)
            
#https://stackoverflow.com/questions/25559221/qtreewidgetitem-issue-items-set-using-setwidgetitem-are-dispearring-after-movin        
class TreeWidget(QTreeWidget):
    customMimeType = "application/x-customTreeWidgetdata"
    def __init__(self,parent):
        super().__init__()
        self.win = parent
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.setEditTriggers(QAbstractItemView.DoubleClicked)
        self.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.dropEvent = self.treeDropEvent
        self.header().setSectionResizeMode(QHeaderView.ResizeToContents) #adjust
        self.header().setCascadingSectionResizes(True)
        self.customContextMenuRequested.connect(self.context_menu)
        #self.header().setSectionResizeMode(5,QHeaderView.Stretch) # movable True
        #self.setContextMenuPolicy(Qt.CustomContextMenu) #비활성화시키면 contextmenuevent 동작됨
        self.sel_nd_it_list = []
        self.log_lst = []
        self.log = ""
        self.inst_list=[]
        self.undoStack = QUndoStack(self)
        self.undoStack.setIndex(0)
        self.cnt = 0
        
    def mousePressEvent(self, event):
        if event.modifiers() != Qt.KeyboardModifier.ControlModifier:
            return super().mousePressEvent(event)
    
    def mouseReleaseEvent(self, event):
        if event.modifiers() == Qt.KeyboardModifier.ControlModifier:
            # 위에서 Select했던 item을 여기로 넘겨줘야함
            super().mousePressEvent(event)
            items = self.currentItem()
            if items:
                self.setCurrentItem(items)
        return super().mouseReleaseEvent(event)

    #SQL
    def save_log(self):
        self.log = ""
        top_it_cnt = self.topLevelItemCount()
        for i in range(top_it_cnt):
            top_it = self.topLevelItem(i)
            if top_it:
                name = top_it.name
                if top_it.inp_tog:
                    inp = top_it.inp_tog.cur
                    sub = top_it.sub_tog.cur
                    coor_str = top_it.pos
                    self.log += ','.join(["top",name,inp,sub,coor_str,""])
                else:
                    self.log += ','.join(["top",name,"","","",""])
                self.log += '\n'
                
                self.recur_log(top_it)
                    
        self.log = self.log.rstrip('\n')
        return self.log
    '''
    def load_log(self, log):
        self.disconnect()
        self.clear()
        reader = log.split('\n')
        for i, row in enumerate(reader):
            row = row.split(',')
            if len(row) == 7:
                row[4] = (row[4] + "," + row[5]).strip("\"")
                row[5] = ""
                row.pop()
            reader[i] = row
        self.insts = []

        for row in reader:
            parent = ""
            parent_str = row[0]
            name = row[1]
            if parent_str == 'top':
                parent = self
                tw_it = TreeWidgetItem(self, parent, row)
                tw_it.prnt = 'top'
                tw_it.setText(0, name)
            else:
                for inst in self.insts:
                    if inst.name == parent_str:
                        parent = inst
                        tw_it = TreeWidgetItem(self, parent, row)
                        tw_it.prnt = parent.name
                        tw_it.setText(0, name)
                        break

            if len(row) > 2:
                sub_con = row[5]
                tw_it.setText(3, sub_con)
            self.insts.append(tw_it)
        self.itemChanged.connect(self.change_check)
    '''
    # undo 할 때 쓰임
    def load_log_from_logs(self, logs):
        self.inst_list = []
        self.disconnect()
        self.clear()
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        print(logs)
        log_list = [log.split(",") for log in logs.split("\n")]
        for row in log_list:
            p_str, name, *rest = row
            p = next((inst for inst in self.inst_list if inst.name == p_str), None)
            tw_it = tr.TreeWidgetItem(self, p, row) if p else tr.TreeWidgetItem(self, self, row)
            tw_it.prnt = p.name if p else 'top'
            tw_it.setIcon(0, QIcon(rsc[tw_it.typ]["icon"]))
            tw_it.setText(0, name)
            if len(rest) > 1 and rest[0] == "K":
                tw_it.setText(3, rest[1])
            self.inst_list.append(tw_it)

        self.itemChanged.connect(self.change_check)
    
    def load_log_from_csv(self):
        #아래 5줄 줄이기
        self.inst_list = []
        #self.disconnect()
        self.clear()
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        
        with open('ex.csv', 'rt') as f:
            log_list = list(csv.reader(f))
        
            for row in log_list:
                prnt, name, *wid_info = row
                p = next((inst for inst in self.inst_list if inst.name == prnt), None) # tuple : iter(O), List : iter(X)
                parent = p if p else self

                tw_it = tr.TreeWidgetItem(self, parent, row)
                tw_it.prnt = p.name if p else 'top'
                tw_it.setIcon(0, QIcon(rsc[tw_it.typ]["icon"]))
                tw_it.setText(0, name)

                #if len(wid_info) > 1 and wid_info[0] == "K":
                #    tw_it.setText(3, wid_info[1])
                self.inst_list.append(tw_it)

            self.itemChanged.connect(self.change_check)
        
    def recur_log(self, parent):
        row = []
        ch_cnt = parent.childCount()
        if ch_cnt:
            for ix in range(ch_cnt):
                it = parent.child(ix)
                if it.is_inst():
                    row = [it.prnt, it.name, it.inp, it.sub_con, it.sub]
                row_str = ",".join(row) + "\n"
                self.log += row_str
                
                self.recur_log(it)
    
    #
    # del 등의 작업 전 log를 undostack에 임시 저장            
    def snapshot(self):
        log = self.save_log()
        cmd = TreeUndoCommand(self,log,self.undoStack)
        self.undoStack.push(cmd)                    
                    
    def keyPressEvent(self, event):
        root = self.invisibleRootItem()
        sel_it_list = self.selectedItems()
        if event.key() == Qt.Key.Key_Delete::
            self.snapshot()
            for sel_it in sel_it_list:
                (sel_it.parent() or root).removeChild(sel_it)
        elif event.matches(QKeySequence.Copy):
            sel_it_name_list = [sel_it.name for sel_it in sel_it_list]
            self.sel_nd_it_list = [sel_it for sel_it in sel_it_list if sel_it.prnt not in sel_it_name_list]
        elif event.matches(QKeySequence.Paste):
            self.snapshot()
            dst_it = self.currentItem()
            if dst_it.is_group():
                for sel_nd_it in self.sel_nd_it_list:
                    row = [sel_nd_it.prnt, sel_nd_it.name, sel_nd_it.inp, sel_nd_it.sub_con, sel_nd_it.sub]
                    TreeWidgetItem(self, dst_it, row)
        elif event.matches(QKeySequence.Undo):
            self.undoStack.undo()
        elif event.matches(QKeySequence.Redo):
            self.undoStack.undo()   
        else:
            super().keyPressEvent(event)
    
    # complete
    def contextMenuEvent(self,event): # menu-act-func
        # menu
        self.ctxt = QMenu(self)
        # act
        del_act = QAction('Delete',self)
        ungr_act = QAction('Ungroup',self)
        gr_act = QAction('Group',self)
        # func
        del_act.triggered.connect(lambda:self.recur_del(event))
        ungr_act.triggered.connect(lambda:self.ungroup_sel_items(event))
        gr_act.triggered.connect(lambda:self.group_sel_items(event))
        # setting
        self.ctxt.addActions([del_act, ungr_act, gr_act])
        self.ctxt.popup(QCursor.pos()) # 우클릭 좌표에서 ctxt 메뉴 띄움
    
    # 핵심 동작
    def exec_insts(self, inst_lst):
        for inst in inst_lst:
            inp = inst.inp_tog.cur
            sub = inst.sub_tog.cur

            if inp == "M":
                x, y = map(int, inst.sub_wid.coor_str.split(','))
                if sub == "Click":
                    pag.click(x=x, y=y, clicks=1)
                elif sub == "Right":
                    pag.rightClick(x=x, y=y)
                elif sub == "Double":
                    pag.click(x=x, y=y, clicks=3, interval=0.1)
                elif sub == "Drag":
                    pag.moveTo(x=1639, y=259)  # 230711 지금은 하드코딩. region으로 처리해야함
                    pag.dragTo(x, y, 0.2)
                elif sub == "Move":
                    pag.moveTo(x=x, y=y)
            else:
                if sub == "Copy":
                    pag.hotkey('ctrl', 'c')
                elif sub == "Paste":
                    text = inst.text(3)
                    if text:
                        pag.write(text)
                    else:
                        pag.hotkey('ctrl', 'v')
                elif sub == "Select All":
                    pag.hotkey('ctrl', 'a')

    # 아직 참조 없음
    def excute_sel(self,event):
        self.exec_insts(self.selectedItems())

    # 나중에 sip 시도해보기
    def recur_del(self,event):
        self.snapshot() # Log 임시저장 for undo
        root = self.invisibleRootItem()
        for sel_item in self.selectedItems():
            (sel_item.parent() or root).removeChild(sel_item)
    
    # 자료구조 heap으로 교체 예정
    # group_sel_items : 
    def group_sel_items(self, event): # cur위에 추가하고 cur끊고 new에 잇기
        self.snapshot() # Log 임시저장 for undo
        root = self.invisibleRootItem()
        cur_it = self.currentItem()
        cur_p = cur_it.parent()
        
        # 0. Node List
        node_lst = []
        if self.get_sel_items_node(cur_p, node_lst): return
        
        # 1. Create New
        new_info = []
        if cur_it.is_top():
            new_info = ["top","New Group","","","","",]
        else:
            new_info = [cur_it.prnt,"New Group","","","","",]
        
        # 2. Connect tar_p & new
        ix = 0
        new = TreeWidgetItem(self,cur_p,new_info)
        if isinstance(cur_p,NoneType):
            pass
        else:
            ix = cur_p.indexOfChild(new)
            new = cur_p.takeChild(ix)
        
        if isinstance(cur_p,NoneType):
            ix = self.indexOfTopLevelItem(new)
            self.insertTopLevelItem(ix,new)
        else:
            #ix, indp_it = self.extract_item(new) : OK
            ix = cur_p.indexOfChild(new)
            cur_p.insertChild(ix,new)

        for sel_nd_it in node_lst:
            # 3. Disconnect tar_p & tar
            # ix, sel_nd_it = self.extract_item(sel_nd_it)

            if sel_nd_it.is_top():
                ix = self.indexOfTopLevelItem(sel_nd_it)
                sel_nd_it = self.takeTopLevelItem(ix)
            else:
                ix = sel_nd_it.parent().indexOfChild(sel_nd_it)
                sel_nd_it = sel_nd_it.parent().takeChild(ix)
            
            # 4. Connect new & tar
            # it.child(ix)
            new.addChild(sel_nd_it)
            new.setExpanded(True)
            self.recur_set_widget(sel_nd_it)
    #    
    def old_group_selected_items(self,event): # cur위에 추가하고 cur끊고 new에 잇기
        self.snapshot()
        root = self.invisibleRootItem()
        cur = self.currentItem()
        tar_p = cur.parent()
        
        # 0. Node List@@
        tar_p_lst, node_lst = [],[]
        if self.get_sel_items_node(tar_p,node_lst):
            return

        # 1. Create New new
        new_info = []
        if tar_p.is_top():
            new_info = ["top","New Group","","","","",]
        else:
            new_info = [cur.prnt,"New Group","","","","",]
        
        # 2. Connect tar_p & new
        new = TreeWidgetItem(self,tar_p,new_info)
        ix, new = self.extract_item(new)
        self.connect_tar_new(tar_p,cur,new,Indi.up.value)

        # 3. Disconnect tar_p & tar
        indi = Indi.up.value
        for sel_nd_it in node_lst:
            ix, indp_it = self.extract_item(sel_nd_it)
            self.change_parent(tar_p, indp_it, new, indi)
        
        # 4. Connect new & tar    
    def ungroup_sel_items(self,event): # 가운데 추출 후 양 쪽 잇기
        self.snapshot()
        indi = Indi.md.value
        root = self.invisibleRootItem()
        
        for item in self.selectedItems():
            # Skip if top inst
            if not self.extract_and_connect(item):
                continue
            # Remove ungrouped folder
            if item == self.currentItem():
                self.extract_item(item)
                
    # custom일경우(나중에 공부). 옆에는 적용되던데 왜지...
    def context_menu(self, pos):
        index = self.indexAt(pos)
        if not index.isValid():
            return

        item = self.itemAt(pos)
        name = item.name

        menu = QMenu()
        #quitAction = menu.addAction("Quit")
        #action = menu.exec_(self.mapToGlobal(pos))
        #if action == quitAction:
        #    qApp.quit()
        menu = QMenu()
        menu.addAction("action")
        menu.addAction(name)
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
        indi = Indi.md.value
        if indi == Indi.md.value:
            if tar.is_group():
                self.change_parent(tar,tar,item,Indi.md.value)
            else:
                return
        else:
            if tar.is_top():
                self.change_parent("top",tar,item,Indi.md.value)
            else:
                self.change_parent(new_p,tar,item,Indi.md.value)
        
        # connect 잘 해줘야
        # item.inp_tog.signal.connect(lambda:item.toggle_input())
        # 아이템이 그룹일 때
        # - M일때/K일때
        # 아이템이 명령일 떄
        # -Top일 때/아닐 때
        #if self.is_group(item):
        #    item.inp_tog = ps.TypeBtn(self,item.text(1))
        #    item.sub_tog = ps.ActCb(self,item.text(1),item.text(2))
        #    self.setItemWidget(item, 1, item.inp_tog)
        #    self.setItemWidget(item, 2, item.sub_tog)
        #    if item.text(1) == "M":
        #        coor = item.sub_wid.coor.text()
        #        item.sub_wid = ps.PosWidget(coor)
        #        # 이동해도, item을 새로 만드는 것이기 때문에, connect도 다시 해줘야한다
        #        # 추후 class init할 때 connect 하도록 수정할 필요있음
        #        item.sub_wid.btn.clicked.connect(lambda ignore,f=item.sub_wid.get_pos:f())                  
        #        self.setItemWidget(item, 3, item.sub_wid)
        #    item.inp_tog.signal.connect(lambda:item.toggle_input())
        #else:
        #    item.p = tar
        #    if self.is_top(item):
        #        item.prnt = "top"
        #    else:
        #        item.prnt = tar.name 
        #    # tar.insertChild(0,item) # 인덱스는 임시로 0
        #    
        #child_cnt = item.childCount()
        ## 단,group이어도 group 자신만 dropevent만하고, 자식들은 move_itemwidget 거치도록
        #if child_cnt:
        #    for idx in range(child_cnt):
        #        child = item.child(idx)
        #        #event를 param으로 넘겨도 되는지
        #        self.move_itemwidget(child,item,event)
            
    def change_parent_plus(self, tar_p, tar, it, indi,mod=""):
        if indi == Indi.md.value:
            if tar.is_group():
                self.change_parent(tar,tar,it,indi)
            else:
                return
        else:
            if tar.is_top():
                self.change_parent("top",tar,it,indi)
            else:
                self.change_parent(tar_p,tar,it,indi)         
    
    # it : 최종 child, tar : 최종 parent
    
    def extract_and_connect(self,it):
        indi = Indi.dw.value
        if it.is_group():
            for ix in range(it.childCount()):
                it_ch = it.child(0) # change parent에서 takechild 수행하면서 child가 삭제되므로 0으로 받기
                it_p = it.parent()
                self.change_parent(it_p, it, it_ch, indi)
        else:
            if it.is_top():
                return False
            else:
                it_gp = (it.parent()).parent()
                it_p = it.parent()
                self.change_parent(it_gp, it_p, it, indi)
        return True
    
    def change_parent(self, tar_p, tar, it, indi, mod=""):
        if tar.is_top():
            tar_p = "top"
        # Step 01 : 독립 it 만들기
        ix, indp_it = self.extract_item(it)
        # Step 02 : tar_p에 잇기
        self.connect_tar_new(tar_p,tar,indp_it,indi)
        # Step 03 : item 재정비
        self.recur_set_widget(indp_it)
        #mod == Qt.KeyboardModifier.ControlModifier:
            
    def extract_item(self,it):
        # Step 01 : 독립 it 만들기
        if it.is_top():
            old_p = self
            ix = old_p.indexOfTopLevelItem(it)
            indp_it = old_p.takeTopLevelItem(ix)
        else:
            old_p = it.parent()
            ix = old_p.indexOfChild(it)
            indp_it = old_p.takeChild(ix)
        return ix, indp_it
    
    def insert_child(self, ix, tar_p, indp_it,indi):
        if tar_p == "top":
            indp_it.prnt = "top"
            #ungroup에만 쓰이고, item move에 안쓰임
            if indi == Indi.up.value or Indi.md.value: 
                self.insertTopLevelItem(ix,indp_it)
            else:
                self.insertTopLevelItem(ix+1,indp_it)
        else:
            indp_it.prnt = tar_p.name
            if indi == Indi.up.value or Indi.md.value: 
                tar_p.insertChild(ix,indp_it)
            else:
                tar_p.insertChild(ix+1,indp_it) 
    
    def connect_tar_new(self,tar_p,tar,indp_it,indi):
        if tar_p == "top":
            indp_it.prnt = "top"
            #ungroup에만 쓰이고, item move에 안쓰임
            if indi == Indi.up.value or Indi.md.value: 
                ix = self.indexOfTopLevelItem(tar)
                self.insertTopLevelItem(ix,indp_it)
            else:
                ix = self.indexOfTopLevelItem(tar)
                self.insertTopLevelItem(ix+1,indp_it)
        else:
            ix = tar_p.indexOfChild(tar)
            indp_it.prnt = tar_p.name
            if indi == Indi.up.value or Indi.md.value: 
                tar_p.insertChild(ix,indp_it)
            else:
                tar_p.insertChild(ix+1,indp_it) 

    def recur_set_widget(self,it):
        it.set_widget(self)
        it.setExpanded(True)
        for ix in range(it.childCount()):
            ch = it.child(ix)
            self.recur_set_widget(ch)

    def treeDropEvent(self, event):
        indi = self.dropIndicatorPosition()
        tar = self.itemAt(event.pos())
        tar_p = tar.parent()
        self.snapshot()

        if event.source() == self:
            mod = event.keyboardModifiers()
            # Extract sel_nd_it list
            tar_p_lst, node_lst = [], []
            if self.get_sel_items_node(tar_p, node_lst):
                return
            else:
                for item in node_lst:
                    self.change_parent_plus(tar_p, tar, item, indi, mod)
                    event.acceptProposedAction()
            #if (modifiers & Qt.KeyboardModifier.ControlModifier) and (modifiers & Qt.ShiftModifier):
            #    print("Control+Shift")   
    # 문제 : group,inst가 위계없이 items에 다 들어가는 중. (왜냐하면, group,inst를 구분하는 코드는 없고, text(1)을 기준으로 나누기 때문에) 중복을 제외하고 넘기기
    # n,0 (role은 0으로  고정하고 n은 0~4)
    
    # sel items 중에서 최상위 item만 node로 간주
    def get_sel_items_node(self,tar_p,node_lst):
        sel_items = self.selectedItems()
        sel_it_name_lst = [sel_it.name for sel_it in sel_items]
        for sel_it in sel_items:
            if sel_it.prnt not in sel_it_name_lst:
                node_lst.append(sel_it)

        # tar_p == nonetype
        if isinstance(tar_p, NoneType):
            return False
        else:
            for sel_nd_it in node_lst:
                if sel_nd_it.name == tar_p.name:
                    return True
        return False
              
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
                if t_it.checkState(0) == Qt.CheckState.Checked: # check 된 것만 돌기
                    if t_it.text(1):
                        inst_lst.append(t_it)
                    else:
                        if t_it.childCount():
                            self.recur_child_exec(t_it,inst_lst)
        self.exec_insts(inst_lst)
        
    def check_child(self, cur, col):
        if col == 0:
            for num in range(cur.childCount()):
                child = cur.child(num)
                child.setCheckState(0, Qt.CheckState.Checked)
                self.check_child(child, col)

    def uncheck_child(self, cur, col):
        if col == 0:
            for num in range(cur.childCount()):
                child = cur.child(num)
                child.setCheckState(0, Qt.Unchecked)
                self.uncheck_child(child, col)

    def uncheck_parent(self, cur, col):
        parent = cur.parent()
        if parent:
            parent.setCheckState(0, Qt.Unchecked)
            self.uncheck_parent(parent, col)

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
                p.setCheckState(0, Qt.CheckState.Checked)
                self.check_parent(p,col)

    def change_check(self,cur,col):
        self.blockSignals(True)
        if cur.checkState(col) == Qt.CheckState.Checked:
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
            writer = csv.writer(csvfile, dialect='excel', lineterminator='\n', quotechar="\"")
            it_row_list = []
            self.collect_it_row(it_row_list)
            for it_row in it_row_list:
                writer.writerow(it_row)
        csvfile.close()

    def collect_it_row(self, it_row_list):
        for ix in range(self.topLevelItemCount()):
            top_it = self.topLevelItem(ix)
            if top_it: # top 있으면
                self.append_top_it(it_row_list, top_it) # top 담기
                if top_it.childCount(): # child 있으면
                    self.recur_append_it(it_row_list, top_it) # child 담기
    
    def append_top_it(self, it_row_list, top_it):
        #top inst일 경우 추가하기
        top_it_row = ["top", top_it.name, "", "", ""]
        it_row_list.append(top_it_row)
 
    def recur_append_it(self,it_row_list,parent):
        for ix in range(parent.childCount()):
            it = parent.child(ix)
            it_row = [parent.name,it.name,"","",""]
            if it.is_inst():
                if it.inp == "M":
                    content = it.sub_wid.coor_str
                else:
                    content = it.sub_wid.text()
                it_row = [parent.name,it.name,it.inp,content,it.sub]
            it_row_list.append(it_row)
            self.recur_append_it(it_row_list,it)
        return
    
    def recur_child_exec(self,parent,lst):
        for ix in range(parent.childCount()):
            child = parent.child(ix)
            if child.checkState(0) != Qt.CheckState.Checked:
                continue
            
            if child.text(1):  # type exists
                lst.append(child)
            elif child.childCount():
                self.recur_child_exec(child, lst)
                        
            #if event.mimeData().hasFormat(TreeWidget.customMimeType):
            #    encoded = event.mimeData().data(TreeWidget.customMimeType)
            #    items = self.decodeData(encoded, event.source())
            #    # problem : 복수 선택 후 복사할 때 child가 중복 복사되는 문제
            #    # solution : 선택된 것들의 이름 모으기, 부모 모으기
            #    # -> 내 부모의 이름이 이름안에 있으면 난 안됨
            #    # selected item에 col에 반영되지 않는 parent 정보가 있으면 편한데,
            #    # 지금은 우선 번거롭더라도 selected items에서 prnt_str으로 parent 이름을 받자


