import os
import psycopg2
from getpass import getpass
from dotenv import load_dotenv

class DatabaseConnection:
    def __init__(self):
        load_dotenv()  # .env 파일에서 환경 변수 로드
        self.connection = None

    def connect(self):
        if self.connection is not None:
            print("Already connected to the database.")
            return self.connection

        try:
            # 데이터베이스 연결 정보 환경 변수에서 가져오기
            db_name = os.getenv("DB_NAME")
            user = os.getenv("DB_USER")
            host = os.getenv("DB_HOST")
            port = os.getenv("DB_PORT")

            # 비밀번호 입력
            password = getpass("Enter your database password: ")

            # 데이터베이스에 연결
            self.connection = psycopg2.connect(
                dbname=db_name,
                user=user,
                password=password,
                host=host,
                port=port
            )
            print("Connected to the database.")
            return self.connection

        except psycopg2.OperationalError as e:
            print(f"Database connection error: {e}")
            return None 