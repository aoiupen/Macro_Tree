"""메인 애플리케이션 모듈

애플리케이션의 진입점을 제공합니다.
"""
import sys
import os
from dotenv import load_dotenv
from view.impl.tree_main import main

# 환경변수 로드
load_dotenv()

# MACRO_TREE_DEBUG 환경 변수 설정 (예시)

if __name__ == "__main__":
    main()