import importlib

def test_utils_import():
    # utils.py가 정상적으로 import되는지만 확인
    importlib.import_module("core.impl.utils") 