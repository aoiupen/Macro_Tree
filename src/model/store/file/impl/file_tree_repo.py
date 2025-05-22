import json
import os
from typing import Dict, Any # Optional removed
import uuid
from core.interfaces.base_tree import IMTTree
from core.impl.tree import MTTree
from model.store.repo.interfaces.base_tree_repo import IMTStore

class MTFileTreeRepository(IMTStore):
    """파일 기반 트리 저장소 구현체"""
    
    def __init__(self, storage_dir: str = "./trees"):
        """저장소 초기화
        
        Args:
            storage_dir: 트리 파일 저장 경로
        """
        self.storage_dir = storage_dir
        os.makedirs(storage_dir, exist_ok=True)
    
    def _get_file_path(self, tree_id: str) -> str:
        """트리 ID로부터 파일 경로를 생성합니다."""
        return os.path.join(self.storage_dir, f"{tree_id}")
    
    def save(self, tree: IMTTree, tree_id: str | None = None) -> str:
        """트리를 파일로 저장합니다."""
        if tree_id is None:
            if hasattr(tree, 'id') and tree.id: 
                tree_id = tree.id
            else:
                tree_id = str(uuid.uuid4())
        
        tree_dict = tree.to_dict()
        json_str = json.dumps(tree_dict, ensure_ascii=False, indent=2)
        with open(self._get_file_path(tree_id), 'w', encoding='utf-8') as file:
            file.write(json_str)
        return tree_id
    
    def load(self, tree_id: str) -> IMTTree | None:
        """파일로부터 트리를 로드합니다."""
        file_path = self._get_file_path(tree_id)
        
        if not os.path.exists(file_path):
            return None
        
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                json_str = file.read()

            tree_data_dict = json.loads(json_str)
            return MTTree.from_dict(tree_data_dict)
        except Exception as e:
            print(f"트리 로드 실패: {e}")
            return None
    
    def delete(self, tree_id: str) -> bool:
        """트리 파일을 삭제합니다."""
        file_path = self._get_file_path(tree_id)
        
        if not os.path.exists(file_path):
            return False
        
        try:
            os.remove(file_path)
            return True
        except Exception as e:
            print(f"트리 삭제 실패: {e}")
            return False
    
    def list_trees(self) -> Dict[str, str]:
        """저장된 모든 트리 목록을 반환합니다."""
        result = {}
        
        for filename in os.listdir(self.storage_dir):
            if filename.endswith(".json"):
                tree_id = filename[:-5]  # .json 확장자 제거
                
                try:
                    tree_obj = self.load(tree_id)
                    if tree_obj and hasattr(tree_obj, 'name') and tree_obj.name:
                        result[tree_id] = tree_obj.name
                    elif tree_obj:
                        result[tree_id] = tree_id
                    else:
                        result[tree_id] = f"Failed to load {tree_id}"
                except Exception:
                    result[tree_id] = f"Error processing {tree_id}"
        
        return result