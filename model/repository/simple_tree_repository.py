import json
import os
import uuid
from typing import Dict, Any, Optional, List

from core.interfaces.base_tree import IMTTree
from core.impl.tree import MTTree
from model.tree_repo import IMTTreeRepository

class SimpleTreeRepository(IMTTreeRepository):
    """파일 기반 매크로 트리 저장소 구현"""
    
    def __init__(self, base_path: str = "./data"):
        self.base_path = base_path
        os.makedirs(base_path, exist_ok=True)
    
    def save(self, tree: IMTTree, name: Optional[str] = None) -> str:
        """트리를 저장합니다."""
        tree_id = str(tree.id) if name is None else name
        tree_data = self.to_json(tree)
        file_path = os.path.join(self.base_path, f"{tree_id}.json")
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(tree_data, f, indent=2, ensure_ascii=False)
        
        return tree_id
    
    def load(self, identifier: Optional[str] = None) -> IMTTree:
        """트리를 불러옵니다."""
        if identifier is None:
            # 가장 최근 파일 찾기
            files = self._list_tree_files()
            if not files:
                raise ValueError("저장된 트리가 없습니다.")
            identifier = sorted(files, key=lambda f: os.path.getmtime(
                os.path.join(self.base_path, f)))[-1].rsplit('.', 1)[0]
        
        file_path = os.path.join(self.base_path, f"{identifier}.json")
        if not os.path.exists(file_path):
            raise ValueError(f"트리를 찾을 수 없음: {identifier}")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            tree_data = json.load(f)
        
        return self.from_json(json.dumps(tree_data))
    
    def delete(self, identifier: str) -> bool:
        """저장된 트리를 삭제합니다."""
        file_path = os.path.join(self.base_path, f"{identifier}.json")
        if os.path.exists(file_path):
            os.remove(file_path)
            return True
        return False
    
    def to_json(self, tree: IMTTree) -> Dict[str, Any]:
        """트리를 JSON으로 변환합니다."""
        return tree.to_dict()
    
    def from_json(self, json_str: str) -> IMTTree:
        """JSON에서 트리를 생성합니다."""
        try:
            tree_data = json.loads(json_str)
            # 구현체에 맞게 수정 필요
            return MTTree.from_dict(tree_data)
        except json.JSONDecodeError as e:
            raise ValueError(f"잘못된 JSON 형식: {e}")
    
    def _list_tree_files(self) -> List[str]:
        """저장된 트리 파일 목록을 반환합니다."""
        return [f for f in os.listdir(self.base_path) if f.endswith('.json')]
