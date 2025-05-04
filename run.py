#!/usr/bin/env python
"""
Macro_Tree 실행을 위한 스크립트
모듈 경로 문제를 해결하기 위해 이 스크립트를 통해 실행합니다.
"""
import os
import sys

# 프로젝트 루트 디렉토리를 PYTHONPATH에 추가
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# main.py 실행
from main import main

if __name__ == "__main__":
    sys.exit(main()) 