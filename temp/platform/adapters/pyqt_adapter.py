from temp.platform.platform_adapter import IMTPlatformAdapter
from temp.viewmodel.tree_viewmodel import IMTTreeViewModel
from PyQt5.QtWidgets import QTreeView, QWidget

class PyQtAdapter(IMTPlatformAdapter):
    """PyQt용 플랫폼 어댑터 구현"""
    
    def __init__(self, viewmodel: IMTTreeViewModel):
        """어댑터 초기화"""
        self._viewmodel = viewmodel
    
    # 메서드 구현...
