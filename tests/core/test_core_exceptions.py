import pytest
from core.exceptions import TreeException

def test_tree_exception():
    with pytest.raises(TreeException):
        raise TreeException("Test error") 