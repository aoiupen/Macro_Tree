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
'''
# selected items -> 마지막에 선택된 item의 부모 밑에 Group 폴더를 만듦
# selected items는 기존의 위치에서 삭제됨
# selected items들에서 item without parent 뽑아냄
# 현재의 parent에서 새로 group 생성(생성후에 lineedit 수정 상태로)
# 새로 생성한 group가 addchild(item without parent)하기

def fillItem(self, inItem, outItem):
        for col in range(inItem.columnCount()):
            for key in range(Qt.UserRole):
                role = Qt.ItemDataRole(key)
                outItem.setData(col, role, inItem.data(col, role))
                
        # *drop event로 Data를 먼저 옮기고, if문 이하에서 item setting
        print(inItem.typ_cb)
        print(inItem.act_cb)
        print(inItem.pos_wid)
        if not outItem.typ_cb: # Group이면 부모 재설정 new_parent(tar)인자를 받아서
            #outItem.p = tar
            outItem.p_name = outItem.text(0) 
            #tar.insertChild(0,drag_item) # 인덱스는 임시로 0
        else:
            outItem.typ_cb = ps.TypCb(self,outItem.text(1))
            outItem.act_cb = ps.ActCb(outItem.text(1),outItem.text(2))
            self.setItemWidget(outItem, 1, outItem.typ_cb)
            self.setItemWidget(outItem, 2, outItem.act_cb)
            if outItem.text(1) == "Mouse":
                coor = outItem.text(3)
                outItem.pos_wid = ps.PosWidget(coor)
                # 이동해도, item을 새로 만드는 것이기 때문에, connect도 다시 해줘야한다.
                # 추후 class init할 때 connect 하도록 수정할 필요있음
                outItem.pos_wid.btn.clicked.connect(lambda ignore,f=outItem.pos_wid.get_pos:f())                  
                self.setItemWidget(outItem, 3, outItem.pos_wid)
            outItem.typ_cb.signal.connect(lambda:outItem.toggle_mouse())
        child_cnt = outItem.childCount()
        # 단,group이어도 group 자신만 dropevent만하고, 자식들은 move_itemwidget 거치도록       

    def fillItems(self, itFrom, itTo):
        for ix in range(itFrom.childCount()):
            ch = itFrom.child(ix)
            it = TreeWidgetItem(self,itTo)
            it.pos_wid = ch.pos_wid
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

        
    elif isinstance(event.source(), QTreeWidget): # 타 widget으로 drop  
                if event.mimeData().hasFormat(TreeWidget.customMimeType):
                    encoded = event.mimeData().data(TreeWidget.customMimeType)
                    items = self.decodeData(encoded, event.source())
                    for it in items:
                        # QTree->TreeWidgetItem?
                        new_it = TreeWidgetItem(self,tar)
                        new_it.pos_wid = it.pos_wid
                        new_it.act_cb = it.act_cb
                        new_it.typ_cb = it.typ_cb
                        
                        #self.fillItem(it, new_it)
                        #self.fillItems(it, new_it)
                    event.acceptProposedAction()
'''