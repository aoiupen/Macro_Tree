from typing import Protocol, Optional, Dict, Any, List
from temp.core.tree import IMTTree


class IMTTreeRepository(Protocol):
    """매크로 트리 저장소 인터페이스
    
    트리 데이터의 영속성을 관리합니다.
    """
    
    def save(self, tree: IMTTree, name: Optional[str] = None) -> str:
        """트리를 저장합니다. Raises: TreeSaveError-저장 실패 시"""
        ...
    
    def load(self, identifier: Optional[str] = None) -> IMTTree:
        """트리를 불러옵니다. Raises: TreeNotFoundError-트리를 찾을 수 없을 때"""
        ...
    
    def delete(self, identifier: str) -> bool:
        """저장된 트리를 삭제합니다.
        
        Args:
            identifier: 트리 식별자
            
        Returns:
            성공 여부
        """
        ...
    
    def to_json(self, tree: IMTTree) -> str:
        """트리를 JSON 문자열로 변환합니다."""
        ...
    
    def from_json(self, json_str: str) -> IMTTree:
        """JSON 문자열에서 트리를 생성합니다. Raises: ValueError-잘못된 JSON 형식"""
        ...