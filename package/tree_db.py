from typing import Dict, List, Optional
from dataclasses import dataclass

@dataclass
class TreeState:
    """현재 트리의 전체 상태를 저장하는 클래스"""
    nodes: Dict[int, Dict]  # {node_id: node_data}
    structure: Dict[int, List[int]]  # {parent_id: [child_ids]}

class TreeDB:
    def __init__(self):
        self.conn_string = "dbname=mydb user=myuser password=mypass"
    
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
                
                return TreeState(nodes, structure)

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
