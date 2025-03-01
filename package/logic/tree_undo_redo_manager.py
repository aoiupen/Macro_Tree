from PyQt5.QtWidgets import QUndoCommand, QUndoStack

class TreeUndoCommand(QUndoCommand):
    def __init__(self, tree, old_state, new_state):
        super().__init__()
        self.tree = tree
        self.old_state = old_state
        self.new_state = new_state

    def undo(self):
        self.tree.restore_state(self.old_state)

    def redo(self):
        self.tree.restore_state(self.new_state)

class TreeUndoRedoManager:
    def __init__(self, tree_widget):
        self.tree_widget = tree_widget
        self.undo_stack = QUndoStack(tree_widget)

    def push_undo_command(self, old_state, new_state):
        self.undo_stack.push(TreeUndoCommand(self.tree_widget, old_state, new_state))

    def undo(self):
        self.undo_stack.undo()

    def redo(self):
        self.undo_stack.redo()