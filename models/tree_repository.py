"""트리 데이터베이스 DAO 모듈

트리 구조의 데이터를 데이터베이스에 저장하고 관리하는 기능을 제공합니다.
"""
import os
import psycopg2
from getpass import getpass
from dotenv import load_dotenv
from typing import Dict, List, Optional, Tuple, Any
from core.tree_state import TreeState
from viewmodels.snapshot_manager import TreeSnapshotManager
from utils.config_manager import ConfigManager


class DatabaseConnection:
    """데이터베이스 연결 싱글톤 클래스
    
    데이터베이스 연결을 관리하는 싱글톤 패턴 클래스입니다.
    """
    
    _instance = None
    _connection = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseConnection, cls).__new__(cls)
        return cls._instance
    
    def connect(self) -> Optional[psycopg2.extensions.connection]:
        """데이터베이스에 연결합니다.
        
        Returns:
            데이터베이스 연결 객체 또는 None
        """
        if self._connection is not None and not self._connection.closed:
            return self._connection
        
        try:
            # 설정 관리자에서 데이터베이스 연결 정보 가져오기
            config = ConfigManager()
            db_name = config.get("database", "name")
            db_user = config.get("database", "user")
            db_host = config.get("database", "host", "localhost")
            db_port = config.get("database", "port", "5432")
            db_password = os.environ.get("DB_PASSWORD")
            
            # 비밀번호가 환경 변수에 없으면 사용자에게 요청
            if not db_password and os.environ.get("ENVIRONMENT") != "production":
                db_password = getpass("Enter database password: ")
            
            # 연결 문자열 생성
            conn_string = f"dbname={db_name} user={db_user} host={db_host} port={db_port}"
            if db_password:
                conn_string += f" password={db_password}"
            
            # 데이터베이스 연결
            self._connection = psycopg2.connect(conn_string)
            return self._connection
            
        except Exception as e:
            print(f"데이터베이스 연결 오류: {e}")
            return None


class TreeRepository:
    """트리 데이터베이스 DAO 클래스
    
    트리 구조의 데이터를 데이터베이스에 저장하고 관리합니다.
    """
    
    def __init__(self, conn_string: Optional[str] = None) -> None:
        """TreeRepository 생성자
        
        Args:
            conn_string: 데이터베이스 연결 문자열 (선택적)
        """
        self.db_connection = DatabaseConnection()
        self.snapshot_manager = TreeSnapshotManager()
        self.conn_string = conn_string
        self.use_db = True  # 데이터베이스 사용 여부

    def get_connection(self) -> Optional[psycopg2.extensions.connection]:
        """데이터베이스 연결을 반환합니다.
        
        Returns:
            데이터베이스 연결 객체 또는 None
        """
        conn = self.db_connection.connect()
        if conn is None:
            self.use_db = False
        return conn

    def _execute_query(self, query: str, params: Optional[Tuple] = None) -> Optional[Tuple[psycopg2.extensions.cursor, psycopg2.extensions.connection]]:
        """데이터베이스 쿼리를 실행합니다.
        
        Args:
            query: 실행할 SQL 쿼리
            params: 쿼리 매개변수 (선택적)
            
        Returns:
            커서와 연결 객체 튜플 또는 None
        """
        conn = self.get_connection()
        if conn is None:
            return None
            
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
        # 데이터베이스 연결 시도
        result = self._execute_query("SELECT id, parent_id, name, inp, sub_con, sub FROM tree_nodes")
        
        # 데이터베이스 연결 실패 또는 쿼리 실패 시 기본 트리 상태 반환
        if result is None:
            print("데이터베이스 연결 실패. 기본 트리 상태를 사용합니다.")
            return self._create_default_tree_state()
            
        cur, _ = result
        rows = cur.fetchall()

        # 데이터가 없으면 기본 트리 상태 반환
        if not rows:
            return self._create_default_tree_state()

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
        
    def _create_default_tree_state(self) -> TreeState:
        """기본 트리 상태를 생성합니다.
        
        Returns:
            기본 트리 상태
        """
        # 기본 노드 생성
        nodes = {
            "1": {
                'name': "G:기본 그룹",
                'inp': "M",
                'sub_con': "",
                'sub': "click",
                'parent_id': None
            },
            "2": {
                'name': "I:기본 인스턴스",
                'inp': "M",
                'sub_con': "",
                'sub': "click",
                'parent_id': None
            },
            "3": {
                'name': "기본 액션",
                'inp': "M",
                'sub_con': "0,0",
                'sub': "click",
                'parent_id': "1"
            }
        }
        
        # 기본 구조 생성
        structure = {
            None: ["1", "2"],
            "1": ["3"]
        }
        
        # 기본 트리 상태 생성
        default_state = TreeState(nodes, structure)
        self.snapshot_manager.add_snapshot(default_state)
        return default_state

    def save_tree(self, tree_state: TreeState) -> None:
        """현재 트리 상태를 DB에 저장합니다.
        
        Args:
            tree_state: 저장할 트리 상태
        """
        # 데이터베이스를 사용하지 않는 경우 저장하지 않음
        if not self.use_db:
            print("데이터베이스를 사용하지 않아 저장하지 않습니다.")
            return
            
        try:
            result = self._execute_query("BEGIN")
            if result is None:
                print("데이터베이스 연결 실패. 저장하지 않습니다.")
                return
                
            cur, conn = result
            
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
            if 'cur' in locals():
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