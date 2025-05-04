import json
import os
from typing import Any, Dict
from uuid import uuid4

from core.interfaces.base_tree import IMTTree
from model.tree_repo import IMTTreeRepository


class SimpleTreeRepository(IMTTreeRepository):
    """파일 기반 트리 저장소"""
    
    def __init__(self, directory_path: str = "./data"):
        """저장소 초기화"""
        self.directory = directory_path
        os.makedirs(directory_path, exist_ok=True)
    
    def save(self, tree: IMTTree, name: str | None = None) -> str:
        """트리를 저장합니다."""
        tree_data = tree.to_dict()
        
        # 이름이 제공되지 않으면 트리 이름 사용
        if name is None:
            name = tree_data.get("name", "Unnamed Tree")
        
        # 저장 파일명 생성
        tree_id = tree_data.get("id", str(uuid4()))
        filename = f"{tree_id}.json"
        file_path = os.path.join(self.directory, filename)
        
        # JSON으로 저장
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(tree_data, f, ensure_ascii=False, indent=2)
        
        return tree_id
    
    def load(self, identifier: str | None = None) -> IMTTree:
        """트리를 불러옵니다."""
        # 식별자가 없으면 가장 최근 파일 사용
        if identifier is None:
            files = os.listdir(self.directory)
            json_files = [f for f in files if f.endswith('.json')]
            
            if not json_files:
                raise ValueError("저장된 트리가 없습니다.")
            
            # 최신 파일 (수정 시간 기준)
            json_files.sort(key=lambda x: os.path.getmtime(os.path.join(self.directory, x)), reverse=True)
            filename = json_files[0]
        else:
            filename = f"{identifier}.json"
        
        file_path = os.path.join(self.directory, filename)
        
        # 파일 존재 확인
        if not os.path.exists(file_path):
            raise ValueError(f"트리 파일을 찾을 수 없습니다: {filename}")
        
        # JSON 파일 로드
        with open(file_path, 'r', encoding='utf-8') as f:
            tree_data = json.load(f)
        
        # 트리 객체 생성
        from core.impl.tree import SimpleTree
        return SimpleTree.from_dict(tree_data)
    
    def delete(self, identifier: str) -> bool:
        """저장된 트리를 삭제합니다."""
        filename = f"{identifier}.json"
        file_path = os.path.join(self.directory, filename)
        
        if os.path.exists(file_path):
            os.remove(file_path)
            return True
        
        return False
    
    def to_json(self, tree: IMTTree) -> str:
        """트리를 JSON 문자열로 변환합니다."""
        tree_data = tree.to_dict()
        return json.dumps(tree_data, ensure_ascii=False, indent=2)
    
    def from_json(self, json_str: str) -> IMTTree:
        """JSON 문자열에서 트리를 생성합니다."""
        try:
            tree_data = json.loads(json_str)
            from core.impl.tree import SimpleTree
            return SimpleTree.from_dict(tree_data)
        except json.JSONDecodeError as e:
            raise ValueError(f"잘못된 JSON 형식: {str(e)}")
