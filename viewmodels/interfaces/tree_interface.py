"""트리 ViewModel 인터페이스 모듈

트리 ViewModel의 인터페이스를 정의합니다.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from .viewmodel_base_interface import IViewModel


class ITreeViewModel(IViewModel):
    """트리 ViewModel 인터페이스"""
    
    @abstractmethod
    def get_items(self) -> List[Dict[str, Any]]:
        """트리 아이템 목록을 반환합니다."""
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
    def update_item(self, item_id: str, property_name: str, value: Any) -> None:
        """아이템 속성을 업데이트합니다.
        
        Args:
            item_id: 업데이트할 아이템 ID
            property_name: 업데이트할 속성 이름
            value: 새 값
        """
        pass
    
    @abstractmethod
    def get_selected_items(self) -> List[str]:
        """선택된 아이템 ID 목록을 반환합니다."""
        pass
    
    @abstractmethod
    def select_item(self, item_id: str) -> None:
        """아이템을 선택합니다.
        
        Args:
            item_id: 선택할 아이템 ID
        """
        pass
    
    @abstractmethod
    def toggle_select_item(self, item_id: str) -> None:
        """아이템 선택을 토글합니다.
        
        Args:
            item_id: 토글할 아이템 ID
        """
        pass
    
    @abstractmethod
    def toggle_expand(self, item_id: str) -> None:
        """아이템 확장을 토글합니다.
        
        Args:
            item_id: 토글할 아이템 ID
        """
        pass
    
    @abstractmethod
    def is_expanded(self, item_id: str) -> bool:
        """아이템이 확장되었는지 확인합니다.
        
        Args:
            item_id: 확인할 아이템 ID
            
        Returns:
            확장 여부
        """
        pass 