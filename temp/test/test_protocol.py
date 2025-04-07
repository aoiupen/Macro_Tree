import pytest
from typing import Protocol, runtime_checkable

from temp.core.tree import IMTTreeReadable
from test.mocks.mock_tree import MockTree

def test_mock_tree_implements_readable_protocol():
    """MockTree가 IMTTreeReadable 프로토콜을 구현하는지 검증"""
    # Protocol이 runtime_checkable이라면 직접 검증 가능
    if getattr(IMTTreeReadable, "_is_runtime_protocol", False):
        assert isinstance(MockTree(), IMTTreeReadable)
    
    # 또는 메서드 존재 확인으로 검증
    mock = MockTree()
    assert hasattr(mock, "get_item")
    assert hasattr(mock, "get_children")
    
    # 메서드 시그니처 검증은 typing 모듈의 한계로 어려움
