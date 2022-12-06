'''
self.tw2 = tr.TreeWidget(self)
self.tw2.setColumnCount(2)
self.tw2.setHeaderLabels(["Name","List"])
val_1 = tr.TreeWidgetItem(self.tw2,self.tw2)
val_1.setText(0,"val_a")
val_1.setText(1,"a,b,c,d,e,f,g,h,i,j,k")
val_1.setFlags(val_1.flags()|Qt.ItemIsEditable) #editable

val_2 = tr.TreeWidgetItem(self.tw2,self.tw2)
val_2.setText(0,"val_a")
val_2.setText(1,"a,b,c,d,e,f,g,h,i,j,k")
val_2.setFlags(val_2.flags()|Qt.ItemIsEditable) #editable

val_3 = tr.TreeWidgetItem(self.tw2,self.tw2)
val_3.setText(0,"val_a")
val_3.setText(1,"a,b,c,d,e,f,g,h,i,j,k")
val_3.setFlags(val_3.flags()|Qt.ItemIsEditable) #editable

self.tw.header().setStretchLastSection(True)
#self.tw.header().setSectionResizeMode(QHeaderView.ResizeToContents)
self.tw2.header().setStretchLastSection(True)
self.tw2.header().setSectionResizeMode(QHeaderView.ResizeToContents)
#self.ctr_lay.addWidget(self.tw2)
'''