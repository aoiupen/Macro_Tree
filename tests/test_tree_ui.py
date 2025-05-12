import pytest
from PyQt6.QtWidgets import QApplication, QTreeWidget, QTreeWidgetItem
from view.impl.tree_view import TreeView
from viewmodel.impl.tree_viewmodel import MTTreeViewModel

@pytest.fixture
def app(qtbot):
    return QApplication.instance() or QApplication([])

@pytest.fixture
def tree_view(app):
    # 간단한 트리와 뷰모델 생성
    viewmodel = MTTreeViewModel(tree=None)
    tree_view = TreeView(viewmodel)
    return tree_view

def test_item_clicked(qtbot, tree_view):
    # QTreeWidgetItem 추가
    item = QTreeWidgetItem(["Test Item"])
    tree_view.addTopLevelItem(item)
    # 시그널 직접 발생
    with qtbot.waitSignal(tree_view.itemClicked, timeout=1000):
        tree_view.itemClicked.emit(item, 0)
    # 추가 검증: ViewModel의 select_item이 호출됐는지 등
    # (실제 ViewModel에 Mock/Spy를 적용하면 더 정밀하게 검증 가능)

# 확장/축소 등도 같은 방식으로 테스트 가능 