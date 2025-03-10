"""트리 실행 취소/재실행 관리 모듈

트리 위젯의 실행 취소/재실행 기능을 관리하는 클래스를 제공합니다.
"""
from PyQt5.QtWidgets import QUndoCommand, QUndoStack
from core.tree_state import TreeState


class TreeUndoCommand(QUndoCommand):
    """트리 실행 취소 명령 클래스
    
    트리 상태 변경에 대한 실행 취소/재실행을 처리합니다.
    """

    def __init__(self, tree, old_state: TreeState, new_state: TreeState) -> None:
        """TreeUndoCommand 생성자
        
        Args:
            tree: 트리 위젯 인스턴스
            old_state: 이전 트리 상태
            new_state: 새로운 트리 상태
        """
        super().__init__()
        self.tree = tree
        self.old_state = old_state
        self.new_state = new_state
        self.setText("트리 상태 변경")
    
    def undo(self) -> None:
        """실행 취소 작업을 수행합니다."""
        self.tree.restore_state(self.old_state)
    
    def redo(self) -> None:
        """다시 실행 작업을 수행합니다."""
        self.tree.restore_state(self.new_state)


class TreeUndoRedoManager:
    """트리 실행 취소/재실행 관리 클래스
    
    트리 위젯의 실행 취소/재실행 기능을 관리합니다.
    """
    
    def __init__(self, tree_widget) -> None:
        """TreeUndoRedoManager 생성자
        
        Args:
            tree_widget: 관리할 트리 위젯 인스턴스
        """
        self.tree = tree_widget
        self.command_stack = QUndoStack()
    
    def push_undo_command(self, old_state: TreeState, new_state: TreeState) -> None:
        """실행 취소 명령을 스택에 추가합니다.
        
        Args:
            old_state: 이전 트리 상태
            new_state: 새로운 트리 상태
        """
        command = TreeUndoCommand(self.tree, old_state, new_state)
        self.command_stack.push(command)
    
    def undo(self) -> None:
        """마지막 작업을 실행 취소합니다."""
        self.command_stack.undo()
    
    def redo(self) -> None:
        """마지막으로 실행 취소된 작업을 다시 실행합니다."""
        self.command_stack.redo() 