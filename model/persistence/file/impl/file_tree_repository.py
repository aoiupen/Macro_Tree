import json
import os
from typing import Dict, Optional, Any, TypeVar, Type
import uuid

# 타입 참조만 가져옵니다
IMTTree = TypeVar('IMTTree')
from model.store.repo.interfaces.base_tree_repo import IMTTreeRepository, IMTTreeJSONSerializable

class MTFileTreeRepository(IMTTreeRepository, IMTTreeJSONSerializable):
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
        return os.path.join(self.storage_dir, f"{tree_id}.json")
    
    def save(self, tree: Any, tree_id: Optional[str] = None) -> str:
        """트리를 파일로 저장합니다."""
        # ID가 없으면 새로 생성
        if tree_id is None:
            tree_id = str(uuid.uuid4())
        
        # 트리를 딕셔너리로 변환
        tree_dict = tree.to_dict()
        
        # 딕셔너리를 JSON으로 변환
        json_str = json.dumps(tree_dict, ensure_ascii=False, indent=2)
        
        # 파일에 저장
        with open(self._get_file_path(tree_id), 'w', encoding='utf-8') as file:
            file.write(json_str)
        
        return tree_id
    
    def load(self, tree_id: str) -> Optional[Any]:
        """파일로부터 트리를 로드합니다."""
        file_path = self._get_file_path(tree_id)
        
        if not os.path.exists(file_path):
            return None
        
        try:
            # 파일에서 JSON 문자열 읽기
            with open(file_path, 'r', encoding='utf-8') as file:
                json_str = file.read()
            
            return self.from_json(json_str)
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
                    # 트리 이름 가져오기
                    tree = self.load(tree_id)
                    if tree:
                        result[tree_id] = tree.name
                except Exception:
                    # 로드 실패 시 ID만 사용
                    result[tree_id] = f"Tree {tree_id}"
        
        return result