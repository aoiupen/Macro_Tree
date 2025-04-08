from typing import Protocol, runtime_checkable

import pytest

from temp.core.tree import IMTTreeReadable
from temp.test.mocks.mock_tree import MockTree


def test_mock_tree_implements_readable_protocol():
    """MockTree가 IMTTreeReadable 프로토콜을 구현하는지 검증"""
    # IMTTreeReadable에 @runtime_checkable 데코레이터가 추가되어 있어야 함
    assert isinstance(MockTree(), IMTTreeReadable)
    
    # 또는 메서드 존재 확인으로 검증
    mock = MockTree()
    assert hasattr(mock, "get_item")
    assert hasattr(mock, "get_children")
    
    # 메서드 시그니처 검증은 typing 모듈의 한계로 어려움
