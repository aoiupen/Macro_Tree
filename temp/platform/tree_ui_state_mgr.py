from typing import Protocol, Dict, Any, Callable, List, Optional
from temp.model.tree_state_mgr import IMTTreeStateManager
from temp.model.tree_item import IMTTreeItem

class IMTTreeUIStateManager(Protocol):
    """UI 상태 관리자 인터페이스
    
    책임:
    1. UI 특화 상태 관리:
       - get_ui_state(): 현재 UI 상태 조회
       - update_ui_state(): UI 상태 업데이트
       - save_ui_state(): UI 상태 저장
       - restore_ui_state(): UI 상태 복원
    
    2. 트리 데이터-UI 상태 동기화:
       - get_selected_items(): 선택된 아이템 조회
       - select_item(): 아이템 선택 상태 설정
    
    3. UI 상태 변경 이벤트 처리:
       - subscribe_to_ui_change(): UI 상태 변경 알림 구독
    
    Note:
        - IMTTreeStateManager: 비즈니스 로직 상태(실행취소/다시실행 등) 관리
        - IMTTreeViewModel: 데이터-UI 변환 및 조작 로직
        - IMTTreeUIStateManager: UI 특화 상태 관리
    """
    
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
