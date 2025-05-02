from typing import Protocol, Dict, Any, List, Type, Optional
from temp.platform.interfaces.ui_element import IMTUIElement
from temp.model.tree_item import IMTTreeItem
from temp.platform.tree_view import IMTTreeView

class IMTPlatformAdapter(Protocol):
    """플랫폼 특화 UI 생성 어댑터"""
    
    def create_tree_view(self) -> IMTTreeView:
        """트리 뷰 생성"""
        pass
    
    def create_item_view(self, item_type: str) -> IMTUIElement:
        """아이템 타입별 뷰 생성"""
        pass
    
    def create_container(self, layout_type: str) -> IMTUIElement:
        """컨테이너 요소 생성"""
        pass
    
    def initialize(self, config: Dict[str, Any]) -> None:
        """플랫폼 초기화"""
        pass
    
    def shutdown(self) -> None:
        """플랫폼 종료"""
        pass
