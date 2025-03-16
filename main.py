"""메인 애플리케이션 모듈

애플리케이션의 진입점을 제공합니다.
"""
import sys
from PyQt5.QtWidgets import QApplication
from view.main_window import MainWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)
    main = MainWindow(app)
    main.show()
    sys.exit(app.exec_())