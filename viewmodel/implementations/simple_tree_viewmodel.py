from typing import Dict, List, Any, Optional
import os
from ...model.implementations.simple_tree import SimpleTree
from ...model.implementations.simple_tree_item import SimpleTreeItem

class SimpleTreeViewModel:
    def __init__(self, tree: SimpleTree):
        self._tree = tree
        self._selected_ids: List[str] = []
    
    def get_items_for_display(self) -> List[Dict[str, Any]]:
        tree_items = self._tree.get_all_items()
        
        # 리스트 컴프리헨션 사용
        return [{
            "id": item.get_id(),
            "name": item.get_property("name", ""),
            "selected": item.get_id() in self._selected_ids
        } for item_id, item in tree_items.items()]
    
    def get_tree_items(self) -> Dict[str, SimpleTreeItem]:
        """모든 트리 아이템 딕셔너리 반환"""
        return self._tree.get_all_items()
    
    def get_item(self, item_id: str) -> Optional[SimpleTreeItem]:
        """특정 ID의 트리 아이템 반환"""
        return self._tree.get_item(item_id)
    
    def add_item(self, name: str, parent_id: Optional[str] = None) -> Optional[str]:
        """
        새 아이템을 추가합니다.
        
        Args:
            name: 아이템 이름
            parent_id: 부모 아이템 ID (없으면 루트 아이템)
            
        Returns:
            생성된 아이템의 ID 또는 None (실패 시)
        """
        # 간단한 ID 생성 (실제로는 더 견고한 방식 사용 권장)
        import uuid
        item_id = str(uuid.uuid4())
        
        # 새 아이템 생성
        from ...model.implementations.simple_tree_item import SimpleTreeItem
        new_item = SimpleTreeItem(item_id, name)
        
        # 트리에 추가
        if self._tree.add_item(new_item, parent_id):
            # 부모가 있으면 부모 확장
            if parent_id:
                parent_item = self._tree.get_item(parent_id)
                if parent_item:
                    parent_item.set_property("expanded", True)
            return item_id
        return None
    
    def delete_item(self, item_id: str) -> bool:
        """
        아이템을 삭제합니다.
        
        Args:
            item_id: 삭제할 아이템 ID
            
        Returns:
            성공 여부
        """
        # 선택된 아이템이면 선택 해제
        if item_id in self._selected_ids:
            self._selected_ids.remove(item_id)
            
        return self._tree.remove_item(item_id)
    
    def update_item(self, item_id: str, name: Optional[str] = None, parent_id: Optional[str] = None) -> bool:
        """
        아이템을 업데이트합니다.
        
        Args:
            item_id: 업데이트할 아이템 ID
            name: 새 이름 (변경 시)
            parent_id: 새 부모 ID (변경 시)
            
        Returns:
            성공 여부
        """
        return self._tree.update_item(item_id, name, parent_id)
    
    def select_item(self, item_id: str) -> bool:
        item = self._tree.get_item(item_id)
        if not item:
            return False
        
        # 기존 선택 모두 지우기
        self._selected_ids.clear()
        # 새 선택 추가
        self._selected_ids.append(item_id)
        return True
    
    def get_selected_items(self) -> List[str]:
        return self._selected_ids

    def get_visible_items(self) -> List[Dict[str, Any]]:
        """화면에 표시할 아이템만 반환 (확장 상태에 따라 필터링)"""
        result = []
        
        # 루트 레벨 아이템 먼저 가져오기
        root_items = [item for item_id, item in self._tree.get_all_items().items() 
                     if not item.get_property("parent_id")]
        
        # 각 루트 아이템에 대해 자식 아이템 재귀적으로 처리
        for item in root_items:
            result.append({
                "id": item.get_id(),
                "name": item.get_property("name", ""),
                "level": 0,  # 루트 레벨
                "expanded": item.get_property("expanded", False),
                "selected": item.get_id() in self._selected_ids,
                "has_children": self._has_children(item.get_id())
            })
            
            # 확장된 상태면 자식도 포함
            if item.get_property("expanded", False):
                self._add_children_to_result(item.get_id(), result, 1)  # 레벨 1부터 시작
        
        return result

    def _add_children_to_result(self, parent_id: str, result: List[Dict[str, Any]], level: int) -> None:
        """특정 부모의 자식 아이템을 결과 목록에 추가"""
        children = self._get_children(parent_id)
        
        for child in children:
            child_id = child.get_id()
            result.append({
                "id": child_id,
                "name": child.get_property("name", ""),
                "level": level,
                "expanded": child.get_property("expanded", False),
                "selected": child_id in self._selected_ids,
                "has_children": self._has_children(child_id)
            })
            
            # 이 자식이 확장되어 있으면 그 자식들도 추가
            if child.get_property("expanded", False):
                self._add_children_to_result(child_id, result, level + 1)

    def _get_children(self, parent_id: str) -> List[SimpleTreeItem]:
        """특정 부모의 모든 자식 아이템 반환"""
        return [item for item_id, item in self._tree.get_all_items().items() 
                if item.get_property("parent_id") == parent_id]

    def _has_children(self, item_id: str) -> bool:
        """
        아이템이 자식을 가지고 있는지 확인 (최적화된 버전)
        모든 아이템을 순회하는 대신 첫 번째 자식 아이템만 찾음
        """
        for item in self._tree.get_all_items().values():
            if item.get_property("parent_id") == item_id:
                return True
        return False

    def toggle_expanded(self, item_id: str, expanded: Optional[bool] = None) -> bool:
        """
        아이템의 확장/축소 상태 변경
        
        Args:
            item_id: 아이템 ID
            expanded: 설정할 상태. None이면 현재 상태 반전
        """
        item = self._tree.get_item(item_id)
        if not item:
            return False
        
        if expanded is None:
            # 상태 토글
            current = item.get_property("expanded", False)
            item.set_property("expanded", not current)
        else:
            # 상태 직접 설정
            item.set_property("expanded", expanded)
            
        return True
        
    def move_item(self, item_id: str, new_parent_id: Optional[str] = None) -> bool:
        """
        아이템을 다른 부모로 이동합니다.
        
        Args:
            item_id: 이동할 아이템 ID
            new_parent_id: 새 부모 ID (None이면 루트 레벨로 이동)
            
        Returns:
            성공 여부
        """
        return self._tree.update_item(item_id, parent_id=new_parent_id)
    
    def save_tree(self, file_path: str) -> bool:
        """
        현재 트리를 파일에 저장합니다.
        
        Args:
            file_path: 저장할 파일 경로
            
        Returns:
            성공 여부
        """
        return self._tree.save_to_file(file_path)
    
    def load_tree(self, file_path: str) -> bool:
        """
        파일에서 트리를 로드합니다.
        
        Args:
            file_path: 불러올 파일 경로
            
        Returns:
            성공 여부
        """
        if not os.path.exists(file_path):
            return False
            
        new_tree = SimpleTree.load_from_file(file_path)
        if new_tree:
            self._tree = new_tree
            self._selected_ids.clear()
            return True
        return False
