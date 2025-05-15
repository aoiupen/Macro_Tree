import pytest
import copy
from src.core.impl.item import MTTreeItem
from src.core.interfaces.base_item_data import MTTreeItemData, MTNodeType

def test_item_create_and_basic_properties():
    # 1. initial_data가 dict일 때
    initial_dict_data = {"name": "Test Item Dict", "node_type": MTNodeType.GROUP, "children_ids": ["child1"]}
    item1 = MTTreeItem("item1", initial_dict_data)
    assert item1.id == "item1"
    
    item1_data = item1.data
    assert isinstance(item1_data, MTTreeItemData)
    assert item1_data.name == "Test Item Dict"
    assert item1_data.node_type == MTNodeType.GROUP
    assert item1_data.children_ids == ["child1"]
    if "id" in initial_dict_data:
        assert item1_data.id == initial_dict_data["id"]
    else:
        assert item1_data.id == "item1"

    # 2. initial_data가 MTTreeItemData 객체일 때
    initial_obj_data = MTTreeItemData(id="item2_data_id", name="Test Item Obj", node_type=MTNodeType.INSTRUCTION)
    item2 = MTTreeItem("item2_item_id", initial_obj_data)
    assert item2.id == "item2_item_id"
    item2_data = item2.data
    assert item2_data.name == "Test Item Obj"
    assert item2_data.node_type == MTNodeType.INSTRUCTION
    assert item2_data.id == "item2_data_id"

    # 3. initial_data가 None일 때
    item3 = MTTreeItem("item3", None)
    assert item3.id == "item3"
    item3_data = item3.data
    assert item3_data.name == ""
    assert item3_data.node_type is None
    assert item3_data.id == "item3"

    # 4. MTTreeItemData에 없는 id를 item_id로 줄 때
    item4_data_obj = MTTreeItemData(name="Item 4 data")
    item4 = MTTreeItem("item4_id", item4_data_obj)
    assert item4.id == "item4_id"
    assert item4.data.name == "Item 4 data"
    assert item4.data.id is None

class TestMTTreeItem:

    @pytest.fixture
    def sample_item_data_dict(self):
        return {"name": "Sample Item", "node_type": MTNodeType.INSTRUCTION, "is_expanded": True, "children_ids": ["c1", "c2"]}

    @pytest.fixture
    def sample_item(self, sample_item_data_dict):
        return MTTreeItem("sample1", sample_item_data_dict)

    def test_id_property(self, sample_item):
        assert sample_item.id == "sample1"

    def test_data_property_returns_deepcopy(self, sample_item):
        data1 = sample_item.data
        data2 = sample_item.data
        assert data1 is not data2
        assert data1 == data2

        data1.name = "Modified Data1"
        assert sample_item.data.name == "Sample Item"

    def test_get_property(self, sample_item, sample_item_data_dict):
        assert sample_item.get_property("name") == sample_item_data_dict["name"]
        assert sample_item.get_property("node_type") == sample_item_data_dict["node_type"]
        assert sample_item.get_property("is_expanded") == sample_item_data_dict["is_expanded"]
        assert sample_item.get_property("children_ids") == sample_item_data_dict["children_ids"]
        assert sample_item.get_property("non_existent_key") is None
        assert sample_item.get_property("non_existent_key", "default_val") == "default_val"
        
        item_no_children_ids_field = MTTreeItem("item_no_children", {"name": "Test"})
        item_no_children_ids_field._data.children_ids = None
        assert item_no_children_ids_field.get_property("children_ids") == []

    def test_set_property(self, sample_item):
        sample_item.set_property("name", "New Name")
        assert sample_item.get_property("name") == "New Name"
        
        sample_item.set_property("new_custom_field", "custom_value")
        assert sample_item.get_property("new_custom_field") == "custom_value"

        new_children = ["c3", "c4"]
        sample_item.set_property("children_ids", new_children)
        assert sample_item.get_property("children_ids") == new_children

    def test_clone(self, sample_item):
        cloned_item = sample_item.clone()

        assert cloned_item is not sample_item
        assert cloned_item.id == sample_item.id
        
        assert cloned_item._data is not sample_item._data
        assert cloned_item.data == sample_item.data

        cloned_item.set_property("name", "Cloned New Name")
        assert sample_item.get_property("name") == "Sample Item"

        sample_item.set_property("name", "Original New Name")
        assert cloned_item.get_property("name") == "Cloned New Name"

    def test_initial_data_id_handling(self):
        # Case 1: initial_data (dict) 에 id가 명시된 경우
        item_c1 = MTTreeItem("item_id_c1", {"id": "data_id_c1", "name": "Test C1"})
        assert item_c1.id == "item_id_c1"
        assert item_c1.data.id == "data_id_c1"
        assert item_c1.data.name == "Test C1"

        # Case 2: initial_data (dict) 에 id가 명시되지 않은 경우
        item_c2 = MTTreeItem("item_id_c2", {"name": "Test C2"})
        assert item_c2.id == "item_id_c2"
        assert item_c2.data.id == "item_id_c2"
        assert item_c2.data.name == "Test C2"

        # Case 3: initial_data (MTTreeItemData) 에 id가 명시된 경우
        data_c3 = MTTreeItemData(id="data_id_c3", name="Test C3")
        item_c3 = MTTreeItem("item_id_c3", data_c3)
        assert item_c3.id == "item_id_c3"
        assert item_c3.data.id == "data_id_c3"
        assert item_c3.data.name == "Test C3"

        # Case 4: initial_data (MTTreeItemData) 에 id가 명시되지 않은 경우 (생성자에서 None)
        data_c4 = MTTreeItemData(name="Test C4")
        assert data_c4.id is None
        item_c4 = MTTreeItem("item_id_c4", data_c4)
        assert item_c4.id == "item_id_c4"
        assert item_c4.data.id is None
        assert item_c4.data.name == "Test C4"

        # Case 5: initial_data가 None인 경우
        item_c5 = MTTreeItem("item_id_c5", None)
        assert item_c5.id == "item_id_c5"
        assert item_c5.data.id == "item_id_c5"
        assert item_c5.data.name == "" 