from typing import Optional, Dict, Any
from model.store.repo.interfaces.base_tree_repo import IMTStore

class StoreManager:
    def __init__(self, repository: IMTStore):
        self._repository = repository

    def save(self, tree_dict: dict, tree_id: Optional[str] = None) -> str:
        result = self._repository.save(tree_dict, tree_id)
        return str(result)

    def load(self, tree_id: str) -> Optional[dict]:
        result = self._repository.load(tree_id)
        return result if isinstance(result, dict) or result is None else None

    def delete(self, tree_id: str) -> bool:
        result = self._repository.delete(tree_id)
        return bool(result)

    def list_trees(self) -> Dict[str, str]:
        result = self._repository.list_trees()
        return dict(result) 