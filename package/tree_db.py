from typing import Dict, List, Optional
from dataclasses import dataclass
import psycopg2
import copy  # 깊은 복사를 위해 사용

@dataclass
class TreeState:
    """현재 트리의 전체 상태를 저장하는 클래스"""
    nodes: Dict[int, Dict]  # {node_id: node_data}
    structure: Dict[int, List[int]]  # {parent_id: [child_ids]}

class TreeDB:
    def __init__(self):
        self.conn_string = "dbname=mydb user=myuser password=mypass"
        self.snapshots = []  # 스냅샷을 저장할 리스트
    
    def get_connection(self):
        return psycopg2.connect(self.conn_string)
    
    def load_tree(self) -> TreeState:
        """DB에서 전체 트리 구조를 로드"""
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT id, parent_id, name, inp, sub_con, sub FROM tree_nodes")
                rows = cur.fetchall()
                
                nodes = {}
                structure = {}
                
                for row in rows:
                    node_id, parent_id, name, inp, sub_con, sub = row
                    nodes[node_id] = {
                        'name': name,
                        'inp': inp,
                        'sub_con': sub_con,
                        'sub': sub,
                        'parent_id': parent_id
                    }
                    
                    if parent_id not in structure:
                        structure[parent_id] = []
                    structure[parent_id].append(node_id)
                
                # 최초 스냅샷 생성
                initial_state = TreeState(nodes, structure)
                self.take_snapshot(initial_state)  # 최초 스냅샷 저장
                
                return initial_state

    def save_tree(self, tree_state: TreeState):
        """현재 트리 상태를 DB에 저장"""
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                # 기존 데이터 삭제
                cur.execute("TRUNCATE tree_nodes RESTART IDENTITY CASCADE")
                
                # 새로운 상태 저장
                for node_id, node_data in tree_state.nodes.items():
                    cur.execute(
                        """
                        INSERT INTO tree_nodes 
                        (id, parent_id, name, inp, sub_con, sub)
                        VALUES (%s, %s, %s, %s, %s, %s)
                        """,
                        (node_id, node_data['parent_id'], node_data['name'],
                         node_data['inp'], node_data['sub_con'], node_data['sub'])
                    )
                conn.commit()

    def take_snapshot(self, tree_state: TreeState):
        """현재 트리 상태의 스냅샷을 저장"""
        self.snapshots.append(copy.deepcopy(tree_state))  # 깊은 복사하여 저장

    def create_new_snapshot(self, changes: Dict[int, Dict]) -> TreeState:
        """최신 스냅샷의 복사본을 만들고 변경 사항을 적용하여 새로운 스냅샷 생성"""
        if not self.snapshots:
            raise ValueError("No snapshots available to create a new snapshot.")

        latest_snapshot = self.snapshots[-1]  # 최신 스냅샷
        new_snapshot = copy.deepcopy(latest_snapshot)  # 최신 스냅샷의 복사본 생성

        # 변경 사항 적용
        for node_id, changes in changes.items():
            if node_id in new_snapshot.nodes:
                new_snapshot.nodes[node_id].update(changes)  # 변경 사항 적용

        self.take_snapshot(new_snapshot)  # 새로운 스냅샷 저장
        return new_snapshot

    def restore_snapshot(self, index: int) -> Optional[TreeState]:
        """지정된 인덱스의 스냅샷으로 복원"""
        if 0 <= index < len(self.snapshots):
            return self.snapshots[index]
        return None