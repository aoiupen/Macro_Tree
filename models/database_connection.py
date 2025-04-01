"""데이터베이스 연결 모듈

데이터베이스 연결 관련 기능을 제공합니다.
"""
import os
import psycopg2
import logging
from getpass import getpass
from dotenv import load_dotenv
from typing import Optional

# 로깅 설정
logger = logging.getLogger(__name__)

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
        self._connection_params = self._get_connection_params()
        self._password_attempts = 0
        self._max_attempts = 3
        self._connection = None
    
    def _get_connection_params(self) -> dict:
        """환경변수에서 연결 파라미터를 가져와 검증합니다."""
        # 기본값과 함께 환경 변수에서 파라미터 가져오기
        host = os.getenv("DB_HOST", "localhost")
        port = os.getenv("DB_PORT", "5432")
        dbname = os.getenv("DB_NAME", "postgres")
        user = os.getenv("DB_USER", "postgres")
        
        # 기본 검증 (예: 포트 범위 확인)
        try:
            port_num = int(port)
            if port_num < 1 or port_num > 65535:
                logger.warning(f"올바르지 않은 포트 번호: {port}, 기본값 5432 사용")
                port = "5432"
        except ValueError:
            logger.warning(f"올바르지 않은 포트 형식: {port}, 기본값 5432 사용")
            port = "5432"
            
        return {
            "host": host,
            "port": port,
            "dbname": dbname,
            "user": user
        }
    
    def connect(self) -> Optional[psycopg2.extensions.connection]:
        """데이터베이스에 연결합니다."""
        # 이미 연결되어 있으면 기존 연결 반환
        if self._connection is not None:
            if not self._connection.closed:
                return self._connection
        
        # 최대 시도 횟수를 초과하면 None 반환
        if self._password_attempts >= self._max_attempts:
            print("비밀번호 시도 횟수를 초과했습니다.")
            return None
            
        try:
            # 연결 파라미터 복사 (비밀번호 추가용)
            conn_params = self._connection_params.copy()
            
            # 비밀번호 환경변수 확인
            password = os.getenv("DB_PASSWORD")
            
            # 환경변수에 비밀번호가 없으면 입력받음
            if not password:
                print(f"PostgreSQL 데이터베이스 비밀번호를 입력하세요 (시도 {self._password_attempts+1}/{self._max_attempts}):")
                password = getpass()
            
            # 연결 파라미터에 비밀번호 추가
            conn_params["password"] = password
            
            # 연결 시도 (문자열 대신 키워드 인자 사용)
            self._connection = psycopg2.connect(**conn_params)
            
            # 성공하면 시도 횟수 초기화
            self._password_attempts = 0
            print("데이터베이스에 성공적으로 연결되었습니다.")
            
            # 사용 후 비밀번호 메모리에서 삭제
            del conn_params["password"]
            password = None
            
            return self._connection
            
        except psycopg2.OperationalError as e:
            # 비밀번호 인증 실패 시에 시도 횟수 증가
            if "password authentication failed" in str(e):
                self._password_attempts += 1
                print(f"비밀번호가 일치하지 않습니다. ({self._password_attempts}/{self._max_attempts})")
                
                # 최대 시도 횟수 미만이면 재귀적으로 다시 시도
                if self._password_attempts < self._max_attempts:
                    return self.connect()
            else:
                # 일반적인 오류 메시지 표시 (상세 내용은 로그에만 기록)
                print("데이터베이스 연결에 실패했습니다. 로그를 확인하세요.")
                logger.error(f"데이터베이스 연결 오류: {e}")
            
            return None
    
    def disconnect(self) -> None:
        """데이터베이스 연결을 종료합니다."""
        if self._connection and not self._connection.closed:
            self._connection.close()
            self._connection = None