"""트리 스냅샷 관리 모듈

트리 상태의 스냅샷을 관리하는 기능을 제공합니다.
"""
from typing import Dict, List, Optional, Any
import copy
from collections import deque
from core.tree_state import TreeState


class TreeSnapshotManager:
    """트리 스냅샷 관리 클래스
    
    트리 상태의 스냅샷을 효율적으로 관리합니다.
    """
    
    def __init__(self, max_snapshots: int = 20) -> None:
        """TreeSnapshotManager 생성자
        
        Args:
            max_snapshots: 최대 스냅샷 수 (기본값: 20)
        """
        self.snapshots = deque(maxlen=max_snapshots)
        self.current_index = -1
    
    def add_snapshot(self, tree_state: TreeState) -> None:
        """새로운 스냅샷을 추가합니다.
        
        Args:
            tree_state: 저장할 트리 상태
        """
        # 현재 인덱스 이후의 스냅샷 제거
        if self.current_index < len(self.snapshots) - 1:
            self.snapshots = deque(list(self.snapshots)[:self.current_index + 1], maxlen=self.snapshots.maxlen)
        
        # 깊은 복사본 저장
        self.snapshots.append(copy.deepcopy(tree_state))
        self.current_index = len(self.snapshots) - 1
    
    def get_current_snapshot(self) -> Optional[TreeState]:
        """현재 스냅샷을 반환합니다.
        
        Returns:
            현재 스냅샷 또는 None
        """
        if not self.snapshots or self.current_index < 0:
            return None
        
        return copy.deepcopy(self.snapshots[self.current_index])
    
    def can_undo(self) -> bool:
        """실행 취소 가능 여부를 반환합니다.
        
        Returns:
            실행 취소 가능 여부
        """
        return self.current_index > 0
    
    def can_redo(self) -> bool:
        """다시 실행 가능 여부를 반환합니다.
        
        Returns:
            다시 실행 가능 여부
        """
        return self.current_index < len(self.snapshots) - 1
    
    def undo(self) -> Optional[TreeState]:
        """이전 스냅샷으로 이동합니다.
        
        Returns:
            이전 스냅샷 또는 None
        """
        if not self.can_undo():
            return None
        
        self.current_index -= 1
        return copy.deepcopy(self.snapshots[self.current_index])
    
    def redo(self) -> Optional[TreeState]:
        """다음 스냅샷으로 이동합니다.
        
        Returns:
            다음 스냅샷 또는 None
        """
        if not self.can_redo():
            return None
        
        self.current_index += 1
        return copy.deepcopy(self.snapshots[self.current_index])
    
    def create_snapshot_from_changes(self, changes: Dict[str, Dict[str, Any]]) -> TreeState:
        """최신 스냅샷의 복사본을 만들고 변경 사항을 적용하여 새로운 스냅샷을 생성합니다.
        
        Args:
            changes: 적용할 변경 사항 딕셔너리
            
        Returns:
            새로 생성된 트리 상태
        """
        current = self.get_current_snapshot()
        if not current:
            # 스냅샷이 없으면 새로운 트리 상태 생성
            return TreeState({}, {})
        
        # 현재 스냅샷의 깊은 복사본 생성
        new_state = copy.deepcopy(current)
        
        # 변경 사항 적용
        for node_id, node_changes in changes.items():
            if node_id in new_state.nodes:
                # 기존 노드 업데이트
                new_state.nodes[node_id].update(node_changes)
            else:
                # 새 노드 추가
                new_state.nodes[node_id] = node_changes
                
                # 부모 노드가 있으면 구조 업데이트
                if 'parent_id' in node_changes:
                    parent_id = node_changes['parent_id']
                    if parent_id not in new_state.structure:
                        new_state.structure[parent_id] = []
                    new_state.structure[parent_id].append(node_id)
        
        # 새 스냅샷 추가
        self.add_snapshot(new_state)
        return new_state 