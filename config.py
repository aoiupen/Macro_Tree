"""설정 모듈

환경 변수와 프로젝트 설정을 관리하는 모듈입니다.
"""
import os
from typing import Optional
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()

# 프로젝트 루트 디렉토리 설정
PROJECT_ROOT: str = os.path.abspath(os.getenv("PROJECT_ROOT", "."))  # 기본값으로 현재 디렉토리 사용

if not os.path.exists(PROJECT_ROOT):
    print(f"Error: PROJECT_ROOT '{PROJECT_ROOT}' does not exist.")
    PROJECT_ROOT = None

# 디버그 모드 설정
DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"

# 데이터베이스 연결 정보
DB_NAME: Optional[str] = os.getenv("DB_NAME")
DB_USER: Optional[str] = os.getenv("DB_USER")
DB_HOST: Optional[str] = os.getenv("DB_HOST")
DB_PORT: Optional[str] = os.getenv("DB_PORT")