from typing import Dict, List, Optional
from dataclasses import dataclass
import copy

@dataclass
class TreeState:
    """현재 트리의 전체 상태를 저장하는 클래스"""
    nodes: Dict[int, Dict]  # {node_id: node_data}
    structure: Dict[int, List[int]]  # {parent_id: [child_ids]}

class TreeSnapshotManager:
    def __init__(self):
        self.snapshots = []

    def take_snapshot(self, tree_state: TreeState):
        """현재 트리 상태의 스냅샷을 저장"""
        self.snapshots.append(copy.deepcopy(tree_state))

    def create_new_snapshot(self, changes: Dict[int, Dict]) -> TreeState:
        """최신 스냅샷의 복사본을 만들고 변경 사항을 적용하여 새로운 스냅샷 생성"""
        if not self.snapshots:
            raise ValueError("No snapshots available to create a new snapshot.")

        latest_snapshot = self.snapshots[-1]
        new_snapshot = copy.deepcopy(latest_snapshot)

        for node_id, changes in changes.items():
            if node_id in new_snapshot.nodes:
                new_snapshot.nodes[node_id].update(changes)

        self.take_snapshot(new_snapshot)
        return new_snapshot

    def restore_snapshot(self, index: int) -> Optional[TreeState]:
        """지정된 인덱스의 스냅샷으로 복원"""
        if 0 <= index < len(self.snapshots):
            return self.snapshots[index]
        return None