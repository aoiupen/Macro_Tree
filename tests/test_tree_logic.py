import pytest
from core.impl.tree import MTTree, MTItem
import sys
import os
import core.exceptions as exc
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# RF : python -m pytest tests/test_tree_logic.py
@pytest.fixture
def tree():
    tree = MTTree(tree_id="root", name="Root Tree")
    root_item = MTItem("root", {"name": "Root", "parent_id": None})
    group1 = MTItem("group1", {"name": "Group 1", "parent_id": "root"})
    group2 = MTItem("group2", {"name": "Group 2", "parent_id": "root"})
    subgroup2 = MTItem("subgroup2", {"name": "Sub Group 2", "parent_id": "group2"})
    tree.add_item(root_item, None)
    tree.add_item(group1, "root")
    tree.add_item(group2, "root")
    tree.add_item(subgroup2, "group2")
    # group2의 하위 항목 4개 중 2개는 group2, 2개는 subgroup2에 추가
    group2_items = []
    for i in range(4):
        item = MTItem(f"item-g2-{i}", {"name": f"Item {i} in Group 2", "parent_id": None})
        group2_items.append(item)
    for i, item in enumerate(group2_items):
        if i < 2:
            item._data.parent_id = "group2"
            tree.add_item(item, "group2")
        else:
            item._data.parent_id = "subgroup2"
            tree.add_item(item, "subgroup2")
    # 서브 아이템도 추가
    for i in range(2):
        sub_item = MTItem(f"item-g2-{i}-sub", {"name": f"Sub-item of {i}", "parent_id": "group2"})
        tree.add_item(sub_item, "group2")
    for i in range(2, 4):
        sub_item = MTItem(f"item-g2-{i}-sub", {"name": f"Sub-item of {i}", "parent_id": "subgroup2"})
        tree.add_item(sub_item, "subgroup2")
    return tree

# def test_add_item(tree):
#     new_item = MTItem("item2", {"name": "Item 2", "parent_id": "group1"})
#     tree.add_item(new_item, "group1")
#     assert tree.get_item("item2") is not None
#     assert "item2" in tree.get_item("group1").get_property("children_ids")

# def test_remove_item(tree):
#     assert tree.remove_item("item1")

def test_move_item_normal(tree):
    assert tree.move_item("item1", "group2") is True
    assert tree.get_item("item1").get_property("parent_id") == "group2"
    assert "item1" in tree.get_item("group2").get_property("children_ids", [])
    assert "item1" not in tree.get_item("group1").get_property("children_ids", [])

def test_move_item_same_parent(tree):
    assert tree.move_item("item1", "group1") is False  # 이미 같은 부모

def test_move_item_to_root(tree):
    assert tree.move_item("item1", None) is True
    assert tree.get_item("item1").get_property("parent_id") is None

def test_move_item_to_nonexistent_parent(tree):
    with pytest.raises(exc.MTItemNotFoundError):
        tree.move_item("item1", "not_exist")

def test_move_item_circular(tree):
    # group1의 자식인 item1을 group1의 자손으로 이동 시도(순환 참조)
    tree.add_item(MTItem("item2", {"name": "Item 2", "parent_id": "item1"}), "item1")
    with pytest.raises(exc.MTTreeError):
        tree.move_item("group1", "item2") 