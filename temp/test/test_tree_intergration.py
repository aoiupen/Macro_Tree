from typing import Dict, List, Optional

from temp.core.tree import IMTTreeReadable
from temp.test.mocks.mock_tree import MockTree


def test_tree_read_operations()-> None:
    """트리 읽기 작업 테스트"""
    # 테스트 데이터 설정
    test_items = [
        {"id": "1", "name": "Root", "parent_id": None},
        {"id": "2", "name": "Child1", "parent_id": "1"},
        {"id": "3", "name": "Child2", "parent_id": "1"}
    ]
    
    # Mock 구현체 생성
    tree: IMTTreeReadable = MockTree(test_items)
    
    # 작업 테스트
    item = tree.get_item("1")
    assert item is not None  # None이 아님을 확인
    assert item["name"] == "Root"
    children = tree.get_children("1")
    assert len(children) == 2
    child1 = children[0]
    child2 = children[1]
    assert child1 is not None  # None이 아님을 확인
    assert child2 is not None  # None이 아님을 확인
    assert child1["id"] == "2"
    assert child2["id"] == "3"
    # 테스트 코드
