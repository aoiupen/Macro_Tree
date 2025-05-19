from typing import Any, Callable, Dict, List, Set, Optional
from copy import deepcopy

from core.interfaces.base_tree import IMTTree
from model.events.interfaces.base_tree_event_mgr import MTTreeEvent
from model.state.interfaces.base_tree_state_mgr import IMTTreeStateManager
from model.events.interfaces.base_tree_event_mgr import TreeEventCallback
from model.events.impl.tree_event_mgr import EventManagerBase

# MTNodeType Enum을 사용한다면 import 필요
# from core.interfaces.base_item_data import MTNodeType # 예시 경로

def _format_tree_for_comprehension(tree_data_dict: dict) -> str:
    """
    트리 데이터 딕셔너리를 사람이 이해하기 쉬운 문자열로 포맷합니다.
    주요 항목 (ID, 이름, 타입) 및 계층 구조를 보여줍니다.
    """
    if not tree_data_dict or not isinstance(tree_data_dict, dict):
        return "(No tree data or invalid format)"

    lines = []
    items_map = tree_data_dict.get('items', {})

    def _recursive_build_lines(item_id: str, indent_level: int):
        item_snapshot = items_map.get(item_id)
        if not item_snapshot:
            lines.append(f"{'  ' * indent_level}Error: Item '{item_id}' not found in items map.")
            return

        # item_snapshot['data']는 MTTreeItemData 객체라고 가정
        item_data_obj = item_snapshot.get('data') 
        if not item_data_obj: # MTTreeItemData 객체가 없을 경우에 대한 방어 코드
            lines.append(f"{'  ' * indent_level}- ID: {item_id}, Name: N/A (No item_data_obj)")
            return

        # MTTreeItemData 객체의 속성에 직접 접근
        name = getattr(item_data_obj, 'name', 'N/A')
        node_type_val = getattr(item_data_obj, 'node_type', None)
        
        # MTNodeType Enum 멤버일 경우, .name 또는 str()을 사용하여 문자열로 변환
        type_display = ""
        if node_type_val:
            # if isinstance(node_type_val, MTNodeType): # 실제 Enum 타입으로 확인
            #     type_display = f" (Type: {node_type_val.name})" 
            # else: # 이미 문자열이거나 다른 타입일 경우
            type_display = f" (Type: {str(node_type_val)})"

        lines.append(f"{'  ' * indent_level}- ID: {item_id}, Name: {name}{type_display}")

        children_ids = getattr(item_data_obj, 'children_ids', [])
        for child_id_val in children_ids:
            _recursive_build_lines(child_id_val, indent_level + 1)

    lines.append(f"Tree ID: {tree_data_dict.get('id', 'N/A')}, Tree Name: {tree_data_dict.get('name', 'N/A')}")
    root_id_val = tree_data_dict.get('root_id')

    if not root_id_val:
        lines.append("  (No root_id defined for the tree)")
    else:
        root_item_snapshot = items_map.get(root_id_val)
        if not root_item_snapshot:
            lines.append(f"  (Root item '{root_id_val}' not found in items map)")
        else:
            root_data_obj = root_item_snapshot.get('data')
            if not root_data_obj:
                lines.append(f"  Root Item: ID: {root_id_val}, Name: N/A (No root_data_obj)")
            else:
                root_name = getattr(root_data_obj, 'name', 'N/A')
                lines.append(f"  Root Item: ID: {root_id_val}, Name: {root_name} (Usually a dummy root)")
                
                root_children_ids = getattr(root_data_obj, 'children_ids', [])
                if not root_children_ids:
                    lines.append(f"    (Root '{root_id_val}' has no children to display)")
                else:
                    lines.append("    Children:")
                    for child_id_val in root_children_ids:
                        _recursive_build_lines(child_id_val, 3)

    return "\n".join(lines)

class MTTreeStateManager(EventManagerBase, IMTTreeStateManager):
    """매크로 트리 상태 관리자 구현"""
    
    def __init__(self, tree: IMTTree, max_history: int = 100):
        """상태 관리자를 초기화합니다."""
        super().__init__()
        self._max_history = max_history
        self._undo_stack: List[Dict[str, Any]] = []
        self._redo_stack: List[Dict[str, Any]] = []
        self._new_stage = {}
        self.set_initial_state(tree)
    
    def set_initial_state(self, tree: IMTTree) -> None:
        """초기 상태를 설정합니다."""
        # 기존 이력 초기화
        self._undo_stack = []
        self._redo_stack = []
        self._new_stage = tree.to_dict()
    
    def can_undo(self) -> bool:
        """Undo 가능한 상태가 있는지 확인합니다."""
        return len(self._undo_stack) > 0
    
    def can_redo(self) -> bool:
        """Redo 가능한 상태가 있는지 확인합니다."""
        return len(self._redo_stack) > 0
    
    # 최대 히스토리 수 제한 (오래된 순으로 제거)
    def _limit_stack(self, stack: List[Dict[str, Any]]) -> None:
        if len(stack) > self._max_history:
            stack.pop(0)

    def new_undo(self, new_stage: Dict[str, Any]) -> Dict[str, Any] | None:
        """Stage를 Undo로, Redo는 비우고"""
        if not new_stage:
            return
        self._undo_stack.append(self._new_stage)
        self._new_stage = new_stage

        self._limit_stack(self._undo_stack)
        self._redo_stack.clear()
        
        self.notify(MTTreeEvent.TREE_CRUD, self._new_stage)
        return self._new_stage

    def undo(self, stage: Dict[str, Any]) -> Dict[str, Any] | None:
        """Undo를 Stage로, Stage를 Redo로"""
        if not self.can_undo():
            return None
        self._redo_stack.append(stage.to_dict())
        self._limit_stack(self._redo_stack)
        self._new_stage = self._undo_stack.pop() # 가장 최근 상태 (Redo 스택으로 갈 것)

        self.notify(MTTreeEvent.TREE_UNDO, self._new_stage)
        return self._new_stage
    
    def redo(self, stage: Dict[str, Any]) -> Dict[str, Any] | None:
        """Redo를 Stage로, Stage를 Undo로"""
        if not self.can_redo():
            return None
        self._undo_stack.append(stage.to_dict())
        self._limit_stack(self._undo_stack)
        self._new_stage = self._redo_stack.pop()

        self.notify(MTTreeEvent.TREE_REDO, self._new_stage)
        return self._new_stage 