"""트리 데이터베이스 DAO 모듈

트리 구조의 데이터를 데이터베이스에 저장하고 관리하는 기능을 제공합니다.
"""
import os
import psycopg2
from getpass import getpass
from dotenv import load_dotenv
from typing import Dict, List, Optional, Tuple, Any
from core.tree_state import TreeState
from core.tree_state_manager import TreeStateManager
from utils.config_manager import ConfigManager
from .dummy_data import get_default_tree


# 데이터베이스 테이블 관련 상수
TABLE_CONFIG = {
    "name": "tree_nodes",
    "columns": ["id", "parent_id", "name", "inp", "sub_con", "sub"]
}


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
            # 환경 변수에서 연결 정보 로드
            load_dotenv()
            db_host = os.getenv("DB_HOST", "localhost")
            db_port = os.getenv("DB_PORT", "5432")
            db_name = os.getenv("DB_NAME", "postgres")
            db_user = os.getenv("DB_USER", "postgres")
            db_password = os.getenv("DB_PASSWORD", "")
            
            # 연결 문자열 생성
            conn_string = f"host={db_host} port={db_port} dbname={db_name} user={db_user} password={db_password}"
            
            # 연결 시도
            self._connection = psycopg2.connect(conn_string)
            return self._connection
        except Exception as e:
            print(f"데이터베이스 연결 오류: {e}")
            return None


class TreeRepository:
    """트리 저장소 클래스
    
    트리 구조의 데이터를 데이터베이스에 저장하고 관리합니다.
    """
    
    def __init__(self, conn_string: Optional[str] = None) -> None:
        """TreeRepository 생성자
        
        Args:
            conn_string: 데이터베이스 연결 문자열 (선택적)
        """
        self.db_connection = DatabaseConnection()
        self.state_manager = TreeStateManager()
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
        """SQL 쿼리를 실행합니다.
        
        Args:
            query: 실행할 SQL 쿼리
            params: 쿼리 파라미터 (선택적)
            
        Returns:
            (커서, 연결) 튜플 또는 None
        """
        if not self.use_db:
            return None
            
        conn = self.get_connection()
        if conn is None:
            return None
            
        try:
            cursor = conn.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            return cursor, conn
        except Exception as e:
            print(f"쿼리 실행 오류: {e}")
            if conn:
                conn.rollback()
            return None
    
    def load_tree(self) -> TreeState:
        """데이터베이스에서 트리를 로드합니다.
        
        Returns:
            로드된 트리 상태
        """
        if not self.use_db:
            return self._create_default_tree_state()
            
        # 노드 정보 조회 쿼리 - 간결한 방식으로 작성
        columns = ", ".join(TABLE_CONFIG["columns"])
        query = f"SELECT {columns} FROM {TABLE_CONFIG['name']} ORDER BY id"
        
        result = self._execute_query(query)
        if result is None:
            return self._create_default_tree_state()
            
        cursor, conn = result
        
        try:
            # 노드 정보 저장
            nodes = {}
            structure = {}
            
            rows = cursor.fetchall()
            for row in rows:
                node_id, parent_id, name, inp, sub_con, sub = row
                
                # 노드 정보 저장
                nodes[str(node_id)] = {
                    'name': name,
                    'inp': inp,
                    'sub_con': sub_con,
                    'sub': sub,
                    'parent_id': str(parent_id) if parent_id is not None else None
                }
                
                # 구조 정보 저장
                parent_key = str(parent_id) if parent_id is not None else None
                if parent_key not in structure:
                    structure[parent_key] = []
                structure[parent_key].append(str(node_id))
            
            # 트리 상태 생성
            tree_state = TreeState(nodes, structure)
            
            # 스냅샷 저장
            self.save_state(tree_state)
            
            return tree_state
        finally:
            cursor.close()
            conn.commit()
    
    def _create_default_tree_state(self) -> TreeState:
        """기본 트리 상태를 생성합니다."""
        default_tree = get_default_tree()
        self.save_state(default_tree)
        return default_tree
    
    def save_tree(self, tree_state: TreeState) -> None:
        """트리 상태를 데이터베이스에 저장합니다.
        
        Args:
            tree_state: 저장할 트리 상태
        """
        if not self.use_db:
            return
            
        # 기존 데이터 삭제
        delete_query = f"DELETE FROM {TABLE_CONFIG['name']}"
        result = self._execute_query(delete_query)
        if result is None:
            return
            
        cursor, conn = result
        
        try:
            # 새 데이터 삽입 - 간결한 방식으로 작성
            columns = ", ".join(TABLE_CONFIG["columns"])
            placeholders = ", ".join(['%s'] * len(TABLE_CONFIG["columns"]))
            insert_query = f"INSERT INTO {TABLE_CONFIG['name']} ({columns}) VALUES ({placeholders})"
            
            values = []
            for node_id, node_data in tree_state.nodes.items():
                # 문자열 ID를 정수로 변환
                try:
                    int_id = int(node_id)
                except ValueError:
                    # ID가 정수로 변환할 수 없는 경우 (임시 ID 등) 건너뜀
                    continue
                    
                parent_id = node_data.get('parent_id')
                int_parent_id = int(parent_id) if parent_id and parent_id != 'null' else None
                
                params = (
                    int_id,
                    int_parent_id,
                    node_data.get('name', ''),
                    node_data.get('inp', ''),
                    node_data.get('sub_con', ''),
                    node_data.get('sub', '')
                )
                
                values.append(params)
            
            # 일괄 삽입 실행
            cursor.executemany(insert_query, values)
            
            # 변경사항 저장
            conn.commit()
            
            # 스냅샷 저장
            self.save_state(tree_state)
            
        except Exception as e:
            print(f"트리 저장 오류: {e}")
            conn.rollback()
        finally:
            cursor.close()
    
    def save_state(self, tree_state: TreeState) -> None:
        """현재 트리 상태를 저장합니다.
        
        Args:
            tree_state: 저장할 트리 상태
        """
        self.state_manager.save_state(tree_state)

    def update_tree(self, changes: Dict[int, Dict[str, Any]]) -> None:
        """트리 상태를 업데이트합니다.
        
        Args:
            changes: 변경 사항 딕셔너리
        """
        # 현재 상태 가져오기
        current_state = self.state_manager.get_current_state()
        if not current_state:
            return
            
        # 변경 사항 적용
        str_changes = {str(k): v for k, v in changes.items()}
        new_state = self._apply_changes(current_state, str_changes)
        
        # 새 상태 저장
        self.save_state(new_state)
    
    def _apply_changes(self, state: TreeState, changes: Dict[str, Dict[str, Any]]) -> TreeState:
        """변경 사항을 적용한 새 상태를 생성합니다.
        
        Args:
            state: 기존 트리 상태
            changes: 변경 사항 딕셔너리
            
        Returns:
            새로 생성된 트리 상태
        """
        # 기존 상태 복사
        new_nodes = state.nodes.copy()
        new_structure = state.structure.copy()
        
        # 변경 사항 적용
        for node_id, node_changes in changes.items():
            if "_deleted" in node_changes:
                # 노드 삭제
                if node_id in new_nodes:
                    del new_nodes[node_id]
                # 구조에서도 제거
                for parent_id, children in new_structure.items():
                    if node_id in children:
                        children.remove(node_id)
            else:
                # 노드 추가/수정
                if node_id in new_nodes:
                    new_nodes[node_id].update(node_changes)
                else:
                    new_nodes[node_id] = node_changes
                    
                    # 부모-자식 관계 설정
                    if "parent_id" in node_changes:
                        parent_id = node_changes["parent_id"]
                        if parent_id not in new_structure:
                            new_structure[parent_id] = []
                        if node_id not in new_structure[parent_id]:
                            new_structure[parent_id].append(node_id)
        
        return TreeState(new_nodes, new_structure)