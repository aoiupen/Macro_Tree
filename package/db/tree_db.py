from tree_db_dao import TreeDbDao, TreeState
from tree_snapshot_manager import TreeSnapshotManager
from typing import Dict, Optional  # Dict 및 Optional 임포트

class TreeDB:
    def __init__(self, conn_string):
        self.db_dao = TreeDbDao(conn_string)
        self.snapshot_manager = TreeSnapshotManager()

    def load_tree(self) -> TreeState:
        """DB에서 전체 트리 구조를 로드하고 초기 스냅샷 생성"""
        initial_state = self.db_dao.load_tree()
        self.snapshot_manager.take_snapshot(initial_state)
        return initial_state

    def save_tree(self, tree_state: TreeState):
        """현재 트리 상태를 DB에 저장"""
        self.db_dao.save_tree(tree_state)

    def take_snapshot(self, tree_state: TreeState):
        """현재 트리 상태의 스냅샷을 저장"""
        self.snapshot_manager.take_snapshot(tree_state)

    def create_new_snapshot(self, changes: Dict[int, Dict]) -> TreeState:
        """최신 스냅샷의 복사본을 만들고 변경 사항을 적용하여 새로운 스냅샷 생성"""
        return self.snapshot_manager.create_new_snapshot(changes)

    def restore_snapshot(self, index: int) -> Optional[TreeState]:
        """지정된 인덱스의 스냅샷으로 복원"""
        return self.snapshot_manager.restore_snapshot(index)