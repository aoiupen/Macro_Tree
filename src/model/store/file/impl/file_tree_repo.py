import json
import os
from typing import Dict, Optional, Any
import uuid

class MTFileTreeRepository:
    """파일 기반 트리 저장소 구현체 (직렬화/역직렬화는 Core에서 담당)"""
    
    def __init__(self, storage_dir: str = "./trees"):
        """저장소 초기화
        
        Args:
            storage_dir: 트리 파일 저장 경로
        """
        self.storage_dir = storage_dir
        os.makedirs(storage_dir, exist_ok=True)
    
    def _get_file_path(self, tree_id: str) -> str:
        """트리 ID로부터 파일 경로를 생성합니다."""
        return os.path.join(self.storage_dir, f"{tree_id}.json")
    
    def save(self, tree_dict: dict, tree_id: str | None = None) -> str:
        """트리를 파일로 저장합니다."""
        if tree_id is None:
            tree_id = str(uuid.uuid4())
        json_str = json.dumps(tree_dict, ensure_ascii=False, indent=2)
        with open(self._get_file_path(tree_id), 'w', encoding='utf-8') as file:
            file.write(json_str)
        return tree_id
    
    def load(self, tree_id: str) -> dict | None:
        """파일로부터 트리를 로드합니다."""
        file_path = self._get_file_path(tree_id)
        
        if not os.path.exists(file_path):
            return None
        
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                json_str = file.read()
            tree_data = json.loads(json_str)
            return tree_data
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
                    tree_data = self.load(tree_id)
                    if tree_data and 'name' in tree_data:
                        result[tree_id] = tree_data['name']
                    else:
                        result[tree_id] = f"Tree {tree_id}"
                except Exception:
                    result[tree_id] = f"Tree {tree_id}"
        
        return result