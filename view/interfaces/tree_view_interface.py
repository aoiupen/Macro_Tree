"""트리 뷰 인터페이스 모듈

트리 뷰의 인터페이스를 정의합니다.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from .view_base_interface import IView


class ITreeView(IView):
    """트리 뷰 인터페이스"""
    
    @abstractmethod
    def set_items(self, items: List[Dict[str, Any]]) -> None:
        """트리 아이템 목록을 설정합니다.
        
        Args:
            items: 설정할 아이템 목록
        """
        pass
    
    @abstractmethod
    def add_item(self, item: Dict[str, Any], parent_id: Optional[str] = None) -> bool:
        """아이템을 추가합니다.
        
        Args:
            item: 추가할 아이템 데이터
            parent_id: 부모 아이템 ID (선택적)
            
        Returns:
            추가 성공 여부
        """
        pass
    
    @abstractmethod
    def remove_item(self, item_id: str) -> bool:
        """아이템을 제거합니다.
        
        Args:
            item_id: 제거할 아이템 ID
            
        Returns:
            제거 성공 여부
        """
        pass
    
    @abstractmethod
    def update_item(self, item_id: str, properties: Dict[str, Any]) -> bool:
        """아이템을 업데이트합니다.
        
        Args:
            item_id: 업데이트할 아이템 ID
            properties: 업데이트할 속성 딕셔너리
            
        Returns:
            업데이트 성공 여부
        """
        pass
    
    @abstractmethod
    def expand_item(self, item_id: str) -> None:
        """아이템을 확장합니다.
        
        Args:
            item_id: 확장할 아이템 ID
        """
        pass
    
    @abstractmethod
    def collapse_item(self, item_id: str) -> None:
        """아이템을 축소합니다.
        
        Args:
            item_id: 축소할 아이템 ID
        """
        pass
    
    @abstractmethod
    def set_selected_items(self, item_ids: List[str]) -> None:
        """선택된 아이템을 설정합니다.
        
        Args:
            item_ids: 선택할 아이템 ID 목록
        """
        pass
    
    @abstractmethod
    def get_selected_items(self) -> List[str]:
        """선택된 아이템 ID 목록을 반환합니다.
        
        Returns:
            선택된 아이템 ID 목록
        """
        pass 