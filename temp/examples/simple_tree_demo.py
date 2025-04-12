import sys
import os

# temp 패키지를 Python 경로에 추가
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from temp.view.implementations.simple_tree_app import main

if __name__ == "__main__":
    main()
