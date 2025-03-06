import sys
from PyQt5.QtWidgets import QApplication, QMainWindow
from package.ui.ui import UI
#
class MainWindow(QMainWindow):
    def __init__(self,app):
        super().__init__()
        main_ui = UI(self,app)
        
if __name__ == "__main__":
    app = QApplication(sys.argv)
    main = MainWindow(app)
    main.show()
    sys.exit(app.exec_())