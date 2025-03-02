# config.py
import os
from dotenv import load_dotenv

load_dotenv()

PROJECT_ROOT = os.path.abspath(os.getenv("PROJECT_ROOT", ".")) # 기본값으로 현재 디렉토리 사용

if not os.path.exists(PROJECT_ROOT):
    print(f"Error: PROJECT_ROOT '{PROJECT_ROOT}' does not exist.")
    PROJECT_ROOT = None

DEBUG = os.getenv("DEBUG", "False").lower() == "true"

# 데이터베이스 연결 정보
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")