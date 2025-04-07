from temp.core.tree import IMTTreeReadable
from test.mocks.mock_tree import MockTree

def test_tree_read_operations():
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
    assert tree.get_item("1")["name"] == "Root"
    children = tree.get_children("1")
    assert len(children) == 2
    assert children[0]["id"] == "2"
    assert children[1]["id"] == "3"
