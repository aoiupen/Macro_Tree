import pytest
from core.impl.tree import MTTree, MTItem
import core.exceptions as exc

@pytest.fixture
def tree():
    tree = MTTree(tree_id="root", name="Root Tree")
    root_item = MTItem("root", {"name": "Root", "parent_id": None, "node_type": "group"})
    group1 = MTItem("group1", {"name": "Group 1", "parent_id": "root", "node_type": "group"})
    group2 = MTItem("group2", {"name": "Group 2", "parent_id": "root", "node_type": "group"})
    subgroup2 = MTItem("subgroup2", {"name": "Sub Group 2", "parent_id": "group2", "node_type": "group"})
    tree.add_item(root_item, None)
    tree.add_item(group1, "root")
    tree.add_item(group2, "root")
    tree.add_item(subgroup2, "group2")
    # group2의 하위 항목 4개 중 2개는 group2, 2개는 subgroup2에 추가
    group2_items = []
    for i in range(4):
        item = MTItem(f"item-g2-{i}", {"name": f"Item {i} in Group 2", "parent_id": None, "node_type": "instruction"})
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
        sub_item = MTItem(f"item-g2-{i}-sub", {"name": f"Sub-item of {i}", "parent_id": "group2", "node_type": "instruction"})
        tree.add_item(sub_item, "group2")
    for i in range(2, 4):
        sub_item = MTItem(f"item-g2-{i}-sub", {"name": f"Sub-item of {i}", "parent_id": "subgroup2", "node_type": "instruction"})
        tree.add_item(sub_item, "subgroup2")
    return tree

def test_move_group(tree):
    # group1을 group2 아래로 이동
    assert tree.move_item("group1", "group2") is True
    assert tree.get_item("group1").get_property("parent_id") == "group2"
    assert "group1" in tree.get_item("group2").get_property("children_ids", [])

def test_move_instruction(tree):
    # instr1을 group2 아래로 이동
    assert tree.move_item("instr1", "group2") is True
    assert tree.get_item("instr1").get_property("parent_id") == "group2"
    assert "instr1" in tree.get_item("group2").get_property("children_ids", [])
    assert "instr1" not in tree.get_item("group1").get_property("children_ids", [])

def test_move_group_to_root(tree):
    # group1을 루트로 이동
    assert tree.move_item("group1", None) is True
    assert tree.get_item("group1").get_property("parent_id") is None

def test_move_instruction_to_root(tree):
    # instr1을 루트로 이동
    assert tree.move_item("instr1", None) is True
    assert tree.get_item("instr1").get_property("parent_id") is None

def test_move_group_to_instruction(tree):
    # 그룹을 instruction 아래로 이동 시도 (비즈니스 룰에 따라 허용/금지)
    # 예: instruction 타입 아래에는 자식이 올 수 없도록 금지한다면
    instr1 = tree.get_item("instr1")
    if instr1.get_property("node_type") == "instruction":
        with pytest.raises(Exception):  # 실제 예외 타입으로 변경
            tree.move_item("group1", "instr1")
    else:
        # 허용되는 구조라면 정상 이동 테스트
        assert tree.move_item("group1", "instr1") is True
