import os
import psycopg2
from typing import Dict, List, Optional
from dataclasses import dataclass
import copy
from dotenv import load_dotenv
from getpass import getpass

# .env 파일의 환경 변수를 로드
load_dotenv()

@dataclass
class TreeState:
    """현재 트리의 전체 상태를 저장하는 클래스"""
    nodes: Dict[int, Dict]  # {node_id: node_data}
    structure: Dict[int, List[int]]  # {parent_id: [child_ids]}

class TreeDbDao:
    def __init__(self):
        # 환경 변수에서 데이터베이스 연결 정보 가져오기
        self.conn_string = (
            f"dbname={os.getenv('DB_NAME')} "
            f"user={os.getenv('DB_USER')} "
            f"host={os.getenv('DB_HOST')} "
            f"port={os.getenv('DB_PORT')}"
        )
        # 비밀번호를 사용자에게 입력받기
        self.password = getpass("Enter your database password: ")
        self.conn_string += f" password={self.password}"

    def get_connection(self):
        try:
            return psycopg2.connect(self.conn_string)
        except psycopg2.OperationalError as e:
            print(f"Database connection error: {e}")
            raise

    def load_tree(self):
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