import pytest
from core.impl.tree import MTTree, MTTreeItem

@pytest.fixture
def tree():
    tree = MTTree(tree_id="root", name="Root Tree")
    root_item = MTTreeItem("root", {"name": "Root", "parent_id": None})
    group1 = MTTreeItem("group1", {"name": "Group 1", "parent_id": "root"})
    group2 = MTTreeItem("group2", {"name": "Group 2", "parent_id": "root"})
    subgroup2 = MTTreeItem("subgroup2", {"name": "Sub Group 2", "parent_id": "group2"})
    tree.add_item(root_item, None)
    tree.add_item(group1, "root")
    tree.add_item(group2, "root")
    tree.add_item(subgroup2, "group2")
    # group2의 하위 항목 4개 중 2개는 group2, 2개는 subgroup2에 추가
    group2_items = []
    for i in range(4):
        item = MTTreeItem(f"item-g2-{i}", {"name": f"Item {i} in Group 2", "parent_id": None})
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
        sub_item = MTTreeItem(f"item-g2-{i}-sub", {"name": f"Sub-item of {i}", "parent_id": "group2"})
        tree.add_item(sub_item, "group2")
    for i in range(2, 4):
        sub_item = MTTreeItem(f"item-g2-{i}-sub", {"name": f"Sub-item of {i}", "parent_id": "subgroup2"})
        tree.add_item(sub_item, "subgroup2")
    return tree

def assert_tree_consistency(tree):
    # 모든 아이템의 parent_id와 children_ids가 일관적인지 검증
    for item_id, item in tree.items.items():
        parent_id = item.get_property("parent_id")
        if parent_id:
            parent = tree.get_item(parent_id)
            assert parent is not None, f"부모 {parent_id}가 없음"
            assert item_id in parent.get_property("children_ids", []), f"{item_id}가 부모 {parent_id}의 children_ids에 없음"
        children_ids = item.get_property("children_ids", [])
        for child_id in children_ids:
            child = tree.get_item(child_id)
            assert child is not None, f"자식 {child_id}가 없음"
            assert child.get_property("parent_id") == item_id, f"자식 {child_id}의 parent_id가 {item_id}가 아님"

def test_move_item_consistency(tree):
    tree.move_item("item1", "group2")
    assert_tree_consistency(tree)
