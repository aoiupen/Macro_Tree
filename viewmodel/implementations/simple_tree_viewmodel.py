from typing import Dict, List, Any, Optional, Callable, Set
import os
from uuid import uuid4
from ...model.implementations.simple_tree import SimpleTree
from ...model.implementations.simple_tree_item import SimpleTreeItem
from model.tree_repo import IMTTreeRepository
from model.tree_state_mgr import IMTTreeStateManager
from viewmodel.tree_viewmodel import IMTTreeViewModel

class SimpleTreeViewModel(IMTTreeViewModel):
    """간단한 트리 뷰모델 구현"""
    
    def __init__(self, repository: IMTTreeRepository, state_manager: IMTTreeStateManager):
        """뷰모델 초기화
        
        Args:
            repository: 트리 저장소
            state_manager: 트리 상태 관리자
        """
        self._repository = repository
        self._state_mgr = state_manager
        self._selected_items: Set[str] = set()  # 선택된 아이템 ID 집합
        self._subscribers: Set[Callable[[], None]] = set()  # 변경 알림을 받을 콜백
    
    def get_item(self, item_id: str) -> SimpleTreeItem | None:
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
        new_item = SimpleTreeItem(item_id, name)
        
        # 트리에 추가
        try:
            tree.add_item(new_item, parent_id)
            self._notify_change()
            return item_id
        except ValueError:
            return None
    
    def get_current_tree(self) -> SimpleTree | None:
        """현재 트리를 반환합니다."""
        return self._state_mgr.current_state
    
    def get_items(self) -> List[Dict[str, Any]]:
        """UI에 표시할 아이템 목록을 반환합니다."""
        tree = self.get_current_tree()
        if not tree:
            return []
        
        result = []
        
        # 트리 순회하면서 아이템 정보 수집
        def visitor(item: SimpleTreeItem) -> None:
            parent_id = None
            for pid, children in tree._children_map.items():
                if item.id in children:
                    parent_id = pid
                    break
            
            item_data = {
                "id": item.id,
                "parent_id": parent_id,
                "name": item.get_property("name", "unnamed"),
                "expanded": item.get_property("expanded", False),
                "selected": item.id in self._selected_items
            }
            result.append(item_data)
        
        tree.traverse(visitor)
        return result
    
    def load_tree(self, tree_id: str) -> bool:
        """저장소에서 트리를 로드합니다."""
        try:
            tree = self._repository.load(tree_id)
            if tree:
                self._state_mgr.set_initial_state(tree)
                self._selected_items.clear()
                self._notify_change()
                return True
        except ValueError:
            pass
        return False
    
    def save_tree(self, tree_id: str | None = None) -> str | None:
        """현재 트리를 저장소에 저장합니다."""
        tree = self.get_current_tree()
        if not tree:
            return None
        
        try:
            saved_id = self._repository.save(tree, tree_id)
            return saved_id
        except Exception:
            return None
    
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
            except ValueError:
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
        except ValueError:
            return False
    
    def select_item(self, item_id: str, multi_select: bool = False) -> bool:
        """아이템을 선택합니다.
        
        Args:
            item_id: 선택할 아이템 ID
            multi_select: 다중 선택 모드
            
        Returns:
            성공 여부
        """
        tree = self.get_current_tree()
        if not tree or not tree.get_item(item_id):
            return False
        
        # 다중 선택이 아니면 기존 선택 초기화
        if not multi_select:
            self._selected_items.clear()
        
        # 선택 토글
        if item_id in self._selected_items:
            self._selected_items.remove(item_id)
        else:
            self._selected_items.add(item_id)
        
        self._notify_change()
        return True
    
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
    
    def can_undo(self) -> bool:
        """실행 취소 가능 여부를 반환합니다."""
        return self._state_mgr.can_undo()
    
    def can_redo(self) -> bool:
        """다시 실행 가능 여부를 반환합니다."""
        return self._state_mgr.can_redo()
    
    def undo(self) -> bool:
        """이전 상태로 되돌립니다."""
        result = self._state_mgr.undo() is not None
        if result:
            self._notify_change()
        return result
    
    def redo(self) -> bool:
        """다음 상태로 복원합니다."""
        result = self._state_mgr.redo() is not None
        if result:
            self._notify_change()
        return result
    
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
    
    def get_item_children(self, parent_id: str | None = None) -> List[Dict[str, Any]]:
        """특정 부모의 자식 아이템 정보를 반환합니다."""
        tree = self.get_current_tree()
        if not tree:
            return []
        
        result = []
        children = tree.get_children(parent_id)
        
        for child in children:
            item_data = {
                "id": child.id,
                "name": child.get_property("name", "unnamed"),
                "expanded": child.get_property("expanded", False),
                "selected": child.id in self._selected_items
            }
            result.append(item_data)
        
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
