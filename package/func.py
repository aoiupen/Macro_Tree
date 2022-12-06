import csv
import pandas as pd
import pyautogui as pag
from openpyxl import load_workbook
from requests import delete
from package import tree as tr

'''
def write_csv(self,parent,ch_it):
    lst = [ch_it.text(i) for i in range(self.tw.columnCount())] #text로 접근하기보다, widget으로 접근하는게 맞음
    if ch_it.text(1) == "Mouse":
        lst[3] = ch_it.pos_cp.coor.text()
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
                tw_item = tr.TreeWidgetItem(self.tw,parent,row)
                tw_item.prnt_name = 'top'
                tw_item.setText(0,name)
            else:
                for inst in self.insts:
                    if inst.text(0) == parent_str:   
                        parent = inst                        
                        tw_item = tr.TreeWidgetItem(self.tw,parent,row)
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
    self.tw.itemChanged.connect(get_item)

def set_cls_win(self):
    self.close() 