from platforms.adapters.adapter import IMTPlatformAdapter
from viewmodel.interfaces.base_tree_viewmodel_core import IMTTreeViewModelCore
from PyQt6.QtWidgets import QTreeView, QWidget

"""
[Adapter 계층 설명]
이 클래스는 PyQt의 QTreeWidget 이벤트(itemClicked 등)를
공통 UI 이벤트 Enum(MTTreeUIEvent)으로 변환하여
ViewModel에 전달하는 Adapter 역할을 합니다.

아키텍처 계층 구조:
[PyQt 위젯] → [PyQtTreeAdapter] → [ViewModel] → [Model]
여러 프론트엔드(웹 등)와의 확장성을 위해 Adapter 패턴을 사용합니다.
"""
class PyQtAdapter(IMTPlatformAdapter):
    """PyQt용 플랫폼 어댑터 구현"""
    
    def __init__(self, viewmodel: IMTTreeViewModelCore):
        """어댑터 초기화"""
        self._viewmodel = viewmodel
    
    # 메서드 구현...
