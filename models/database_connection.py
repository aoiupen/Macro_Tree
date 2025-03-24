"""데이터베이스 연결 모듈

데이터베이스 연결 관련 기능을 제공합니다.
"""
import os
import psycopg2
from getpass import getpass
from dotenv import load_dotenv
from typing import Optional

class DatabaseConnection:
    """데이터베이스 연결 클래스
    
    데이터베이스 연결을 관리합니다.
    """
    
    _instance = None
    _connection = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseConnection, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        """DatabaseConnection 생성자"""
        # 환경 변수 로드
        load_dotenv()
        self.conn_string = self._build_connection_string()
        self._password_attempts = 0
        self._max_attempts = 3
        self._connection = None
    
    def _build_connection_string(self) -> str:
        """환경변수에서 연결 문자열을 생성합니다."""
        host = os.getenv("DB_HOST", "localhost")
        port = os.getenv("DB_PORT", "5432")
        dbname = os.getenv("DB_NAME", "postgres")
        user = os.getenv("DB_USER", "postgres")
        # 비밀번호는 포함하지 않음 (나중에 직접 입력)
        return f"host={host} port={port} dbname='{dbname}' user={user}"
    
    def connect(self) -> Optional[psycopg2.extensions.connection]:
        """데이터베이스에 연결합니다.
        
        사용자에게 비밀번호를 직접 입력받아 연결합니다.
        비밀번호가 잘못되면 최대 3번까지 재시도할 수 있습니다.
        
        Returns:
            데이터베이스 연결 객체 또는 None
        """
        # 이미 연결되어 있으면 기존 연결 반환
        if self._connection is not None:
            if not self._connection.closed:
                return self._connection
        
        # 최대 시도 횟수를 초과하면 None 반환
        if self._password_attempts >= self._max_attempts:
            print("비밀번호 시도 횟수를 초과했습니다.")
            return None
            
        try:
            # 비밀번호 환경변수 확인
            password = os.getenv("DB_PASSWORD")
            
            # 환경변수에 비밀번호가 없으면 입력받음
            if not password:
                print(f"PostgreSQL 데이터베이스 비밀번호를 입력하세요 (시도 {self._password_attempts+1}/{self._max_attempts}):")
                password = getpass()
            
            # 연결 문자열에 비밀번호 추가
            conn_string_with_password = f"{self.conn_string} password={password}"
            
            # 연결 시도
            self._connection = psycopg2.connect(conn_string_with_password)
            
            # 성공하면 시도 횟수 초기화
            self._password_attempts = 0
            print("데이터베이스에 성공적으로 연결되었습니다.")
            
            return self._connection
            
        except psycopg2.OperationalError as e:
            # 비밀번호 인증 실패 시 시도 횟수 증가
            if "password authentication failed" in str(e):
                self._password_attempts += 1
                print(f"비밀번호가 일치하지 않습니다. ({self._password_attempts}/{self._max_attempts})")
                
                # 최대 시도 횟수 미만이면 재귀적으로 다시 시도
                if self._password_attempts < self._max_attempts:
                    return self.connect()
            else:
                print(f"데이터베이스 연결 오류: {e}")
            
            return None
    
    def disconnect(self) -> None:
        """데이터베이스 연결을 종료합니다."""
        if self._connection and not self._connection.closed:
            self._connection.close()
            self._connection = None