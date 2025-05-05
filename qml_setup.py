from PyQt6.QtQml import QQmlApplicationEngine
from PyQt6.QtCore import QUrl


def setup_qml_engine(viewmodel):
    engine = QQmlApplicationEngine()
    engine.rootContext().setContextProperty("treeViewModel", viewmodel)
    engine.load(QUrl.fromLocalFile("view/qml/main.qml"))
    if not engine.rootObjects():
        raise RuntimeError("QML 파일을 로드할 수 없습니다.")
    return engine
