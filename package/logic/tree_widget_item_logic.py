class TreeWidgetItemLogic:
    def __init__(self, row):
        self.prnt = row[0]
        self.name = row[1]
        self.inp = row[2]
        self.__sub_con = row[3]
        self.sub = row[4]
        self.typ = "G" if self.is_group() else "I"

    def is_group(self):
        return self.inp == ""

    def is_inst(self):
        return self.inp != ""

    @property
    def sub_con(self):
        if self.__sub_con:
            return self.__sub_con
        else:
            return "Empty"

    @sub_con.setter
    def sub_con(self, value):
        self.__sub_con = value

    def toggle_input(self):
        if self.inp == "M":
            self.inp = "K"
        else:
            self.inp = "M"

    def toggle_subact(self):
        if self.inp == "M":
            if self.sub == "click":
                self.sub = "double"
            else:
                self.sub = "click"
        else:
            if self.sub == "typing":
                self.sub = "copy"
            elif self.sub == "copy":
                self.sub = "paste"
            else:
                self.sub = "typing"