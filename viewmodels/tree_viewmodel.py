# macro_tree/viewmodels/tree_viewmodel.py
from PyQt5.QtCore import QObject, pyqtProperty, pyqtSignal, pyqtSlot
from core.tree_executor import TreeExecutor
from core.tree_state import TreeState

class TreeViewModel(QObject):
    dataChanged = pyqtSignal()
    
    def __init__(self, tree_executor: TreeExecutor):
        super().__init__()
        self._tree_executor = tree_executor
        self._tree_state = None
        
    @pyqtProperty(object, notify=dataChanged)
    def treeState(self):
        return self._tree_state
        
    @treeState.setter
    def treeState(self, value):
        self._tree_state = value
        self.dataChanged.emit()
    
    @pyqtSlot(str)
    def executeItem(self, item_id: str):
        self._tree_executor.execute_item(item_id)
        self.dataChanged.emit()