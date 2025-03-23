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
    
    # 모델과 이벤트 핸들러 생성
    tree_model = TreeViewModel()
    event_handler = TreeEventHandler(tree_model)
    
    # QML 컨텍스트에 객체 등록
    engine.rootContext().setContextProperty("_stateManager", state_manager)
    engine.rootContext().setContextProperty("_treeModel", tree_model)
    engine.rootContext().setContextProperty("_eventHandler", event_handler)
    
    # QML 파일 로드
    qml_file = os.path.join(os.path.dirname(__file__), "view", "qml", "main.qml")
    engine.load(QUrl.fromLocalFile(qml_file))
    
    # 애플리케이션 실행
    sys.exit(app.exec())