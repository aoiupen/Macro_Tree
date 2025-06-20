import json
import logging
import os
import time
from typing import Any, Dict, List, Optional, Tuple

import psycopg2
from psycopg2 import sql
from psycopg2.extras import Json

from core.interfaces.base_tree import IMTTree, IMTTreeSerializable
from core.impl.tree import MTTree
from model.store.repo.interfaces.base_tree_repo import IMTStore
import core.exceptions as exc

logger = logging.getLogger(__name__)

class PostgreSQLConnectionError(Exception):
    """PostgreSQL 연결 오류"""
    pass

class TreeNotFoundError(Exception):
    """트리를 찾을 수 없음"""
    pass

class PostgreSQLTreeRepository(IMTStore, IMTTreeSerializable):
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

    def save(self, tree: IMTTree, tree_id: str | None = None) -> str:
        """트리를 데이터베이스에 저장합니다.
        
        Args:
            tree: 저장할 트리 객체
            tree_id: 트리 ID (None이면 새 ID 생성)
            
        Returns:
            저장된 트리의 식별자 (ID)
            
        Raises:
            PostgreSQLConnectionError: 데이터베이스 연결 실패 시
        """
        # 트리 이름 사용
        name = tree.name
            
        # 트리를 JSON으로 직렬화
        tree_data = tree.to_dict()
        
        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # 기존 트리가 있는지 확인
            if tree_id and tree_id.isdigit():
                cursor.execute(
                    "SELECT id FROM tree_states WHERE id = %s",
                    (int(tree_id),)
                )
                result = cursor.fetchone()
            else:
                result = None
            
            if result is not None:
                tree_id = result[0]
                cursor.execute(
                    """
                    UPDATE tree_states 
                    SET state = %s, name = %s, updated_at = CURRENT_TIMESTAMP 
                    WHERE id = %s
                    """,
                    (Json(tree_data), name, tree_id)
                )
            else:
                # 새 트리 삽입
                cursor.execute(
                    """
                    INSERT INTO tree_states (name, state) 
                    VALUES (%s, %s) 
                    RETURNING id
                    """,
                    (name, Json(tree_data))
                )
                insert_result = cursor.fetchone()
                if insert_result is not None:
                    tree_id = insert_result[0]
                else:
                    raise Exception("Failed to insert new tree and retrieve its ID.")
                
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

    def load(self, tree_id: str) -> IMTTree | None:
        """트리를 데이터베이스에서 불러옵니다.
        
        Args:
            tree_id: 트리 ID
            
        Returns:
            IMTTree 객체 또는 None (실패 시)
        """
        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            if tree_id.isdigit():
                # ID로 불러오기
                cursor.execute(
                    "SELECT state FROM tree_states WHERE id = %s",
                    (int(tree_id),)
                )
            else:
                # 이름으로 불러오기
                cursor.execute(
                    "SELECT state FROM tree_states WHERE name = %s",
                    (tree_id,)
                )
                
            result = cursor.fetchone()
            if result is not None:
                tree_data = result[0]
                return MTTree.from_dict(tree_data)
            else:
                logger.warning(f"트리를 찾을 수 없음: {tree_id}")
                return None
            
        except psycopg2.Error as e:
            logger.error(f"트리 불러오기 실패: {e}")
            return None
        finally:
            if conn:
                conn.close()

    def delete(self, tree_id: str) -> bool:
        """저장된 트리를 삭제합니다.
        
        Args:
            tree_id: 트리 ID
            
        Returns:
            성공 여부
        """
        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            if tree_id.isdigit():
                # ID로 삭제
                cursor.execute(
                    "DELETE FROM tree_states WHERE id = %s",
                    (int(tree_id),)
                )
            else:
                # 이름으로 삭제
                cursor.execute(
                    "DELETE FROM tree_states WHERE name = %s",
                    (tree_id,)
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
                
    def list_trees(self) -> Dict[str, str]:
        """사용 가능한 모든 트리 목록을 반환합니다.
        
        Returns:
            트리 ID를 키, 트리 이름을 값으로 하는 딕셔너리
        """
        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute(
                "SELECT id, name FROM tree_states ORDER BY updated_at DESC"
            )
            
            return {str(row[0]): row[1] for row in cursor.fetchall()}
            
        except psycopg2.Error as e:
            logger.error(f"트리 목록 불러오기 실패: {e}")
            return {}
        finally:
            if conn:
                conn.close()

    def to_json(self) -> str:
        """트리를 JSON 문자열로 변환합니다.
        
        참고: 이 메서드는 전체 저장소가 아닌 개별 트리에 적용됩니다.
        트리 객체에서 호출되어야 합니다.
        """
        raise NotImplementedError("저장소 자체는 JSON으로 변환할 수 없습니다. 트리 객체에서 사용하세요.")
    
    @classmethod
    def from_json(cls, json_str: str) -> Any:
        """JSON 문자열에서 트리를 생성합니다.
        
        Args:
            json_str: JSON 문자열
            
        Returns:
            생성된 트리 객체
            
        Raises:
            InvalidMTItemDomainDTOError: 잘못된 JSON 형식
        """
        try:
            # JSON을 딕셔너리로 변환
            tree_dict = json.loads(json_str)
            
            # 딕셔너리로부터 트리 생성
            return MTTree.from_dict(tree_dict)
        except json.JSONDecodeError as e:
            raise exc.InvalidMTItemDomainDTOError(f"잘못된 JSON 형식: {e}")
        except Exception as e:
            raise exc.MTTreeError(f"트리 생성 실패: {e}")
            
    # 추가 기능 - 스냅샷 관리
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
            if result is not None:
                tree_state = result[0]
            else:
                raise TreeNotFoundError(f"트리를 찾을 수 없음: {tree_id}")
                
            # 스냅샷 저장
            cursor.execute(
                """
                INSERT INTO tree_snapshots (tree_state_id, name, snapshot) 
                VALUES (%s, %s, %s)
                RETURNING id
                """,
                (int(tree_id), name, Json(tree_state))
            )
            
            snapshot_result = cursor.fetchone()
            if snapshot_result is not None:
                snapshot_id = snapshot_result[0]
            else:
                raise Exception("Failed to create snapshot and retrieve its ID.")
            
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
            if result is not None:
                tree_id, snapshot_data, tree_name = result
            else:
                raise TreeNotFoundError(f"스냅샷을 찾을 수 없음: {snapshot_id}")
                
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
            
            new_tree_result = cursor.fetchone()
            if new_tree_result is not None:
                new_tree_id = new_tree_result[0]
            else:
                raise Exception("Failed to restore tree and retrieve its ID.")
            
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

    # IMTTreeSerializable 인터페이스의 restore_state 메서드 구현
    def restore_state(self, data: Dict[str, Any]) -> None:
        """
        주어진 딕셔너리 데이터로부터 현재 트리 인스턴스의 상태를 복원합니다.
        이 메서드는 저장소 레벨에서는 직접적인 의미가 없을 수 있으므로,
        현재는 인터페이스 만족을 위해 비워둡니다.
        실제 상태 복원은 트리 객체 자체에서 담당해야 합니다.
        """
        # logger.warning("restore_state called on PostgreSQLTreeRepository, but it's a repository-level operation.")
        # 이 메서드는 인터페이스 요구사항을 충족시키기 위해 존재합니다.
        # 저장소 객체 자체가 특정 '상태'를 복원하는 것은 적합하지 않을 수 있습니다.
        # 실제 트리 데이터의 복원은 load 메서드 등을 통해 이루어집니다.
        pass 

    # IMTTreeSerializable 인터페이스의 dict_to_state 메서드 구현
    def dict_to_state(self, data_dict: dict) -> MTTree | None:
        """
        제공된 딕셔너리로부터 MTTree 객체를 생성하여 반환합니다.
        IMTTreeSerializable 인터페이스 구현의 일부입니다.
        """
        if not data_dict:
            # 빈 딕셔너리나 None이 입력된 경우 처리
            # 예를 들어, 경고를 로깅하거나 None을 반환할 수 있습니다.
            # print("Warning: dict_to_state received empty or None data_dict.")
            return None
        try:
            # MTTree 클래스에 from_dict 클래스 메서드가 구현되어 있다고 가정
            return MTTree.from_dict(data_dict)
        except Exception as e:
            # 실제 운영 환경에서는 적절한 로깅 프레임워크 사용 권장
            print(f"Error converting dictionary to MTTree state in PostgreSQLTreeRepository: {e}")
            # 필요에 따라 사용자 정의 예외를 발생시키거나, None을 반환하여 호출 측에서 처리하도록 할 수 있습니다.
            return None

    # tree_to_dict 메서드도 IMTTreeSerializable의 일부일 수 있으므로 확인 필요
    # 만약 그렇다면, 다음과 같이 구현될 수 있음:
    # def tree_to_dict(self, tree: IMTTree) -> dict | None:
    #     if not tree:
    #         return None
    #     try:
    #         return tree.to_dict()
    #     except Exception as e:
    #         print(f"Error converting MTTree state to dictionary: {e}")
    #         return None 