import os
import psycopg2
from getpass import getpass
from dotenv import load_dotenv
from typing import Dict, List
from dataclasses import dataclass
from tree_data import TreeState

class DatabaseConnection:
    _instance = None
    _connection = None  # 클래스 변수로 연결 객체 저장

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def connect(self):
        if DatabaseConnection._connection is not None:  # 클래스 변수 사용
            return DatabaseConnection._connection

        try:
            load_dotenv()
            db_name = os.getenv("DB_NAME")
            user = os.getenv("DB_USER")
            host = os.getenv("DB_HOST")
            port = os.getenv("DB_PORT")
            password = getpass("Enter your database password: ")

            DatabaseConnection._connection = psycopg2.connect(  # 클래스 변수 사용
                dbname=db_name,
                user=user,
                password=password,
                host=host,
                port=port
            )
            return DatabaseConnection._connection

        except psycopg2.OperationalError as e:
            print(f"Database connection error: {e}")
            return None

class TreeDbDao:
    def __init__(self):
        self.db_connection = DatabaseConnection()

    def get_connection(self):
        return self.db_connection.connect()

    def _execute_query(self, query, params=None):
        """데이터베이스 연결 및 커서 생성, 쿼리 실행을 담당하는 내부 메서드"""
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                if params:
                    cur.execute(query, params)
                else:
                    cur.execute(query)
                return cur, conn

    def load_tree(self):
        """DB에서 전체 트리 구조를 로드"""
        cur, _ = self._execute_query("SELECT id, parent_id, name, inp, sub_con, sub FROM tree_nodes")
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
        cur, conn = self._execute_query("DELETE FROM tree_nodes")
        for node_id, node_data in tree_state.nodes.items():
            cur.execute(
                "INSERT INTO tree_nodes (id, parent_id, name, inp, sub_con, sub) VALUES (%s, %s, %s, %s, %s, %s)",
                (
                    node_id,
                    node_data['parent_id'],
                    node_data['name'],
                    node_data['inp'],
                    node_data['sub_con'],
                    node_data['sub']
                ),
            )
        conn.commit()