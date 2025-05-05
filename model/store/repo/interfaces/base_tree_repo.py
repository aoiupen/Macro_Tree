from typing import Any, Dict, Protocol, TypeVar

# IMTTree 타입 참조
IMTTree = TypeVar('IMTTree')

class IMTTreeRepository(Protocol):
    """트리 저장소 인터페이스"""
    
    def save(self, tree: IMTTree, tree_id: str | None = None) -> str:
        """트리를 저장소에 저장합니다.
        
        Args:
            tree: 저장할 트리
            tree_id: 트리 ID (None이면 새 ID 생성)
            
        Returns:
            저장된 트리 ID
        """
        ...
    
    def load(self, tree_id: str) -> IMTTree | None:
        """ID로 트리를 로드합니다.
        
        Args:
            tree_id: 로드할 트리 ID
            
        Returns:
            로드된 트리 또는 None (실패 시)
        """
        ...
    
    def delete(self, tree_id: str) -> bool:
        """트리를 삭제합니다.
        
        Args:
            tree_id: 삭제할 트리 ID
            
        Returns:
            성공 여부
        """
        ...
    
    def list_trees(self) -> Dict[str, str]:
        """사용 가능한 모든 트리 목록을 반환합니다.
        
        Returns:
            트리 ID를 키, 트리 이름을 값으로 하는 딕셔너리
        """
        ...