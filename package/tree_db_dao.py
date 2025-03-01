import psycopg2
from typing import Dict, List, Optional
from dataclasses import dataclass
import copy

@dataclass
class TreeState:
    """현재 트리의 전체 상태를 저장하는 클래스"""
    nodes: Dict[int, Dict]  # {node_id: node_data}
    structure: Dict[int, List[int]]  # {parent_id: [child_ids]}

class TreeDbDao:
    def __init__(self, conn_string):
        self.conn_string = conn_string

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

                return TreeState(nodes, structure)  # 수정된 부분