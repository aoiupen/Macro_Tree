"""메인 애플리케이션 모듈

애플리케이션의 진입점을 제공합니다.
"""
import sys
import os
from PyQt6.QtWidgets import QApplication
from PyQt6.QtQml import QQmlApplicationEngine, QQmlContext
from PyQt6.QtCore import QUrl, QObject, pyqtSlot, pyqtSignal, QVariant
from PyQt6.QtGui import QFontDatabase

from viewmodels.tree_viewmodel import TreeViewModel
from viewmodels.tree_data_repository_viewmodel import TreeDataRepositoryViewModel
from view.tree_event_handler import TreeEventHandler
from viewmodels.tree_executor import TreeExecutor
from core.tree_state import TreeState
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
        """선택된 아이템을 실행합니다."""
        if self._tree_viewmodel:
            selected_items = self._tree_viewmodel.get_selected_items()
            if selected_items and len(selected_items) > 0:
                result = False
                for item_id in selected_items:
                    # 하나라도 성공하면 True
                    success = self._executor.execute_item(item_id)
                    result = result or success
                return result
        return False

# QML 디버깅을 위한 브리지 클래스
class QmlBridge(QObject):
    """QML과 Python 간의 연결을 위한 브리지 클래스"""
    
    # 시그널 정의
    modelUpdated = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.tree_view_model = None
        self.repository_view_model = None
    
    def set_models(self, tree_vm, repo_vm):
        """모델 참조를 설정합니다."""
        self.tree_view_model = tree_vm
        self.repository_view_model = repo_vm
        
        # 시그널 연결
        if self.tree_view_model:
            self.tree_view_model.stateChanged.connect(self.handle_state_changed)
        
        if self.repository_view_model:
            self.repository_view_model.dataLoaded.connect(self.handle_data_loaded)
    
    @pyqtSlot()
    def handle_state_changed(self):
        """트리 상태 변경 시 호출됩니다."""
        print("QmlBridge: 트리 상태가 변경되었습니다.")
        self.modelUpdated.emit()
    
    @pyqtSlot(TreeState)
    def handle_data_loaded(self, tree_state):
        """데이터 로드 시 호출됩니다."""
        print(f"QmlBridge: 데이터가 로드되었습니다. 노드 수: {len(tree_state.nodes)}")
        
        # 모델에 반영되었는지 확인
        if self.tree_view_model:
            self.tree_view_model.restore_state(tree_state)
            print("QmlBridge: 트리 뷰모델에 상태가 복원되었습니다.")
        
        self.modelUpdated.emit()
    
    @pyqtSlot(result=str)
    def dump_model_info(self):
        """모델 정보를 덤프합니다."""
        if not self.tree_view_model:
            return "트리 뷰모델이 없습니다."
        
        result = "트리 모델 정보:\n"
        
        try:
            # 트리 상태 정보
            state = self.tree_view_model.get_current_state()
            if state:
                node_count = len(state.nodes) if state.nodes else 0
                struct_count = len(state.structure) if state.structure else 0
                result += f"- 노드 수: {node_count}\n"
                result += f"- 구조 항목 수: {struct_count}\n"
                
                # 노드 ID 목록
                if node_count > 0:
                    result += f"- 노드 ID: {', '.join(list(state.nodes.keys())[:5])}...\n"
                
                # 루트 노드 정보
                root_nodes = state.structure.get(None, [])
                result += f"- 루트 노드 수: {len(root_nodes)}\n"
                if root_nodes:
                    result += f"- 루트 노드 ID: {', '.join(root_nodes)}\n"
                    
                    # 첫 번째 루트 노드의 자세한 정보
                    if root_nodes[0] in state.nodes:
                        root_data = state.nodes[root_nodes[0]]
                        result += f"- 첫 번째 루트 노드 이름: {root_data.get('name', '이름 없음')}\n"
            else:
                result += "- 상태 객체가 없습니다.\n"
        except Exception as e:
            result += f"- 정보 수집 중 오류: {e}\n"
        
        return result

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
        
        # QML 브리지 생성 및 설정
        qml_bridge = QmlBridge()
        qml_bridge.set_models(tree_viewmodel, repository_viewmodel)
        
        # QML 컨텍스트에 필요한 객체 등록
        engine.rootContext().setContextProperty("_treeModel", tree_viewmodel)
        engine.rootContext().setContextProperty("_eventHandler", event_handler)
        engine.rootContext().setContextProperty("_repository", repository_viewmodel)
        engine.rootContext().setContextProperty("_treeBusinessLogic", tree_business_logic)
        engine.rootContext().setContextProperty("_qmlBridge", qml_bridge)
        
        # 디버깅 정보 출력
        print("\n===== 애플리케이션 초기화 =====")
        print(f"트리 뷰모델: {tree_viewmodel}")
        print(f"저장소 뷰모델: {repository_viewmodel}")
        print(f"이벤트 핸들러: {event_handler}")
        
        # 초기 데이터 로드
        print("\n===== 초기 데이터 로드 =====")
        if repository_viewmodel.load_tree_from_db():
            print("데이터베이스에서 트리를 성공적으로 로드했습니다.")
            current_state = repository_viewmodel.get_current_state()
            if current_state:
                print(f"로드된 트리 노드 수: {len(current_state.nodes)}")
                tree_viewmodel.restore_state(current_state)
                print("트리 뷰모델에 상태를 복원했습니다.")
            else:
                print("현재 상태가 없습니다.")
        else:
            print("데이터베이스에서 트리를 로드하지 못했습니다.")
        
        # QML 파일 로드
        qml_file = os.path.join(os.path.dirname(__file__), "view", "qml", "main.qml")
        engine.load(QUrl.fromLocalFile(qml_file))
        
        # 로드 실패 처리
        if not engine.rootObjects():
            print("QML 파일을 로드할 수 없습니다:", qml_file)
            return 1
        
        print("\n===== QML 로드 완료 =====")
        
        # 애플리케이션 실행
        return app.exec()
    except Exception as e:
        print(f"애플리케이션 실행 오류: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())