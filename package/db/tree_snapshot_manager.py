from typing import Dict, List, Optional
from dataclasses import dataclass
import copy
from tree_data import TreeState

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