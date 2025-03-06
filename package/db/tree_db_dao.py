"""트리 데이터베이스 DAO 모듈

트리 구조의 데이터를 데이터베이스에 저장하고 관리하는 기능을 제공합니다.
"""
import os
import psycopg2
from getpass import getpass
from dotenv import load_dotenv
from typing import Dict, List, Optional, Tuple, Any
from package.db.tree_data import TreeState
from package.db.tree_snapshot_manager import TreeSnapshotManager


class DatabaseConnection:
    """데이터베이스 연결 싱글톤 클래스
    
    데이터베이스 연결을 관리하는 싱글톤 패턴 클래스입니다.
    """
    
    _instance = None
    _connection = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def connect(self) -> Optional[psycopg2.extensions.connection]:
        """데이터베이스 연결을 생성하고 반환합니다.
        
        Returns:
            데이터베이스 연결 객체 또는 None
        """
        if DatabaseConnection._connection is not None:
            return DatabaseConnection._connection

        try:
            config = ConfigManager()
            db_name = config.get("database", "name")
            user = config.get("database", "user")
            host = config.get("database", "host")
            port = config.get("database", "port")
            
            password = getpass("Enter your database password: ")

            DatabaseConnection._connection = psycopg2.connect(
                dbname=db_name,
                user=user,
                password=password,
                host=host,
                port=port
            )
            return DatabaseConnection._connection

        except (psycopg2.OperationalError, KeyError) as e:
            print(f"데이터베이스 연결 오류: {e}")
            return None
        except Exception as e:
            print(f"예상치 못한 오류: {e}")
            return None


class TreeDbDao:
    """트리 데이터베이스 DAO 클래스
    
    트리 구조의 데이터를 데이터베이스에 저장하고 관리합니다.
    """
    
    def __init__(self, conn_string: Optional[str] = None) -> None:
        """TreeDbDao 생성자
        
        Args:
            conn_string: 데이터베이스 연결 문자열 (선택적)
        """
        self.db_connection = DatabaseConnection()
        self.snapshot_manager = TreeSnapshotManager()
        self.conn_string = conn_string

    def get_connection(self) -> Optional[psycopg2.extensions.connection]:
        """데이터베이스 연결을 반환합니다.
        
        Returns:
            데이터베이스 연결 객체 또는 None
        """
        return self.db_connection.connect()

    def _execute_query(self, query: str, params: Optional[Tuple] = None) -> Tuple[psycopg2.extensions.cursor, psycopg2.extensions.connection]:
        """데이터베이스 쿼리를 실행합니다.
        
        Args:
            query: 실행할 SQL 쿼리
            params: 쿼리 매개변수 (선택적)
            
        Returns:
            커서와 연결 객체 튜플
        """
        conn = self.get_connection()
        cur = conn.cursor()
        if params:
            cur.execute(query, params)
        else:
            cur.execute(query)
        return cur, conn

    def load_tree(self) -> TreeState:
        """DB에서 전체 트리 구조를 로드하고 초기 스냅샷을 생성합니다.
        
        Returns:
            로드된 트리 상태
        """
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

        initial_state = TreeState(nodes, structure)
        self.snapshot_manager.add_snapshot(initial_state)
        return initial_state

    def save_tree(self, tree_state: TreeState) -> None:
        """현재 트리 상태를 DB에 저장합니다.
        
        Args:
            tree_state: 저장할 트리 상태
        """
        try:
            cur, conn = self._execute_query("BEGIN")
            
            # 기존 데이터 삭제
            cur.execute("DELETE FROM tree_nodes")
            
            # 일괄 삽입을 위한 데이터 준비
            insert_data = []
            for node_id, node_data in tree_state.nodes.items():
                insert_data.append((
                    node_id,
                    node_data['parent_id'],
                    node_data['name'],
                    node_data['inp'],
                    node_data['sub_con'],
                    node_data['sub']
                ))
            
            # 일괄 삽입 실행
            cur.executemany(
                "INSERT INTO tree_nodes (id, parent_id, name, inp, sub_con, sub) VALUES (%s, %s, %s, %s, %s, %s)",
                insert_data
            )
            
            # 트랜잭션 커밋
            cur.execute("COMMIT")
            
        except Exception as e:
            print(f"트리 저장 오류: {e}")
            cur.execute("ROLLBACK")
        
    def add_snapshot(self, tree_state: TreeState) -> None:
        """현재 트리 상태의 스냅샷을 저장합니다.
        
        Args:
            tree_state: 스냅샷으로 저장할 트리 상태
        """
        self.snapshot_manager.add_snapshot(tree_state)

    def create_snapshot_from_changes(self, changes: Dict[int, Dict[str, Any]]) -> TreeState:
        """최신 스냅샷의 복사본을 만들고 변경 사항을 적용하여 새로운 스냅샷을 생성합니다.
        
        Args:
            changes: 적용할 변경 사항 딕셔너리
            
        Returns:
            새로 생성된 트리 상태
        """
        return self.snapshot_manager.create_snapshot_from_changes(changes)

    # 이전 메서드 이름과의 호환성을 위한 별칭
    take_snapshot = add_snapshot
    create_new_snapshot = create_snapshot_from_changes