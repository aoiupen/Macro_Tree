from typing import Dict, List, Any, Optional, Callable, Set
from uuid import uuid4
from core.interfaces.base_tree import IMTTree
from core.interfaces.base_tree import IMTTreeItem
from model.store.repo.interfaces.base_tree_repo import IMTTreeRepository
from model.services.state.interfaces.base_tree_state_mgr import IMTTreeStateManager
from viewmodel.interfaces.base_tree_viewmodel import IMTTreeViewModel
from core.interfaces.base_item_data import MTTreeItemData
from core.impl.utils import to_tree_item_data
import core.exceptions as exc

class MTTreeViewModel(IMTTreeViewModel):
    """데모 트리 뷰모델 구현"""
    
    def __init__(self, repository: IMTTreeRepository | None, state_manager: IMTTreeStateManager | None):
        """뷰모델 초기화
        
        Args:
            repository: 트리 저장소
            state_manager: 트리 상태 관리자
        """
        self._repository = repository
        self._state_mgr = state_manager
        self._selected_items: Set[str] = set()  # 선택된 아이템 ID 집합
        self._subscribers: Set[Callable[[], None]] = set()  # 변경 알림을 받을 콜백
    
    # RF : 반환형이 인터페이스 -> DIP (구현이 아닌 인터페이스에 의존하는 원칙. 추상화에 의존하는 원칙. 해당 인터페이스로 구현한 어떤 객체든 반환 -> 유연성, 추상화 보장)
    def get_item(self, item_id: str) -> IMTTreeItem | None:
        """ID로 아이템을 찾습니다."""
        tree = self.get_current_tree()
        if tree:
            return tree.get_item(item_id)
        return None
    
    def add_item(self, name: str, parent_id: str | None = None) -> str | None:
        """새 아이템을 추가합니다.
        
        Args:
            name: 아이템 이름
            parent_id: 부모 아이템 ID (None이면 최상위 레벨)
            
        Returns:
            추가된 아이템 ID 또는 None (실패 시)
        """
        tree = self.get_current_tree()
        if not tree:
            return None
        
        # 상태 저장 (UNDO를 위해)
        self._state_mgr.save_state(tree)
        
        # 새 아이템 생성
        item_id = str(uuid4())
        new_item = IMTTreeItem(item_id, name)
        
        # 트리에 추가
        try:
            tree.add_item(new_item, parent_id)
            self._notify_change()
            return item_id
        except ValueError:
            return None
    
    def get_current_tree(self) -> IMTTree | None:
        """현재 트리를 반환합니다."""
        return self._state_mgr.current_state
    

    
    def update_item(self, item_id: str, name: str | None = None, parent_id: str | None = None) -> bool:
        """아이템을 업데이트합니다.
        
        Args:
            item_id: 업데이트할 아이템 ID
            name: 새 이름 (None이면 변경 안 함)
            parent_id: 새 부모 ID (None이면 변경 안 함)
            
        Returns:
            성공 여부
        """
        tree = self.get_current_tree()
        if not tree:
            return False
        
        # 상태 저장 (UNDO를 위해)
        self._state_mgr.save_state(tree)
        
        # 아이템 찾기
        item = tree.get_item(item_id)
        if not item:
            return False
        
        # 이름 변경
        if name is not None:
            item.set_property("name", name)
        
        # 부모 변경
        if parent_id is not None:
            try:
                tree.move_item(item_id, parent_id)
            except exc.MTTreeItemNotFoundError:
                return False
            except exc.MTTreeError:
                return False
        
        self._notify_change()
        return True
    
    def remove_item(self, item_id: str) -> bool:
        """아이템을 삭제합니다."""
        tree = self.get_current_tree()
        if not tree:
            return False
        
        # 상태 저장 (UNDO를 위해)
        self._state_mgr.save_state(tree)
        
        # 선택된 아이템에서 제거
        if item_id in self._selected_items:
            self._selected_items.remove(item_id)
        
        # 트리에서 제거
        try:
            tree.remove_item(item_id)
            self._notify_change()
            return True
        except exc.MTTreeItemNotFoundError:
            return False

    
    def get_selected_items(self) -> List[str]:
        """선택된 아이템 ID 목록을 반환합니다."""
        return list(self._selected_items)
    
    def toggle_expanded(self, item_id: str, expanded: bool | None = None) -> bool:
        """아이템 확장/축소 상태를 토글합니다.
        
        Args:
            item_id: 토글할 아이템 ID
            expanded: 확장 상태 (None이면 현재 상태의 반대)
            
        Returns:
            성공 여부
        """
        tree = self.get_current_tree()
        if not tree:
            return False
        
        item = tree.get_item(item_id)
        if not item:
            return False
        
        # 상태 저장 (UNDO를 위해)
        self._state_mgr.save_state(tree)
        
        # 확장 상태 결정
        current = item.get_property("expanded", False)
        new_state = not current if expanded is None else expanded
        
        # 상태 변경
        item.set_property("expanded", new_state)
        
        self._notify_change()
        return True
    
    def move_item(self, item_id: str, new_parent_id: str | None = None) -> bool:
        """아이템을 이동합니다."""
        tree = self.get_current_tree()
        if not tree:
            return False
        
        # 상태 저장 (UNDO를 위해)
        self._state_mgr.save_state(tree)
        
        # 이동 수행
        try:
            tree.move_item(item_id, new_parent_id)
            self._notify_change()
            return True
        except ValueError:
            return False
    
    def get_item_children(self, parent_id: str | None = None) -> list[MTTreeItemData]:
        """특정 부모의 자식 아이템 정보를 반환합니다."""
        tree = self.get_current_tree()
        if not tree:
            return []
        result = []
        children = tree.get_children(parent_id)
        for child in children:
            result.append(
                to_tree_item_data(
                    child,
                    parent_id,
                    selected=(child.id in self._selected_items)
                )
            )
        return result
    
    def subscribe(self, callback: Callable[[], None]) -> None:
        """변경 알림을 구독합니다."""
        self._subscribers.add(callback)
    
    def unsubscribe(self, callback: Callable[[], None]) -> None:
        """변경 알림 구독을 해제합니다."""
        if callback in self._subscribers:
            self._subscribers.remove(callback)
    
    def _notify_change(self) -> None:
        """모든 구독자에게 변경을 알립니다."""
        for callback in self._subscribers:
            callback()

    # RF : core 메서드를 직접 호출하지 않고, 계층 분리 원칙에 따라 wrapper로 감싸서 호출
    def get_tree_items(self) -> Dict[str, IMTTreeItem]:
        tree = self.get_current_tree()
        if not tree:
            return {}
        return tree.get_all_items()
