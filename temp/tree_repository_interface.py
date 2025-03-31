from typing import Protocol, Optional, Dict, Any, List
from temp.tree_interface import IMTTree


class IMTTreeRepository(Protocol):
    """매크로 트리 저장소 인터페이스
    
    트리 데이터의 영속성을 관리합니다.
    """
    
    def save(self, tree: IMTTree, name: str = None) -> str:
        """트리를 저장합니다.
        
        Args:
            tree: 저장할 트리
            name: 저장 이름 (선택적)
            
        Returns:
            저장된 트리의 식별자
            
        Raises:
            TreeSaveError: 저장 실패 시
        """
        ...
    
    def load(self, identifier: str = None) -> IMTTree:
        """트리를 불러옵니다.
        
        Args:
            identifier: 트리 식별자 (None이면 최신 트리)
            
        Returns:
            불러온 트리
            
        Raises:
            TreeNotFoundError: 트리를 찾을 수 없을 때
        """
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
        """트리를 JSON 문자열로 변환합니다.
        
        Args:
            tree: 변환할 트리
            
        Returns:
            JSON 문자열
        """
        ...
    
    def from_json(self, json_str: str) -> IMTTree:
        """JSON 문자열에서 트리를 생성합니다.
        
        Args:
            json_str: JSON 문자열
            
        Returns:
            생성된 트리
            
        Raises:
            ValueError: 잘못된 JSON 형식
        """
        ...