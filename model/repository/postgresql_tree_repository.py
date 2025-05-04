import json
import logging
import os
import time
from typing import Any, Dict, List, Optional, Tuple

import psycopg2
from psycopg2 import sql
from psycopg2.extras import Json

from core.interfaces.base_tree import IMTTree
from core.impl.tree import MTTree
from core.interfaces.base_item import IMTTreeItem
from model.tree_repo import IMTTreeRepository


logger = logging.getLogger(__name__)


class PostgreSQLConnectionError(Exception):
    """PostgreSQL 연결 오류"""
    pass


class TreeNotFoundError(Exception):
    """트리를 찾을 수 없음"""
    pass


class PostgreSQLTreeRepository(IMTTreeRepository):
    """PostgreSQL 기반 매크로 트리 저장소 구현
    
    PostgreSQL 데이터베이스를 사용해 트리 데이터를 저장하고 불러옵니다.
    """

    def __init__(self, 
                 host: str = "localhost", 
                 port: str = "5432", 
                 dbname: str = "macro_tree", 
                 user: str = "postgres", 
                 password: Optional[str] = None):
        """PostgreSQLTreeRepository 초기화
        
        Args:
            host: 데이터베이스 호스트 (기본값: localhost)
            port: 데이터베이스 포트 (기본값: 5432)
            dbname: 데이터베이스 이름 (기본값: macro_tree)
            user: 데이터베이스 사용자 (기본값: postgres)
            password: 비밀번호 (선택적, 환경변수 DB_PASSWORD 사용 가능)
        """
        self.host = host
        self.port = port
        self.dbname = dbname
        self.user = user
        
        # 비밀번호 처리 (환경변수 우선)
        self.password = password or os.environ.get("DB_PASSWORD")
        
        # 초기 연결 테스트 및 테이블 생성
        self._ensure_tables_exist()

    def _get_connection(self) -> psycopg2.extensions.connection:
        """데이터베이스 연결을 반환합니다.
        
        Returns:
            데이터베이스 연결 객체
        
        Raises:
            PostgreSQLConnectionError: 연결에 실패한 경우
        """
        try:
            conn = psycopg2.connect(
                host=self.host,
                port=self.port,
                dbname=self.dbname,
                user=self.user,
                password=self.password
            )
            return conn
        except psycopg2.OperationalError as e:
            logger.error(f"데이터베이스 연결 실패: {e}")
            raise PostgreSQLConnectionError(f"데이터베이스 연결 실패: {e}")

    def _ensure_tables_exist(self) -> None:
        """필요한 테이블이 존재하는지 확인하고, 없으면 생성합니다."""
        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            # 트리 상태 테이블
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS tree_states (
                    id SERIAL PRIMARY KEY,
                    name TEXT NOT NULL,
                    state JSONB NOT NULL,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # 트리 스냅샷 테이블
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS tree_snapshots (
                    id SERIAL PRIMARY KEY,
                    tree_state_id INT REFERENCES tree_states(id) ON DELETE CASCADE,
                    name TEXT NOT NULL,
                    snapshot JSONB NOT NULL,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                )
            """)

            conn.commit()
        except PostgreSQLConnectionError as e:
            logger.error(f"테이블 생성 실패: {e}")
        finally:
            if conn:
                conn.close()

    def save(self, tree: IMTTree, name: Optional[str] = None) -> str:
        """트리를 데이터베이스에 저장합니다.
        
        Args:
            tree: 저장할 트리 객체
            name: 트리 이름 (없으면 타임스탬프 사용)
            
        Returns:
            저장된 트리의 식별자 (ID)
            
        Raises:
            PostgreSQLConnectionError: 데이터베이스 연결 실패 시
        """
        # 트리 이름 생성 (없는 경우)
        if name is None:
            name = f"tree_{int(time.time())}"
            
        # 트리를 JSON으로 직렬화
        tree_json = self.to_json(tree)
        
        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # 기존 트리가 있는지 확인
            cursor.execute(
                "SELECT id FROM tree_states WHERE name = %s",
                (name,)
            )
            result = cursor.fetchone()
            
            if result:
                # 기존 트리 업데이트
                tree_id = result[0]
                cursor.execute(
                    """
                    UPDATE tree_states 
                    SET state = %s, updated_at = CURRENT_TIMESTAMP 
                    WHERE id = %s
                    """,
                    (tree_json, tree_id)
                )
            else:
                # 새 트리 삽입
                cursor.execute(
                    """
                    INSERT INTO tree_states (name, state) 
                    VALUES (%s, %s) 
                    RETURNING id
                    """,
                    (name, tree_json)
                )
                tree_id = cursor.fetchone()[0]
                
            conn.commit()
            return str(tree_id)
            
        except psycopg2.Error as e:
            if conn:
                conn.rollback()
            logger.error(f"트리 저장 실패: {e}")
            raise
        finally:
            if conn:
                conn.close()

    def load(self, identifier: Optional[str] = None) -> IMTTree:
        """트리를 데이터베이스에서 불러옵니다.
        
        Args:
            identifier: 트리 식별자 (ID 또는 이름, 없으면 최신 트리)
            
        Returns:
            IMTTree 객체
            
        Raises:
            PostgreSQLConnectionError: 데이터베이스 연결 실패 시
            TreeNotFoundError: 트리를 찾을 수 없을 때
        """
        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            if identifier is None:
                # 최신 트리 불러오기
                cursor.execute(
                    "SELECT state FROM tree_states ORDER BY updated_at DESC LIMIT 1"
                )
            elif identifier.isdigit():
                # ID로 불러오기
                cursor.execute(
                    "SELECT state FROM tree_states WHERE id = %s",
                    (int(identifier),)
                )
            else:
                # 이름으로 불러오기
                cursor.execute(
                    "SELECT state FROM tree_states WHERE name = %s",
                    (identifier,)
                )
                
            result = cursor.fetchone()
            if not result:
                raise TreeNotFoundError(f"트리를 찾을 수 없음: {identifier}")
                
            tree_json = result[0]
            return self.from_json(json.dumps(tree_json))
            
        except psycopg2.Error as e:
            logger.error(f"트리 불러오기 실패: {e}")
            raise
        finally:
            if conn:
                conn.close()

    def delete(self, identifier: str) -> bool:
        """저장된 트리를 삭제합니다.
        
        Args:
            identifier: 트리 식별자 (ID 또는 이름)
            
        Returns:
            성공 여부
        """
        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            if identifier.isdigit():
                # ID로 삭제
                cursor.execute(
                    "DELETE FROM tree_states WHERE id = %s",
                    (int(identifier),)
                )
            else:
                # 이름으로 삭제
                cursor.execute(
                    "DELETE FROM tree_states WHERE name = %s",
                    (identifier,)
                )
                
            deleted = cursor.rowcount > 0
            conn.commit()
            return deleted
            
        except psycopg2.Error as e:
            if conn:
                conn.rollback()
            logger.error(f"트리 삭제 실패: {e}")
            return False
        finally:
            if conn:
                conn.close()

    def get_all_trees(self) -> List[Tuple[str, str, str]]:
        """저장된 모든 트리의 목록을 가져옵니다.
        
        Returns:
            트리 목록 (ID, 이름, 업데이트 시간)의 튜플
        """
        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute(
                "SELECT id, name, updated_at FROM tree_states ORDER BY updated_at DESC"
            )
            
            trees = [
                (str(row[0]), row[1], str(row[2])) 
                for row in cursor.fetchall()
            ]
            return trees
            
        except psycopg2.Error as e:
            logger.error(f"트리 목록 불러오기 실패: {e}")
            return []
        finally:
            if conn:
                conn.close()

    def create_snapshot(self, tree_id: str, name: Optional[str] = None) -> str:
        """트리의 스냅샷을 생성합니다.
        
        Args:
            tree_id: 트리 ID
            name: 스냅샷 이름 (없으면 타임스탬프 사용)
            
        Returns:
            생성된 스냅샷의 ID
        """
        if name is None:
            name = f"snapshot_{int(time.time())}"
            
        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # 트리 데이터 가져오기
            cursor.execute(
                "SELECT state FROM tree_states WHERE id = %s",
                (int(tree_id),)
            )
            
            result = cursor.fetchone()
            if not result:
                raise TreeNotFoundError(f"트리를 찾을 수 없음: {tree_id}")
                
            tree_state = result[0]
            
            # 스냅샷 저장
            cursor.execute(
                """
                INSERT INTO tree_snapshots (tree_state_id, name, snapshot) 
                VALUES (%s, %s, %s)
                RETURNING id
                """,
                (int(tree_id), name, Json(tree_state))
            )
            
            snapshot_id = cursor.fetchone()[0]
            conn.commit()
            return str(snapshot_id)
            
        except psycopg2.Error as e:
            if conn:
                conn.rollback()
            logger.error(f"스냅샷 생성 실패: {e}")
            raise
        finally:
            if conn:
                conn.close()

    def restore_snapshot(self, snapshot_id: str) -> str:
        """스냅샷을 복원합니다.
        
        Args:
            snapshot_id: 스냅샷 ID
            
        Returns:
            복원된 트리의 ID
        """
        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # 스냅샷 데이터 가져오기
            cursor.execute(
                """
                SELECT s.tree_state_id, s.snapshot, t.name
                FROM tree_snapshots s
                JOIN tree_states t ON s.tree_state_id = t.id
                WHERE s.id = %s
                """,
                (int(snapshot_id),)
            )
            
            result = cursor.fetchone()
            if not result:
                raise TreeNotFoundError(f"스냅샷을 찾을 수 없음: {snapshot_id}")
                
            tree_id, snapshot_data, tree_name = result
            
            # 복원된 트리 이름 생성
            restored_name = f"{tree_name}_restored_{int(time.time())}"
            
            # 복원된 트리 저장
            cursor.execute(
                """
                INSERT INTO tree_states (name, state) 
                VALUES (%s, %s) 
                RETURNING id
                """,
                (restored_name, Json(snapshot_data))
            )
            
            new_tree_id = cursor.fetchone()[0]
            conn.commit()
            return str(new_tree_id)
            
        except psycopg2.Error as e:
            if conn:
                conn.rollback()
            logger.error(f"스냅샷 복원 실패: {e}")
            raise
        finally:
            if conn:
                conn.close()

    def to_json(self, tree: IMTTree) -> Dict[str, Any]:
        """트리를 JSON으로 변환합니다.
        
        Args:
            tree: IMTTree 객체
            
        Returns:
            JSON으로 변환된 트리 데이터
        """
        return tree.to_dict()

    def from_json(self, json_str: str) -> IMTTree:
        """JSON에서 트리를 생성합니다.
        
        Args:
            json_str: JSON 문자열
            
        Returns:
            IMTTree 객체
            
        Raises:
            ValueError: 잘못된 JSON 형식
        """
        try:
            tree_data = json.loads(json_str)
            return MTTree.from_dict(tree_data)
        except json.JSONDecodeError as e:
            logger.error(f"JSON 파싱 실패: {e}")
            raise ValueError(f"잘못된 JSON 형식: {e}") 