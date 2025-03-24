"""메인 애플리케이션 모듈

애플리케이션의 진입점을 제공합니다.
"""
import sys
import os
from PyQt6.QtWidgets import QApplication
from PyQt6.QtQml import QQmlApplicationEngine
from PyQt6.QtCore import QUrl, QObject, pyqtSlot
from PyQt6.QtGui import QFontDatabase

from viewmodels.tree_viewmodel import TreeViewModel
from viewmodels.tree_data_repository_viewmodel import TreeDataRepositoryViewModel
from view.tree_event_handler import TreeEventHandler
from viewmodels.tree_executor import TreeExecutor
from dotenv import load_dotenv

# 환경변수 로드
load_dotenv()

class TreeBusinessLogic(QObject):
    """트리 관련 비즈니스 로직을 QML에 노출하는 클래스"""
    
    def __init__(self, repository_viewmodel, tree_viewmodel=None, parent=None):
        super().__init__(parent)
        self._repository_viewmodel = repository_viewmodel
        self._tree_viewmodel = tree_viewmodel
        self._executor = TreeExecutor()
    
    @pyqtSlot(result=bool)
    def saveTree(self):
        """현재 트리를 저장합니다."""
        if self._repository_viewmodel:
            current_state = self._repository_viewmodel.get_current_state()
            if current_state:
                return self._repository_viewmodel.save_tree(current_state)
        return False
    
    @pyqtSlot(result=bool)
    def executeSelectedItems(self):
        """선택된 항목을 실행합니다."""
        if not self._tree_viewmodel:
            return False
            
        # 선택된 아이템 가져오기
        selected_ids = self._tree_viewmodel.get_selected_items()
        if not selected_ids:
            print("실행할 항목이 선택되지 않았습니다.")
            return False
            
        success = True
        for item_id in selected_ids:
            # 아이템 가져오기
            item = self._tree_viewmodel.get_item(item_id)
            if item:
                # 아이템 실행
                try:
                    self._executor.execute_item(item)
                except Exception as e:
                    print(f"아이템 실행 오류: {e}")
                    success = False
        
        return success

def main():
    """애플리케이션 메인 함수"""
    try:
        # PyQt 애플리케이션 생성
        app = QApplication(sys.argv)
        
        # 폰트 설정
        QFontDatabase.addApplicationFont("resources/fonts/NanumGothic.ttf")
        
        # QML 엔진 생성
        engine = QQmlApplicationEngine()
        
        # 저장소 뷰모델 생성
        repository_viewmodel = TreeDataRepositoryViewModel()
        
        # 트리 뷰모델 생성
        tree_viewmodel = TreeViewModel()
        
        # 이벤트 핸들러 생성
        event_handler = TreeEventHandler(tree_viewmodel)
        
        # 비즈니스 로직 클래스 생성
        tree_business_logic = TreeBusinessLogic(repository_viewmodel, tree_viewmodel)
        
        # QML 컨텍스트에 필요한 객체 등록
        engine.rootContext().setContextProperty("_treeModel", tree_viewmodel)
        engine.rootContext().setContextProperty("_eventHandler", event_handler)
        engine.rootContext().setContextProperty("_repository", repository_viewmodel)
        engine.rootContext().setContextProperty("_treeBusinessLogic", tree_business_logic)
        
        # 초기 데이터 로드
        if repository_viewmodel.load_tree_from_db():
            current_state = repository_viewmodel.get_current_state()
            if current_state:
                tree_viewmodel.restore_state(current_state)
        
        # QML 파일 로드
        qml_file = os.path.join(os.path.dirname(__file__), "view", "qml", "main.qml")
        engine.load(QUrl.fromLocalFile(qml_file))
        
        # 로드 실패 처리
        if not engine.rootObjects():
            print("QML 파일을 로드할 수 없습니다:", qml_file)
            return 1
        
        # 애플리케이션 실행
        return app.exec()
    except Exception as e:
        print(f"애플리케이션 실행 오류: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())