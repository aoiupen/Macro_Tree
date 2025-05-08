"""메인 애플리케이션 모듈

애플리케이션의 진입점을 제공합니다.
"""
import sys
from PyQt6.QtWidgets import QApplication
from viewmodel.impl.tree_viewmodel import MTTreeViewModel
from dotenv import load_dotenv
from view.impl.tree_app import main as tree_main

# 환경변수 로드
load_dotenv()

def main():
    """애플리케이션 메인 함수"""
    try:
        app = QApplication(sys.argv)
        viewmodel = MTTreeViewModel(None, None)
        # QML 연결이 필요할 때 아래 코드의 주석을 해제하세요.
        # engine = setup_qml_engine(viewmodel)
        return app.exec()
    except Exception as e:
        print(f"애플리케이션 실행 오류: {e}")
        return 1

if __name__ == "__main__":
    tree_main()