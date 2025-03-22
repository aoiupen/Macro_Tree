"""데이터베이스 연결 모듈"""
import os
import psycopg2
from dotenv import load_dotenv
from typing import Optional

class DatabaseConnection:
    """데이터베이스 연결 싱글톤 클래스"""
    
    _instance = None
    _connection = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseConnection, cls).__new__(cls)
        return cls._instance
    
    def connect(self) -> Optional[psycopg2.extensions.connection]:
        """데이터베이스에 연결합니다."""
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