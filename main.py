"""메인 애플리케이션 모듈

애플리케이션의 진입점을 제공합니다.
"""
import sys
import os

# --- src 폴더를 sys.path에 추가 ---
# 현재 main.py 파일의 디렉터리 (루트)를 기준으로 src 폴더의 절대 경로를 생성
SRC_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), 'src'))
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR) # sys.path[0]에 추가하여 가장 먼저 검색되도록 함
# --- src 폴더 추가 완료 ---

from dotenv import load_dotenv
from view.impl.tree_main import main

# 환경변수 로드
load_dotenv()

# MACRO_TREE_DEBUG 환경 변수 설정 (예시)

if __name__ == "__main__":
    main()