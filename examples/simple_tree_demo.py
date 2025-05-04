import sys
import os

# Python 경로 설정
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from view.implementations.simple_tree_app import main

if __name__ == "__main__":
    main()
