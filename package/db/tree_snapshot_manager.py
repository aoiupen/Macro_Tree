"""트리 스냅샷 관리 모듈

트리 상태의 스냅샷을 생성하고 관리하는 기능을 제공합니다.
"""
from typing import Dict, List, Optional, Any
import copy
from package.db.tree_data import TreeState


class TreeSnapshotManager:
    """트리 스냅샷 관리 클래스
    
    트리 상태의 스냅샷을 생성하고 관리합니다.
    """

    def __init__(self) -> None:
        """TreeSnapshotManager 생성자"""
        self.snapshots: List[TreeState] = []

    def add_snapshot(self, tree_state: TreeState) -> None:
        """현재 트리 상태의 스냅샷을 저장합니다.
        
        Args:
            tree_state: 스냅샷으로 저장할 트리 상태
        """
        self.snapshots.append(copy.deepcopy(tree_state))

    def create_snapshot_from_changes(self, changes: Dict[int, Dict[str, Any]]) -> TreeState:
        """최신 스냅샷의 복사본을 만들고 변경 사항을 적용하여 새로운 스냅샷을 생성합니다.
        
        Args:
            changes: 적용할 변경 사항 딕셔너리
            
        Returns:
            새로 생성된 트리 상태
            
        Raises:
            ValueError: 사용 가능한 스냅샷이 없는 경우
        """
        if not self.snapshots:
            raise ValueError("No snapshots available to create a new snapshot.")

        latest_snapshot = self.snapshots[-1]
        new_snapshot = copy.deepcopy(latest_snapshot)

        for node_id, node_changes in changes.items():
            if node_id in new_snapshot.nodes:
                new_snapshot.nodes[node_id].update(node_changes)

        self.add_snapshot(new_snapshot)
        return new_snapshot
        
    # 이전 메서드 이름과의 호환성을 위한 별칭
    take_snapshot = add_snapshot
    create_new_snapshot = create_snapshot_from_changes