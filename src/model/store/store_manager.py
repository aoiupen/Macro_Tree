from typing import Optional, Dict, Any
from model.store.repo.interfaces.base_tree_repo import IMTStore

class StoreManager:
    def __init__(self, repository: IMTStore):
        self._repository = repository

    def save(self, tree_dict: dict, tree_id: Optional[str] = None) -> str:
        return self._repository.save(tree_dict, tree_id)

    def load(self, tree_id: str) -> Optional[dict]:
        return self._repository.load(tree_id)

    def delete(self, tree_id: str) -> bool:
        return self._repository.delete(tree_id)

    def list_trees(self) -> Dict[str, str]:
        return self._repository.list_trees() 