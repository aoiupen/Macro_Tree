from typing import Dict, Any # Optional removed
from model.store.repo.interfaces.base_tree_repo import IMTStore
from core.interfaces.base_tree import IMTTree

class StoreManager:
    def __init__(self, repository: IMTStore):
        self._repository = repository

    def save(self, tree: IMTTree, tree_id: str | None = None) -> str:
        return self._repository.save(tree, tree_id)

    def load(self, tree_id: str) -> IMTTree | None:
        return self._repository.load(tree_id)

    def delete(self, tree_id: str) -> bool:
        result = self._repository.delete(tree_id)
        return bool(result)

    def list_trees(self) -> Dict[str, str]:
        result = self._repository.list_trees()
        return dict(result) 