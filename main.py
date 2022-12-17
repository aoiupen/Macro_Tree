import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from package import ui

class MainWindow(QMainWindow):
    def __init__(self,app):
        super().__init__()
        main_ui = ui.UI()
        main_ui.setup_ui(self,app)
        
if __name__ == "__main__":
    app = QApplication(sys.argv)
    main = MainWindow(app)
    main.show()
    app.exec_()