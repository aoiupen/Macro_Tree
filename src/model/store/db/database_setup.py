import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from contextlib import contextmanager

from .models import Base # src.model.store.db.models에서 Base를 가져옵니다.

# 기존 postgres_repo.py의 연결 정보와 유사하게 설정
DB_HOST = os.environ.get("DB_HOST", "localhost")
DB_PORT = os.environ.get("DB_PORT", "5432")
DB_NAME = os.environ.get("DB_NAME", "macro_tree") # 데이터베이스 이름은 동일하게 유지하거나 필요시 변경
DB_USER = os.environ.get("DB_USER", "postgres")
DB_PASSWORD = os.environ.get("DB_PASSWORD") # 환경 변수에서 비밀번호를 가져옵니다.

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# echo=True로 설정하면 실행되는 SQL 쿼리를 로깅합니다. (개발 시 유용)
engine = create_engine(DATABASE_URL, echo=False) 

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    """데이터베이스 테이블을 생성합니다.
    애플리케이션 시작 시 또는 필요할 때 한 번 호출되어야 합니다.
    MTItem 모델에 정의된 테이블 (mt_items)을 생성합니다.
    """
    # Base.metadata.drop_all(bind=engine) # 기존 테이블 삭제 (테스트 시)
    Base.metadata.create_all(bind=engine)

@contextmanager
def get_db_session():
    """데이터베이스 세션을 제공하고, 사용 후 자동으로 닫는 컨텍스트 매니저입니다.
    
    사용 예시:
    with get_db_session() as db:
        # db 세션 사용
        pass
    """
    session = scoped_session(SessionLocal)
    try:
        yield session
    except Exception:
        session.rollback()
        raise
    finally:
        session.remove()

# 애플리케이션 시작 시 DB 초기화를 위한 간단한 헬퍼 (필요한 경우 사용)
# def main_init_db():
#     print("Initializing database...")
#     init_db()
#     print("Database initialized.")

# if __name__ == "__main__":
#     main_init_db() 