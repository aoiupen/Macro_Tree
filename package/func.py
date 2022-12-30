import csv
import pandas as pd
import pyautogui as pag
from openpyxl import load_workbook
from requests import delete
from package import tree as tr

'''
def write_csv(self,p,ch_it):
    lst = [ch_it.text(i) for i in range(self.tw.columnCount())] #text로 접근하기보다, widget으로 접근하는게 맞음
    if ch_it.text(1) == "Mouse":
        lst[3] = ch_it.pos_cp.coor.text()
    lst.insert(0,p.text(0))     
    writer.writerow(lst)
'''
