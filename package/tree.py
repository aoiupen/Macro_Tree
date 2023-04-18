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
    def __init__(self,tw,parent=None,row=""):
        QTreeWidgetItem.__init__(self, parent) # 부모 지정하는 단계
        self.tw = tw
        self.row = row
        self.p_name,self.name = self.row[0:2]
        self.typ,self.act = self.row[2:4]
        self.pos = self.row[4]

        self.tog_num = "M"
        self.tog_key_list = ["T","C","P","A"]
        self.tog_mouse_list = ["C1","C2"]
        self.tog_icon_dict = {"T":"src/key.png","C":"src/copy.png","P":"src/paste.png","A":"src/all.png"
                              ,"C1":"src/cursor.png","C2":"src/cursor2.png"}
        self.mouse_tog_btn = None
        self.key_tog_btn = None
        self.pos_cp = None
        
        #if len(self.row)>2: #그룹이 아닐 경우
        self.setText(0,self.name)
        self.set_widget(self.tw)
        self.set_icon()
        
        self.setFlags(self.flags()|Qt.ItemIsEditable) #editable
        self.setCheckState(0,Qt.Checked) #col,state
        self.setExpanded(True)
        
    #group을 지웠을 때 child가 윗계층으로 올라가기
    def set_widget(self,tw):
        if self.typ:
            # ~ : 가능
            # ^ : 불가능
            self.setFlags(self.flags() ^ Qt.ItemIsDropEnabled)
            
            #self.key_tog_btn = cp.ActCb(self.tw,typ_txt,act_txt)
            self.key_tog_btn = cp.KeyTogBtn(self,self.typ,self.typ)
            self.mouse_tog_btn = cp.MouseTogBtn(self,self.typ,self.typ)
            self.key_tog_btn.signal.connect(lambda:self.toggle_typ_key())
            self.mouse_tog_btn.signal.connect(lambda:self.toggle_typ_mouse())
            tw.setItemWidget(self, 1, self.mouse_tog_btn)
            tw.setItemWidget(self, 2, self.key_tog_btn)
   
            if "C1" in self.typ or "C2" in self.typ: #23_04_18 "C" 바꿔야함
                self.pos_cp = cp.PosWidget(self.pos)
                tw.setItemWidget(self, 3, self.pos_cp)
                
    def isGroup(self):
        return True if self.typ == "" else False
    
    def isTop(self):
        return True if isinstance(self.parent(),NoneType) else False
        
    def set_icon(self):
        icon_imgs = ["src/bag.png","src/inst.png"]
        self.setIcon(0,QIcon(icon_imgs[self.isGroup()]))
             
    def toggle_typ_key(self):
        if self.tog_num == "K":
            idx = self.tog_key_list.index(self.key_tog_btn.cur_typ)
            idx = (idx+1)%len(self.tog_key_list)
            self.key_tog_btn.cur_typ = self.tog_key_list[idx]
        
        self.tog_num = "K"
        self.tw.removeItemWidget(self,Head.pos.value)
        icon_path = self.tog_icon_dict[self.key_tog_btn.cur_typ]
        self.key_tog_btn.setIcon(QIcon(icon_path))
        
        self.mouse_tog_btn.setStyleSheet("background-color: light gray")
        self.key_tog_btn.setStyleSheet("background-color: #B4EEB4")       
     
    #signal의 class가 qobject를 상속할 때만 @pyqtSlot()을 달아주고, 아니면 달지 않는다
    #https://stackoverflow.com/questions/40325953/why-do-i-need-to-decorate-connected-slots-with-pyqtslot/40330912#40330912       
    def toggle_typ_mouse(self):
        if self.tog_num == "M":
            idx = self.tog_mouse_list.index(self.mouse_tog_btn.cur_typ)
            idx = (idx+1)%len(self.tog_mouse_list)
            self.mouse_tog_btn.cur_typ = self.tog_mouse_list[idx]
        
        # cp를 생성하는게 맞는지 고민 
        self.pos_cp = cp.PosWidget("0,0")
        self.pos_cp.btn.clicked.connect(lambda ignore,f=self.pos_cp.get_pos:f())
        self.tw.setItemWidget(self,Head.pos.value,self.pos_cp) # typ을 M로 변경시 - pos 연동 생성되는 코드
        icon_path = self.tog_icon_dict[self.mouse_tog_btn.cur_typ]
        self.mouse_tog_btn.setIcon(QIcon(icon_path))
        
        self.tog_num = "M"
        self.mouse_tog_btn.setStyleSheet("background-color: #B4EEB4")
        self.key_tog_btn.setStyleSheet("background-color: light gray")
        
        # toggle_typ_key에는 왜 안넣는지?
        self.tw.save_push_log()
        self.tw.disconnect()        
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
            print(cmd.tr_str)
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
        #self.act_items = {"M":["Click","Double","Long","Center","Scroll","Right","Drag","Move"], "K":["Copy","Paste","Select All","Typing"]}
        
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
                if top_it.mouse_tog_btn:
                    three = ""
                    if top_it.mouse_tog_btn.text() == "M":
                        three = top_it.pos_cp.coor.text()
                    elif  top_it.mouse_tog_btn.text() == "K":
                        three = top_it.text(3)
                    self.log_txt += ','.join(["top",top_it.text(0),top_it.mouse_tog_btn.text()
                                              ,top_it.key_tog_btn.cur_typ,three,""])
                else:
                    self.log_txt += ','.join(["top",top_it.text(0),"","","",""])
                self.log_txt += '\n'
                if top_it.childCount():
                    self.recur_log(top_it)
        self.log_txt = self.log_txt.rstrip('\n')
        #print(self.log_txt)
        return self.log_txt
    
    def load_log(self, tr_str):
        self.disconnect()
        self.clear()
        reader = tr_str.split('\n')
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
                tw_it.p_name = 'top'
                tw_it.setText(0, name)
            else:
                for inst in self.insts:
                    if inst.text(0) == parent_str:
                        parent = inst
                        tw_it = TreeWidgetItem(self, parent, row)
                        tw_it.p_name = parent.text(0)
                        tw_it.setText(0, name)
                        break

            if len(row) > 2:
                con = row[5]
                tw_it.setText(3, con)
            self.insts.append(tw_it)
        self.itemChanged.connect(self.change_check)

    def load(self, mem=""):
        self.inst_list = []
        self.disconnect()
        self.clear()
        self.setDragEnabled(True)
        self.setAcceptDrops(True)

        if mem:
            mem_list = [m.split(",") for m in mem.split("\n")]
        else:
            with open('ex.csv', 'rt') as f:
                mem_list = list(csv.reader(f))

        for row in mem_list:
            p_str, name, *rest = row
            p = next((inst for inst in self.inst_list if inst.text(0) == p_str), None)
            tw_it = tr.TreeWidgetItem(self, p, row) if p else tr.TreeWidgetItem(self, self, row)
            tw_it.p_name = p.text(0) if p else 'top'
            tw_it.set_icon()
            tw_it.setText(0, name)
            if len(rest) > 1 and rest[0] == "K":
                tw_it.setText(3, rest[1])
            self.inst_list.append(tw_it)

        self.itemChanged.connect(self.change_check)
               
    def recur_log(self, parent):
        for ix in range(parent.childCount()):
            ch = parent.child(ix)
            ch_vals = [ch.text(i) for i in range(self.columnCount())]
            if ch.mouse_tog_btn:
                ch_vals[1] = ch.mouse_tog_btn.text()
                ch_vals[2] = ch.key_tog_btn.text()
                if ch_vals[1] == "M":
                    ch_vals[3] = ch.pos_cp.coor.text()
                elif ch_vals[1] == "K":
                    ch_vals[3] = ch.text(3)

            ch_vals.insert(0, parent.text(0))
            val_join = ",".join(ch_vals) + "\n"
            self.log_txt += val_join
            if ch.childCount():
                self.recur_log(ch)

    
    def save_push_log(self):
        tr_str = self.save_log()
        print("-"*10) 
        print(tr_str)
        print("-"*10) 
        cmd = TreeUndoCommand(self,tr_str,self.undoStack)
        self.undoStack.push(cmd)                    
                    
    def keyPressEvent(self, event):
        root = self.invisibleRootItem()
        if event.key() == Qt.Key_Delete:
            self.save_push_log()
            for item in self.selectedItems():
                (item.parent() or root).removeChild(item)
        elif event.matches(QKeySequence.Copy):
            self.copy_buf = self.selectedItems()
            p_lst = [item.p_name for item in self.copy_buf]
            name_lst = [item.text(0) for item in self.copy_buf]
            self.copy_buf = [item for item in self.copy_buf if item.p_name not in name_lst]
        elif event.matches(QKeySequence.Paste):
            self.save_push_log()
            target = self.currentItem()
            if target.mouse_tog_btn is None:
                for item in self.copy_buf:
                    new_item = TreeWidgetItem(self, target)
                    new_item.pos_cp = item.pos_cp
                    new_item.key_tog_btn = item.key_tog_btn
                    new_item.mouse_tog_btn = item.mouse_tog_btn
                print("Paste")
        elif event.matches(QKeySequence.Undo):
            self.undoStack.undo()
        else:
            super().keyPressEvent(event)
            
    def contextMenuEvent(self,event):
        self.menu = QMenu(self) # self. 떼도 되나?
        delete_action = QAction('Delete',self)
        delete_action.triggered.connect(lambda:self.recur_delete(event))
        ungroup_action = QAction('Ungroup',self)
        ungroup_action.triggered.connect(lambda:self.ungroup_selected_items(event))
        group_action = QAction('Group',self)
        group_action.triggered.connect(lambda:self.group_selected_items(event))
        self.menu.addActions([delete_action, ungroup_action, group_action]) # 일일이 add 안해도 됨
        self.menu.popup(QCursor.pos())
    
    def exec_insts(self, inst_lst):
        for inst in inst_lst:
            typ_cur = inst.mouse_tog_btn.Text()
            act_cur = inst.key_tog_btn.currentText()

            if typ_cur == "M":
                x, y = map(int, inst.pos_cp.coor.text().split(','))
                if act_cur == "Click":
                    pag.click(x=x, y=y, clicks=1)
                elif act_cur == "Right":
                    pag.rightClick(x=x, y=y)
                elif act_cur == "Double":
                    pag.click(x=x, y=y, clicks=3, interval=0.1)
                elif act_cur == "Drag":
                    pag.moveTo(x=1639, y=259)  # region으로 해야할 듯
                    pag.dragTo(x, y, 0.2)
                elif act_cur == "Move":
                    pag.moveTo(x=x, y=y)

            elif typ_cur == "K":
                if act_cur == "Copy":
                    pag.hotkey('ctrl', 'c')
                elif act_cur == "Paste":
                    text = inst.text(3)
                    if text:
                        pag.write(text)
                    else:
                        pag.hotkey('ctrl', 'v')
                elif act_cur == "Select All":
                    pag.hotkey('ctrl', 'a')

                    
    def excute_sel(self,event):
        self.exec_insts(self.selectedItems())

    # 나중에 sip 시도해보기
    def recur_delete(self,event):
        self.save_push_log()
        root = self.invisibleRootItem()
        for item in self.selectedItems():
            (item.parent() or root).removeChild(item)
    
    # 자료구조 heap으로 교체 예정
    # group_selected_items : 
    def group_selected_items(self,event): # cur위에 추가하고 cur끊고 new에 잇기 
        self.save_push_log()
        root = self.invisibleRootItem()
        cur = self.currentItem()
        cur_p = cur.parent()
        
        # 0. Node List
        node_lst = []
        if self.get_node_list(cur_p, node_lst): return
        
        # 1. Create New
        new_info = []
        if cur.isTop():
            new_info = ["top","New Group","","","","",]
        else:
            new_info = [cur.p_name,"New Group","","","","",]
        
        # 2. Connect tar_p & new
        ix = 0
        new = TreeWidgetItem(self,cur_p,new_info)
        if isinstance(cur_p,NoneType):
            pass
        else:
            ix = cur_p.indexOfChild(new)
            new = cur_p.takeChild(ix)
            print(new.parent())
        
        if isinstance(cur_p,NoneType):
            ix = self.indexOfTopLevelItem(cur)
            self.insertTopLevelItem(ix,new)
        else:
            #ix, indp_it = self.extract_item(new) : OK
            ix = cur_p.indexOfChild(cur)
            cur_p.insertChild(ix,new)

        for node_it in node_lst:
            # 3. Disconnect tar_p & tar
            #ix, node_it = self.extract_item(node_it)

            if node_it.isTop():
                ix = self.indexOfTopLevelItem(node_it)
                node_it = self.takeTopLevelItem(ix)
            else:
                ix = node_it.parent().indexOfChild(node_it)
                node_it = node_it.parent().takeChild(ix)
            
            # 4. Connect new & tar
            # it.child(ix)
            new.addChild(node_it)
            new.setExpanded(True)
            self.recur_set_widget(node_it)
    #    
    def old_group_selected_items(self,event): # cur위에 추가하고 cur끊고 new에 잇기
        self.save_push_log()
        root = self.invisibleRootItem()
        cur = self.currentItem()
        tar_p = cur.parent()
        
        # 0. Node List@@
        tar_p_lst, node_lst = [],[]
        if self.get_node_list(tar_p,node_lst):
            return

        # 1. Create New new
        new_info = []
        print(cur.name)
        if tar_p.isTop():
            new_info = ["top","New Group","","","","",]
        else:
            new_info = [cur.p_name,"New Group","","","","",]
        
        # 2. Connect tar_p & new
        new = TreeWidgetItem(self,tar_p,new_info)
        ix, new = self.extract_item(new)
        self.connect_tar_new(tar_p,cur,new,Indi.up.value)

        # 3. Disconnect tar_p & tar
        indi = Indi.up.value
        for node_it in node_lst:
            ix, indp_it = self.extract_item(node_it)
            self.change_parent(tar_p, indp_it, new, indi)
        
        # 4. Connect new & tar    
    def ungroup_selected_items(self,event): # 가운데 추출 후 양 쪽 잇기
        self.save_push_log()
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
        name = item.text(0)

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
            if tar.isGroup():
                self.change_parent(tar,tar,item,Indi.md.value)
            else:
                return
        else:
            if tar.isTop():
                self.change_parent("top",tar,item,Indi.md.value)
            else:
                self.change_parent(new_p,tar,item,Indi.md.value)
        # connect 잘 해줘야
        # item.mouse_tog_btn.signal.connect(lambda:item.toggle_typ_mouse())
        # 아이템이 그룹일 때
        # - M일때/K일때
        # 아이템이 명령일 떄
        # -Top일 때/아닐 때
        #if self.isGroup(item):
        #    item.mouse_tog_btn = ps.TypBtn(self,item.text(1))
        #    item.key_tog_btn = ps.ActCb(self,item.text(1),item.text(2))
        #    self.setItemWidget(item, 1, item.mouse_tog_btn)
        #    self.setItemWidget(item, 2, item.key_tog_btn)
        #    if item.text(1) == "M":
        #        coor = item.pos_cp.coor.text()
        #        item.pos_cp = ps.PosWidget(coor)
        #        # 이동해도, item을 새로 만드는 것이기 때문에, connect도 다시 해줘야한다
        #        # 추후 class init할 때 connect 하도록 수정할 필요있음
        #        item.pos_cp.btn.clicked.connect(lambda ignore,f=item.pos_cp.get_pos:f())                  
        #        self.setItemWidget(item, 3, item.pos_cp)
        #    item.mouse_tog_btn.signal.connect(lambda:item.toggle_typ_mouse())
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
            
    def change_parent_plus(self, tar_p, tar, it, indi,mod=""):
        if indi == Indi.md.value:
            if tar.isGroup():
                self.change_parent(tar,tar,it,indi)
            else:
                return
        else:
            if tar.isTop():
                self.change_parent("top",tar,it,indi)
            else:
                self.change_parent(tar_p,tar,it,indi)         
    
    # it : 최종 child, tar : 최종 parent
    
    def extract_and_connect(self,it):
        indi = Indi.dw.value
        if it.isGroup():
            for ix in range(it.childCount()):
                it_ch = it.child(0) # change parent에서 takechild 수행하면서 child가 삭제되므로 0으로 받기
                it_p = it.parent()
                self.change_parent(it_p, it, it_ch, indi)
        else:
            if it.isTop():
                return False
            else:
                it_gp = (it.parent()).parent()
                it_p = it.parent()
                self.change_parent(it_gp, it_p, it, indi)
        return True
    
    def change_parent(self, tar_p, tar, it, indi, mod=""):
        if tar.isTop():
            tar_p = "top"
        # Step 01 : 독립 it 만들기
        ix, indp_it = self.extract_item(it)
        # Step 02 : tar_p에 잇기
        self.connect_tar_new(tar_p,tar,indp_it,indi)
        # Step 03 : item 재정비
        self.recur_set_widget(indp_it)
        #mod == Qt.ControlModifier:
            
    def extract_item(self,it):
        # Step 01 : 독립 it 만들기
        if it.isTop():
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
            indp_it.p_name = "top"
            #ungroup에만 쓰이고, item move에 안쓰임
            if indi == Indi.up.value or Indi.md.value: 
                self.insertTopLevelItem(ix,indp_it)
            else:
                self.insertTopLevelItem(ix+1,indp_it)
        else:
            indp_it.p_name = tar_p.name
            if indi == Indi.up.value or Indi.md.value: 
                tar_p.insertChild(ix,indp_it)
            else:
                tar_p.insertChild(ix+1,indp_it) 
    
    def connect_tar_new(self,tar_p,tar,indp_it,indi):
        if tar_p == "top":
            indp_it.p_name = "top"
            #ungroup에만 쓰이고, item move에 안쓰임
            if indi == Indi.up.value or Indi.md.value: 
                ix = self.indexOfTopLevelItem(tar)
                self.insertTopLevelItem(ix,indp_it)
            else:
                ix = self.indexOfTopLevelItem(tar)
                self.insertTopLevelItem(ix+1,indp_it)
        else:
            ix = tar_p.indexOfChild(tar)
            indp_it.p_name = tar_p.name
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
        self.save_push_log()

        if event.source() == self:
            mod = event.keyboardModifiers()
            # Extract node_it list
            tar_p_lst, node_lst = [], []
            if self.get_node_list(tar_p, node_lst):
                return

            for item in node_lst:
                self.change_parent_plus(tar_p, tar, item, indi, mod)
                event.acceptProposedAction()
            #if (modifiers & Qt.ControlModifier) and (modifiers & Qt.ShiftModifier):
            #    print("Control+Shift")   
    # 문제 : group,inst가 위계없이 items에 다 들어가는 중. (왜냐하면, group,inst를 구분하는 코드는 없고, text(1)을 기준으로 나누기 때문에) 중복을 제외하고 넘기기
    # n,0 (role은 0으로  고정하고 n은 0~4)
    
    def get_node_list(self,new_p,node_lst):
        items = self.selectedItems()
        sel_lst = [it.name for it in items]
        for it in items:
            if it.p_name not in sel_lst:
                node_lst.append(it)

        # new_p == nonetype
        if isinstance(new_p,NoneType):
            return False
        else:
            for node_it in node_lst:
                if node_it.name == new_p.name:
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
                if t_it.checkState(0) == Qt.Checked: # check 된 것만 돌기
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
                child.setCheckState(0, Qt.Checked)
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
                top_item = self.topLevelItem(ix)
                if top_item:
                    insts.append(["top", top_item.text(0), "", "", "", ""])
                    if top_item.childCount():
                        self.recur_get_info(insts, top_item)
                
            writer.writerow(insts)
                
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
            if ch.mouse_tog_btn:
                inst[2] = ch.mouse_tog_btn.text()
                if inst[2] == "M":
                    inst[3] = ch.key_tog_btn.currentText()
                    inst[4] = ch.pos_cp.coor.text()
                else:
                    inst[3] = ch.key_tog_btn.currentText()
                    inst[4] = ch.text(3)
            insts.append(inst)
            self.recur_get_info(insts,ch)
        return
    
    def recur_child_exec(self,parent,lst):
        for ix in range(parent.childCount()):
            child = parent.child(ix)
            if child.checkState(0) != Qt.Checked:
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