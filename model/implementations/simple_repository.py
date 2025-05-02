import json
import os
from typing import Dict, Any, Optional

class SimpleRepository:
    """간단한 파일 기반 저장소 구현"""
    
    def __init__(self, base_path: str = "./data"):
        self.base_path = base_path
        os.makedirs(base_path, exist_ok=True)
    
    def save(self, tree_id: str, data: Dict[str, Any]) -> str:
        """트리 데이터를 파일로 저장"""
        file_path = os.path.join(self.base_path, f"{tree_id}.json")
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return tree_id
    
    def load(self, tree_id: str) -> Optional[Dict[str, Any]]:
        """저장된 트리 데이터 로드"""
        file_path = os.path.join(self.base_path, f"{tree_id}.json")
        if not os.path.exists(file_path):
            return None
        
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def list_trees(self) -> Dict[str, str]:
        """저장된 모든 트리 목록 반환"""
        result = {}
        for filename in os.listdir(self.base_path):
            if filename.endswith('.json'):
                tree_id = filename.rsplit('.', 1)[0]
                # 메타데이터 추출 (첫 번째 아이템의 이름 등)
                tree_data = self.load(tree_id)
                name = "Unnamed Tree"
                if tree_data and len(tree_data) > 0:
                    first_item = next(iter(tree_data.values()))
                    name = first_item.get("name", name)
                result[tree_id] = name
        return result
    
    def delete(self, tree_id: str) -> bool:
        """저장된 트리 삭제"""
        file_path = os.path.join(self.base_path, f"{tree_id}.json")
        if os.path.exists(file_path):
            os.remove(file_path)
            return True
        return False
