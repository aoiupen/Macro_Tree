"""트리 데이터베이스 DAO 모듈

트리 구조의 데이터를 데이터베이스에 저장하고 관리하는 기능을 제공합니다.
"""
import os
import psycopg2
from getpass import getpass
from dotenv import load_dotenv
from typing import Dict, List, Optional, Tuple, Any
from core.tree_state import TreeState
from .dummy_data import get_default_tree
from .database_connection import DatabaseConnection


# 데이터베이스 테이블 관련 상수
TABLE_CONFIG = {
    "name": "tree_nodes",
    "columns": ["id", "parent_id", "name", "inp", "sub_con", "sub"]
}


class TreeDataRepository:
    """트리 데이터 저장소 클래스
    
    트리 구조의 데이터를 데이터베이스에 저장하고 관리합니다.
    """
    
    def __init__(self, conn_string: Optional[str] = None) -> None:
        """TreeDataRepository 생성자
        
        Args:
            conn_string: 데이터베이스 연결 문자열 (선택적)
        """
        self.db_connection = DatabaseConnection()
        self.conn_string = conn_string
        self.use_db = True  # 데이터베이스 사용 여부
        
        # 데이터베이스에 연결 시도
        conn = self.get_connection()
        if conn is None:
            print("데이터베이스 연결에 실패했습니다. 더미 데이터를 사용합니다.")
            self.use_db = False

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
            cursor.execute(query, params)
            return cursor, conn
        except (Exception, psycopg2.Error) as error:
            print(f"데이터베이스 쿼리 실행 오류: {error}")
            if conn:
                conn.rollback()
            return None
    
    def load_tree(self) -> Optional[TreeState]:
        """데이터베이스에서 트리를 로드합니다.
        
        Returns:
            트리 상태 객체 또는 None
        """
        # 데이터베이스 사용 불가능하면 더미 데이터 반환
        if not self.use_db:
            print("데이터베이스를 사용할 수 없어 더미 데이터를 로드합니다.")
            return get_default_tree()
            
        # 노드 데이터 가져오기
        query = f"SELECT {', '.join(TABLE_CONFIG['columns'])} FROM {TABLE_CONFIG['name']}"
        result = self._execute_query(query)
        
        if result is None:
            print("데이터베이스 쿼리 실행 실패, 더미 데이터를 로드합니다.")
            return get_default_tree()
            
        cursor, conn = result
        
        try:
            # 결과에서 노드와 구조 데이터 구성
            nodes = {}
            structure = {None: []}
            
            for row in cursor.fetchall():
                node_id = str(row[0])
                parent_id = str(row[1]) if row[1] is not None else None
                
                # 노드 데이터 저장
                nodes[node_id] = {
                    'parent_id': parent_id,
                    'name': row[2],
                    'inp': row[3],
                    'sub_con': row[4],
                    'sub': row[5]
                }
                
                # 구조 데이터 저장
                if parent_id not in structure:
                    structure[parent_id] = []
                structure[parent_id].append(node_id)
                
                # 자식 노드 목록 초기화
                if node_id not in structure:
                    structure[node_id] = []
            
            # 트리 상태 생성
            if nodes:
                print(f"데이터베이스에서 {len(nodes)}개의 노드를 로드했습니다.")
                return TreeState(nodes, structure)
            else:
                print("데이터베이스에 데이터가 없어 더미 데이터를 로드합니다.")
                return get_default_tree()
            
        except Exception as e:
            print(f"트리 로드 오류: {e}, 더미 데이터를 로드합니다.")
            return get_default_tree()
        finally:
            cursor.close()
    
    def save_tree(self, tree_state: TreeState) -> bool:
        """트리를 데이터베이스에 저장합니다.
        
        Args:
            tree_state: 저장할 트리 상태
            
        Returns:
            성공 여부
        """
        if not self.use_db:
            print("데이터베이스를 사용할 수 없어 트리를 저장할 수 없습니다.")
            return False
            
        # 기존 데이터 삭제
        delete_query = f"DELETE FROM {TABLE_CONFIG['name']}"
        result = self._execute_query(delete_query)
        if result is None:
            return False
            
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
            if values:
                cursor.executemany(insert_query, values)
                print(f"데이터베이스에 {len(values)}개의 노드를 저장했습니다.")
            
            # 변경사항 저장
            conn.commit()
            return True
            
        except Exception as e:
            print(f"트리 저장 오류: {e}")
            conn.rollback()
            return False
        finally:
            cursor.close()

    def update_tree(self, changes: Dict[int, Dict[str, Any]]) -> bool:
        """트리 상태를 업데이트합니다.
        
        Args:
            changes: 변경 사항 딕셔너리
            
        Returns:
            성공 여부
        """
        # 현재 트리 로드
        current_tree = self.load_tree()
        if not current_tree:
            return False
            
        # 변경 사항 적용
        str_changes = {str(k): v for k, v in changes.items()}
        new_state = self._apply_changes(current_tree, str_changes)
        
        # 새 상태 저장
        return self.save_tree(new_state)
    
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
    
    def create_database_table(self) -> bool:
        """필요한 데이터베이스 테이블을 생성합니다."""
        if not self.use_db:
            return False
            
        create_table_query = f"""
        CREATE TABLE IF NOT EXISTS {TABLE_CONFIG['name']} (
            id INTEGER PRIMARY KEY,
            parent_id INTEGER REFERENCES {TABLE_CONFIG['name']}(id) ON DELETE CASCADE,
            name TEXT NOT NULL,
            inp TEXT,
            sub_con TEXT,
            sub TEXT
        )
        """
        
        result = self._execute_query(create_table_query)
        if result is None:
            return False
            
        cursor, conn = result
        try:
            conn.commit()
            print(f"테이블 {TABLE_CONFIG['name']}가 성공적으로 생성되었습니다.")
            return True
        except Exception as e:
            print(f"테이블 생성 오류: {e}")
            conn.rollback()
            return False
        finally:
            cursor.close()