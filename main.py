"""메인 애플리케이션 모듈

이 모듈은 애플리케이션의 메인 윈도우를 정의하고 실행합니다.
"""
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow
from package.ui import UI


class MainWindow(QMainWindow):
    """메인 윈도우 클래스
    
    애플리케이션의 주 윈도우를 관리하는 클래스입니다.
    """
    
    def __init__(self, app: QApplication) -> None:
        """MainWindow 클래스의 생성자
        
        Args:
            app: QApplication 인스턴스
        """
        super().__init__()
        main_ui = UI(self, app)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    main = MainWindow(app)
    main.show()
    app.exec_()
    sys.exit(app.exec_())