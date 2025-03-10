"""트리 스냅샷 관리 모듈

트리 상태의 스냅샷을 관리하는 기능을 제공합니다.
"""
from typing import Dict, List, Optional, Any
import copy
from collections import deque
from package.db.tree_data import TreeState


class TreeSnapshotManager:
    """트리 스냅샷 관리 클래스
    
    트리 상태의 스냅샷을 효율적으로 관리합니다.
    """
    
    def __init__(self, max_snapshots: int = 20) -> None:
        """TreeSnapshotManager 생성자
        
        Args:
            max_snapshots: 최대 스냅샷 수
        """
        self.snapshots = deque(maxlen=max_snapshots)
        self.current_index = -1
    
    def add_snapshot(self, tree_state: TreeState) -> None:
        """현재 트리 상태의 스냅샷을 저장합니다.
        
        Args:
            tree_state: 트리 상태
        """
        # 현재 인덱스 이후의 스냅샷 제거
        while len(self.snapshots) > self.current_index + 1:
            self.snapshots.pop()
        
        # 새 스냅샷 추가
        self.snapshots.append(copy.deepcopy(tree_state))
        self.current_index = len(self.snapshots) - 1
    
    def get_current_snapshot(self) -> Optional[TreeState]:
        """현재 스냅샷을 반환합니다.
        
        Returns:
            현재 트리 상태 또는 None
        """
        if 0 <= self.current_index < len(self.snapshots):
            return self.snapshots[self.current_index]
        return None
    
    def can_undo(self) -> bool:
        """실행 취소가 가능한지 확인합니다.
        
        Returns:
            실행 취소 가능 여부
        """
        return self.current_index > 0
    
    def can_redo(self) -> bool:
        """다시 실행이 가능한지 확인합니다.
        
        Returns:
            다시 실행 가능 여부
        """
        return self.current_index < len(self.snapshots) - 1
    
    def undo(self) -> Optional[TreeState]:
        """실행 취소를 수행합니다.
        
        Returns:
            이전 트리 상태 또는 None
        """
        if self.can_undo():
            self.current_index -= 1
            return self.snapshots[self.current_index]
        return None
    
    def redo(self) -> Optional[TreeState]:
        """다시 실행을 수행합니다.
        
        Returns:
            다음 트리 상태 또는 None
        """
        if self.can_redo():
            self.current_index += 1
            return self.snapshots[self.current_index]
        return None
        
    def create_snapshot_from_changes(self, changes: Dict[str, Dict[str, Any]]) -> TreeState:
        """최신 스냅샷의 복사본을 만들고 변경 사항을 적용하여 새로운 스냅샷을 생성합니다.
        
        Args:
            changes: 적용할 변경 사항 딕셔너리
            
        Returns:
            새로 생성된 트리 상태
        """
        if not self.snapshots:
            raise ValueError("스냅샷이 없어 새 스냅샷을 생성할 수 없습니다.")

        latest_snapshot = self.snapshots[self.current_index]
        new_snapshot = copy.deepcopy(latest_snapshot)

        for node_id, node_changes in changes.items():
            if node_id in new_snapshot.nodes:
                new_snapshot.nodes[node_id].update(node_changes)

        self.add_snapshot(new_snapshot)
        return new_snapshot