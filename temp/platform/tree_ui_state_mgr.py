from typing import Protocol, Dict, Any, Callable, List, Optional
from temp.model.tree_state_mgr import IMTTreeStateManager
from temp.model.tree_item import IMTTreeItem

class IMTTreeUIStateManager(Protocol):
    """UI와 트리 상태 연계 관리자"""
    
    def connect_tree_state(self, state_manager: IMTTreeStateManager) -> None:
        """트리 상태 관리자 연결"""
        pass
    
    def get_ui_state(self) -> Dict[str, Any]:
        """현재 UI 상태 조회"""
        pass
    
    def update_ui_state(self, changes: Dict[str, Any]) -> None:
        """UI 상태 업데이트"""
        pass
    
    def subscribe_to_item_change(self, callback: Callable[[IMTTreeItem], None]) -> None:
        """아이템 변경 구독"""
        pass
    
    def subscribe_to_selection_change(self, callback: Callable[[List[str]], None]) -> None:
        """선택 변경 구독"""
        pass
    
    def get_selected_items(self) -> List[str]:
        """선택된 아이템 ID 목록 조회"""
        pass
    
    def select_item(self, item_id: str, multi_select: bool = False) -> None:
        """아이템 선택"""
        pass
