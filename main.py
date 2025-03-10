import sys
from PyQt5.QtWidgets import QApplication, QMainWindow
from view.ui import UI  # ui 폴더를 view 폴더로 변경했습니다.
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