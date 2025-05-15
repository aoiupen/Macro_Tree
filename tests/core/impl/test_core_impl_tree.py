import pytest
from unittest.mock import Mock, call

from src.core.impl.tree import MTTree
from src.core.impl.item import MTTreeItem
from src.core.interfaces.base_item_data import MTNodeType
from src.model.events.interfaces.base_tree_event_mgr import IMTTreeEventManager, MTTreeEvent
import src.core.exceptions as exc

def test_tree_create():
    mock_event_manager = Mock(spec=IMTTreeEventManager)
    tree = MTTree(tree_id="root_tree_id", name="Root Tree", event_manager=mock_event_manager)
    assert tree.id == "root_tree_id"
    assert tree.name == "Root Tree"
    assert tree.root_id == MTTree.DUMMY_ROOT_ID
    assert MTTree.DUMMY_ROOT_ID in tree.items
    expected_calls = [
        call(MTTreeEvent.TREE_RESET, {}),
        call(MTTreeEvent.TREE_CRUD, {'tree_data': tree.to_dict()})
    ]
    mock_event_manager.notify.assert_has_calls(expected_calls, any_order=False)

class TestMTTree:

    @pytest.fixture
    def mock_event_manager(self):
        return Mock(spec=IMTTreeEventManager)

    @pytest.fixture
    def tree(self, mock_event_manager):
        return MTTree(tree_id="test_tree", name="Test Tree", event_manager=mock_event_manager)

    @pytest.fixture
    def item1(self):
        return MTTreeItem(item_id="item1", data={"name": "Item 1", "node_type": MTNodeType.INSTRUCTION})

    @pytest.fixture
    def item2(self):
        return MTTreeItem(item_id="item2", data={"name": "Item 2", "node_type": MTNodeType.GROUP})

    @pytest.fixture
    def item3(self):
        return MTTreeItem(item_id="item3", data={"name": "Item 3", "node_type": MTNodeType.INSTRUCTION})

    def test_add_item_to_root(self, tree, item1, mock_event_manager):
        mock_event_manager.reset_mock()
        tree.add_item(item1)
        assert tree.get_item("item1") == item1
        assert item1.get_property("parent_id") == tree.root_id
        root_item = tree.get_item(tree.root_id)
        assert "item1" in root_item.get_property("children_ids", [])
        
        expected_item_added_data = {"item_id": "item1", "parent_id": tree.root_id}
        expected_tree_crud_data = {"tree_data": tree.to_dict()}
        
        calls = [
            call(MTTreeEvent.ITEM_ADDED, expected_item_added_data),
            call(MTTreeEvent.TREE_CRUD, expected_tree_crud_data)
        ]
        mock_event_manager.notify.assert_has_calls(calls, any_order=False)

    def test_add_item_to_parent(self, tree, item1, item2, mock_event_manager):
        tree.add_item(item1)
        mock_event_manager.reset_mock()

        tree.add_item(item2, parent_id="item1")
        assert tree.get_item("item2") == item2
        assert item2.get_property("parent_id") == "item1"
        assert "item2" in item1.get_property("children_ids", [])

        expected_item_added_data = {"item_id": "item2", "parent_id": "item1"}
        expected_tree_crud_data = {"tree_data": tree.to_dict()}
        calls = [
            call(MTTreeEvent.ITEM_ADDED, expected_item_added_data),
            call(MTTreeEvent.TREE_CRUD, expected_tree_crud_data)
        ]
        mock_event_manager.notify.assert_has_calls(calls, any_order=False)

    def test_add_item_with_index(self, tree, item1, item2, item3, mock_event_manager):
        tree.add_item(item1)
        tree.add_item(item2)
        
        mock_event_manager.reset_mock()
        tree.add_item(item3, parent_id=tree.root_id, index=1)
        
        root_children = tree.get_children(tree.root_id)
        assert len(root_children) == 3
        assert root_children[0].id == "item1"
        assert root_children[1].id == "item3"
        assert root_children[2].id == "item2"
        assert item3.get_property("parent_id") == tree.root_id
        
        expected_item_added_data = {"item_id": "item3", "parent_id": tree.root_id}
        mock_event_manager.notify.assert_any_call(MTTreeEvent.ITEM_ADDED, expected_item_added_data)

    def test_add_item_already_exists(self, tree, item1):
        tree.add_item(item1)
        with pytest.raises(exc.MTTreeItemAlreadyExistsError):
            tree.add_item(item1)

    def test_add_item_non_existent_parent(self, tree, item1):
        with pytest.raises(exc.MTTreeItemNotFoundError):
            tree.add_item(item1, parent_id="non_existent_parent")

    def test_remove_item(self, tree, item1, item2, mock_event_manager):
        tree.add_item(item1)
        tree.add_item(item2, parent_id="item1")
        
        mock_event_manager.reset_mock()
        tree.remove_item("item2")
        assert tree.get_item("item2") is None
        assert "item2" not in item1.get_property("children_ids", [])
        
        expected_item_removed_data = {"item_id": "item2", "parent_id": "item1"}
        mock_event_manager.notify.assert_any_call(MTTreeEvent.ITEM_REMOVED, expected_item_removed_data)

        mock_event_manager.reset_mock()
        tree.remove_item("item1")
        assert tree.get_item("item1") is None
        root_item = tree.get_item(tree.root_id)
        assert "item1" not in root_item.get_property("children_ids", [])
        expected_item_removed_data_2 = {"item_id": "item1", "parent_id": tree.root_id}
        mock_event_manager.notify.assert_any_call(MTTreeEvent.ITEM_REMOVED, expected_item_removed_data_2)

    def test_remove_item_recursive(self, tree, item1, item2, item3, mock_event_manager):
        tree.add_item(item1)
        tree.add_item(item2, parent_id="item1")
        tree.add_item(item3, parent_id="item2")

        assert tree.get_item("item1") is not None
        assert tree.get_item("item2") is not None
        assert tree.get_item("item3") is not None
        
        mock_event_manager.reset_mock()
        tree.remove_item("item1")
        
        assert tree.get_item("item1") is None
        assert tree.get_item("item2") is None
        assert tree.get_item("item3") is None

        mock_event_manager.notify.assert_any_call(MTTreeEvent.ITEM_REMOVED, {"item_id": "item1", "parent_id": tree.root_id})

    def test_remove_non_existent_item(self, tree):
        with pytest.raises(exc.MTTreeItemNotFoundError):
            tree.remove_item("non_existent_item")

    def test_remove_dummy_root_item(self, tree):
        with pytest.raises(exc.MTTreeError, match="더미 루트 아이템은 삭제할 수 없습니다."):
            tree.remove_item(tree.root_id)

    def test_move_item_to_another_parent(self, tree, item1, item2, item3, mock_event_manager):
        tree.add_item(item1)
        tree.add_item(item2)
        tree.add_item(item3, parent_id="item1")
        
        mock_event_manager.reset_mock()
        tree.move_item("item3", new_parent_id="item2")
        
        assert item3.get_property("parent_id") == "item2"
        assert "item3" not in item1.get_property("children_ids", [])
        assert "item3" in item2.get_property("children_ids", [])
        
        expected_moved_data = {
            "item_id": "item3", 
            "new_parent_id": "item2", 
            "old_parent_id": "item1",
            "new_index": -1
        }
        mock_event_manager.notify.assert_any_call(MTTreeEvent.ITEM_MOVED, expected_moved_data)

    def test_move_item_to_root(self, tree, item1, item2, mock_event_manager):
        tree.add_item(item1)
        tree.add_item(item2, parent_id="item1")

        mock_event_manager.reset_mock()
        tree.move_item("item2", new_parent_id=tree.root_id)
        
        assert item2.get_property("parent_id") == tree.root_id
        assert "item2" not in item1.get_property("children_ids", [])
        root_item = tree.get_item(tree.root_id)
        assert "item2" in root_item.get_property("children_ids", [])
        
        expected_moved_data = {
            "item_id": "item2",
            "new_parent_id": tree.root_id,
            "old_parent_id": "item1",
            "new_index": -1
        }
        mock_event_manager.notify.assert_any_call(MTTreeEvent.ITEM_MOVED, expected_moved_data)

    def test_move_item_change_order_same_parent(self, tree, item1, item2, item3, mock_event_manager):
        tree.add_item(item1)
        tree.add_item(item2)
        tree.add_item(item3)

        mock_event_manager.reset_mock()
        tree.move_item("item3", new_parent_id=tree.root_id, new_index=0)
        
        root_children = tree.get_children(tree.root_id)
        assert len(root_children) == 3
        assert root_children[0].id == "item3"
        assert root_children[1].id == "item1"
        assert root_children[2].id == "item2"
        
        expected_moved_data = {
            "item_id": "item3",
            "new_parent_id": tree.root_id,
            "old_parent_id": tree.root_id,
            "new_index": 0
        }
        mock_event_manager.notify.assert_any_call(MTTreeEvent.ITEM_MOVED, expected_moved_data)

    def test_move_item_to_itself_or_descendant(self, tree, item1, item2):
        tree.add_item(item1)
        tree.add_item(item2, parent_id="item1")
        
        with pytest.raises(exc.MTTreeError, match="순환 참조 발생"):
            tree.move_item("item1", new_parent_id="item2")
        with pytest.raises(exc.MTTreeError, match="순환 참조 발생"):
             tree.move_item("item1", new_parent_id="item1")

    def test_move_item_non_existent_item_or_parent(self, tree, item1):
        tree.add_item(item1)
        with pytest.raises(exc.MTTreeItemNotFoundError):
            tree.move_item("non_existent_item", new_parent_id="item1")
        with pytest.raises(exc.MTTreeItemNotFoundError):
            tree.move_item("item1", new_parent_id="non_existent_parent")

    def test_move_dummy_root_item(self, tree):
        with pytest.raises(exc.MTTreeError, match="더미 루트 아이템은 이동할 수 없습니다."):
            tree.move_item(tree.root_id, new_parent_id=None)

    def test_modify_item(self, tree, item1, mock_event_manager):
        tree.add_item(item1)
        changes = {"name": "New Item 1 Name", "custom_prop": "value"}
        
        mock_event_manager.reset_mock()
        tree.modify_item("item1", changes)
        
        modified_item = tree.get_item("item1")
        assert modified_item.get_property("name") == "New Item 1 Name"
        assert modified_item.get_property("custom_prop") == "value"
        
        expected_modified_data = {"item_id": "item1", "changes": changes}
        mock_event_manager.notify.assert_any_call(MTTreeEvent.ITEM_MODIFIED, expected_modified_data)

    def test_modify_non_existent_item(self, tree):
        with pytest.raises(exc.MTTreeItemNotFoundError):
            tree.modify_item("non_existent_item", {"name": "test"})

    def test_get_item(self, tree, item1):
        assert tree.get_item("item1") is None
        tree.add_item(item1)
        assert tree.get_item("item1") == item1

    def test_get_children(self, tree, item1, item2, item3):
        tree.add_item(item1)
        tree.add_item(item2, parent_id="item1")
        tree.add_item(item3, parent_id="item1")

        root_children = tree.get_children(tree.root_id)
        assert len(root_children) == 1
        assert root_children[0].id == "item1"

        item1_children = tree.get_children("item1")
        assert len(item1_children) == 2
        child_ids = {child.id for child in item1_children}
        assert child_ids == {"item2", "item3"}

        assert tree.get_children("non_existent_parent") == []
        assert tree.get_children(None) == root_children

    def test_traverse(self, tree, item1, item2, item3):
        tree.add_item(item1)
        tree.add_item(item2, parent_id="item1")
        tree.add_item(item3)

        visited_items = []
        def visitor(item):
            visited_items.append(item.id)
        
        tree.traverse(visitor)
        expected_ids = {tree.root_id, "item1", "item2", "item3"}
        assert set(visited_items) == expected_ids

        visited_items.clear()
        tree.traverse(visitor, node_id="item1")
        assert set(visited_items) == {"item1", "item2"}
        
        empty_tree = MTTree("empty", "Empty", event_manager=Mock())
        empty_tree.traverse(visitor)
        assert visited_items == []

    def test_reset_tree(self, tree, item1, mock_event_manager):
        tree.add_item(item1)
        assert tree.get_item("item1") is not None
        
        mock_event_manager.reset_mock()
        tree.reset_tree()
        
        assert tree.get_item("item1") is None
        assert tree.items == {tree.root_id: tree.get_item(tree.root_id)}
        assert tree.get_item(tree.root_id).get_property("children_ids") == []

        expected_reset_data = {}
        expected_crud_data = {"tree_data": tree.to_dict()}
        calls = [
            call(MTTreeEvent.TREE_RESET, expected_reset_data),
            call(MTTreeEvent.TREE_CRUD, expected_crud_data)
        ]
        mock_event_manager.notify.assert_has_calls(calls, any_order=False)

    def test_to_dict_and_from_dict(self, tree, item1, item2, mock_event_manager):
        tree.add_item(item1)
        tree.add_item(item2, parent_id="item1")

        tree_dict = tree.to_dict()

        new_tree = MTTree.from_dict(tree_dict, event_manager=mock_event_manager)

        assert new_tree.id == tree.id
        assert new_tree.name == tree.name
        assert new_tree.root_id == tree.root_id
        assert len(new_tree.items) == len(tree.items)
        assert new_tree.get_item("item1").get_property("name") == item1.get_property("name")
        assert new_tree.get_item("item2").get_property("name") == item2.get_property("name")

    def test_clone(self, tree, item1, item2, mock_event_manager):
        original_event_manager = tree._event_manager
        tree.add_item(item1)
        tree.add_item(item2, parent_id="item1")

        cloned_tree = tree.clone()

        assert cloned_tree is not tree
        assert cloned_tree.id == tree.id
        assert cloned_tree.name == tree.name
        assert len(cloned_tree.items) == len(tree.items)
        
        cloned_item1 = cloned_tree.get_item("item1")
        original_item1 = tree.get_item("item1")
        assert cloned_item1 is not original_item1
        assert cloned_item1.get_property("name") == original_item1.get_property("name")
        
        assert cloned_tree.get_item("item1") is not tree.get_item("item1")
        
        assert cloned_tree._event_manager is original_event_manager

        tree.modify_item("item1", {"name": "Modified Original Item1"})
        assert cloned_item1.get_property("name") == "Item 1"

        cloned_tree.modify_item("item2", {"name": "Modified Cloned Item2"})
        assert tree.get_item("item2").get_property("name") == "Item 2"

    def test_is_descendant(self, tree, item1, item2, item3):
        tree.add_item(item1)
        tree.add_item(item2, parent_id="item1")
        tree.add_item(item3, parent_id="item2")

        assert tree._is_descendant(ancestor_id="item1", descendant_id="item2")
        assert tree._is_descendant(ancestor_id="item1", descendant_id="item3")
        assert tree._is_descendant(ancestor_id="item2", descendant_id="item3")
        
        assert not tree._is_descendant(ancestor_id="item2", descendant_id="item1")
        assert not tree._is_descendant(ancestor_id="item3", descendant_id="item1")
        assert not tree._is_descendant(ancestor_id="item1", descendant_id="item1")
        assert not tree._is_descendant(ancestor_id="item1", descendant_id="non_existent")
        assert not tree._is_descendant(ancestor_id="non_existent", descendant_id="item1")
        assert not tree._is_descendant(ancestor_id=tree.root_id, descendant_id="item1")

    def test_dummy_root_properties(self, tree):
        dummy_root = tree.get_item(tree.root_id)
        assert dummy_root is not None
        assert dummy_root.id == MTTree.DUMMY_ROOT_ID
        assert dummy_root.get_property("name") == "MTTree Dummy Root"
        assert dummy_root.get_property("node_type") == MTNodeType.DUMMY_ROOT
        assert dummy_root.get_property("parent_id") is None
        assert isinstance(dummy_root.get_property("children_ids"), list)

    def test_json_serialization_deserialization(self, tree, item1, item2, mock_event_manager):
        tree.add_item(item1)
        tree.add_item(item2, parent_id="item1")

        json_string = tree.to_json()
        assert isinstance(json_string, str)

        new_tree = MTTree.from_json(json_string, event_manager=mock_event_manager)
        assert new_tree.id == tree.id
        assert len(new_tree.items) == len(tree.items)
        assert new_tree.get_item("item1").get_property("name") == item1.get_property("name") 