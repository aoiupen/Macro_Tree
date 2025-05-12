from PyQt6.QtWidgets import QVBoxLayout, QWidget, QPushButton
from viewmodel.impl.tree_viewmodel import MTTreeViewModel
from view.impl.tree_widget import MTTreeWidget
from core.interfaces.base_item_data import MTNodeType

class TreeView(QWidget):
    def __init__(self, viewmodel: MTTreeViewModel, parent=None):
        super().__init__(parent)
        self._viewmodel = viewmodel
        self.layout = QVBoxLayout(self)
        self.add_button = QPushButton("항목 추가")
        self.add_button.clicked.connect(self.on_add_item)
        self.layout.addWidget(self.add_button)
        self.tree_widget = MTTreeWidget(self._viewmodel)
        self.layout.addWidget(self.tree_widget)
        self.setLayout(self.layout)

    def on_add_item(self):
        selected_items = self.tree_widget.selectedItems()
        parent_id = None
        if selected_items:
            parent_id = selected_items[0].data(0, 32)  # Qt.ItemDataRole.UserRole
        self._viewmodel.add_item('New Item', parent_id, node_type=MTNodeType.INSTRUCTION)

    def set_viewmodel(self, viewmodel):
        self._viewmodel = viewmodel
        self.tree_widget.set_viewmodel(viewmodel)

    def on_viewmodel_signal(self, signal_type, data):
        if signal_type == 'item_added':
            self.tree_widget.update_tree_items()
        elif signal_type == 'item_removed':
            self.tree_widget.update_tree_items()
        elif signal_type == 'item_moved':
            self.tree_widget.update_tree_items()
        # 필요시 추가 분기