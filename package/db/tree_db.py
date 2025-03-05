"""트리 데이터베이스 모듈

트리 구조의 데이터를 데이터베이스에 저장하고 관리하는 기능을 제공합니다.
"""
from typing import Dict, Optional
from package.db.tree_db_dao import TreeDbDao, TreeState
from package.db.tree_snapshot_manager import TreeSnapshotManager


class TreeDB:
    """트리 데이터베이스 클래스
    
    트리 구조의 데이터를 데이터베이스에 저장하고 관리합니다.
    """

    def __init__(self, conn_string: str) -> None:
        """TreeDB 생성자
        
        Args:
            conn_string: 데이터베이스 연결 문자열
        """
        self.db_dao = TreeDbDao(conn_string)
        self.snapshot_manager = TreeSnapshotManager()

    def load_tree(self) -> TreeState:
        """DB에서 전체 트리 구조를 로드하고 초기 스냅샷을 생성합니다.
        
        Returns:
            로드된 트리 상태
        """
        initial_state = self.db_dao.load_tree()
        self.snapshot_manager.take_snapshot(initial_state)
        return initial_state

    def save_tree(self, tree_state: TreeState) -> None:
        """현재 트리 상태를 DB에 저장합니다.
        
        Args:
            tree_state: 저장할 트리 상태
        """
        self.db_dao.save_tree(tree_state)

    def take_snapshot(self, tree_state: TreeState) -> None:
        """현재 트리 상태의 스냅샷을 저장합니다.
        
        Args:
            tree_state: 스냅샷으로 저장할 트리 상태
        """
        self.snapshot_manager.take_snapshot(tree_state)

    def create_new_snapshot(self, changes: Dict[int, Dict]) -> TreeState:
        """최신 스냅샷의 복사본을 만들고 변경 사항을 적용하여 새로운 스냅샷을 생성합니다.
        
        Args:
            changes: 적용할 변경 사항 딕셔너리
            
        Returns:
            새로 생성된 트리 상태
        """
        return self.snapshot_manager.create_new_snapshot(changes)