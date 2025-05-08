from viewmodel.interfaces.base_tree_viewmodel_model import IMTTreeViewModelModel

class MTTreeViewModelModel(IMTTreeViewModelModel):
    def undo(self) -> bool:
        result = self._state_mgr.undo() is not None
        if result:
            self._notify_change()
        return result

    def redo(self) -> bool:
        result = self._state_mgr.redo() is not None
        if result:
            self._notify_change()
        return result

    def can_undo(self) -> bool:
        """실행 취소 가능 여부를 반환합니다."""
        return self._state_mgr.can_undo()
    
    def can_redo(self) -> bool:
        """다시 실행 가능 여부를 반환합니다."""
        return self._state_mgr.can_redo()

    def save_tree(self, tree_id: str | None = None) -> str | None:
        tree = self.get_current_tree()
        if not tree:
            return None
        try:
            saved_id = self._repository.save(tree, tree_id)
            return saved_id
        except Exception:
            return None

    def load_tree(self, tree_id: str) -> bool:
        try:
            tree = self._repository.load(tree_id)
            if tree:
                self._state_mgr.set_initial_state(tree)
                self._selected_items.clear()
                self._notify_change()
                return True
        except ValueError:
            pass
        return False 