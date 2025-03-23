"""메인 애플리케이션 모듈

애플리케이션의 진입점을 제공합니다.
"""
import sys
import os
from PyQt6.QtWidgets import QApplication
from PyQt6.QtQml import QQmlApplicationEngine
from PyQt6.QtCore import QObject, QUrl

from core.tree_state_manager import TreeStateManager
from viewmodels.tree_viewmodel import TreeViewModel
from view.tree_event_handler import TreeEventHandler

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # 상태 관리자 생성
    state_manager = TreeStateManager()
    
    # QML 엔진 생성
    engine = QQmlApplicationEngine()
    
    # ViewModel 생성
    tree_model = TreeViewModel(state_manager)
    
    # QML 컨텍스트에 ViewModel만 등록
    engine.rootContext().setContextProperty("viewModel", tree_model)
    
    # QML 파일 로드
    qml_file = os.path.join(os.path.dirname(__file__), "view", "qml", "main.qml")
    engine.load(QUrl.fromLocalFile(qml_file))
    
    # TreeEventHandler는 QML에서 직접 생성하지 않고, 
    # Widget 생성 시 함께 생성되도록 구조 개선 필요
    
    # 애플리케이션 실행
    sys.exit(app.exec())