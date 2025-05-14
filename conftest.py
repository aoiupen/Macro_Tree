import sys
import os

# 현재 conftest.py 파일이 있는 디렉토리(프로젝트 루트)를 sys.path에 추가합니다.
# 이렇게 하면 pytest 실행 시 하위 'src' 폴더를 패키지로 인식할 수 있습니다.
SRC_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), 'src'))
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)
