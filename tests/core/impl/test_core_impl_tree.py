import pytest
from unittest.mock import Mock, call
import uuid # item_id 생성을 위해 추가

from src.core.impl.tree import MTTree
from src.core.interfaces.base_item_data import MTNodeType, MTItemDomainDTO, MTItemUIStateDTO, MTItemDTO # DTO 임포트
from src.core.interfaces.base_tree import IMTTree
from src.model.events.interfaces.base_tree_event_mgr import IMTTreeEventManager, MTTreeEvent
import src.core.exceptions as exc

def test_tree_create():
    mock_event_manager = Mock(spec=IMTTreeEventManager)
    tree:IMTTree = MTTree(tree_id="root_tree_id", name="Root Tree", event_manager=mock_event_manager)
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

    def test_add_item_to_root(self, tree, mock_event_manager):
        mock_event_manager.reset_mock()
        
        item1_id = "item1_ar"
        item1_domain = MTItemDomainDTO(name="Item 1", node_type=MTNodeType.INSTRUCTION, parent_id=tree.root_id)
        item1_ui = MTItemUIStateDTO()
        item1_dto = MTItemDTO(item_id=item1_id, domain_data=item1_domain, ui_state_data=item1_ui)
        
        returned_id = tree.add_item(item_dto=item1_dto)
        assert returned_id == item1_id
        
        added_item_obj = tree.get_item(item1_id)
        assert added_item_obj is not None
        assert added_item_obj.id == item1_id
        assert added_item_obj.data.parent_id == tree.root_id 
        
        root_item_obj = tree.get_item(tree.root_id)
        assert root_item_obj is not None
        assert item1_id in root_item_obj.data.children_ids
        
        expected_item_added_data = {"item_id": item1_id, "parent_id": tree.root_id}
        expected_tree_crud_data = {"tree_data": tree.to_dict()} 
        
        calls = [
            call(MTTreeEvent.ITEM_ADDED, expected_item_added_data),
            call(MTTreeEvent.TREE_CRUD, expected_tree_crud_data)
        ]
        mock_event_manager.notify.assert_has_calls(calls, any_order=False)

    def test_add_item_to_parent(self, tree, mock_event_manager):
        mock_event_manager.reset_mock()

        parent_item_id = "parent1_ap"
        parent_domain = MTItemDomainDTO(name="Parent 1", node_type=MTNodeType.GROUP, parent_id=tree.root_id)
        parent_ui = MTItemUIStateDTO()
        parent_dto = MTItemDTO(item_id=parent_item_id, domain_data=parent_domain, ui_state_data=parent_ui)
        tree.add_item(item_dto=parent_dto)
        mock_event_manager.reset_mock() 

        child_item_id = "child1_ap"
        child_domain = MTItemDomainDTO(name="Child 1", node_type=MTNodeType.INSTRUCTION, parent_id=parent_item_id)
        child_ui = MTItemUIStateDTO()
        child_dto = MTItemDTO(item_id=child_item_id, domain_data=child_domain, ui_state_data=child_ui)
        
        returned_id = tree.add_item(item_dto=child_dto)
        assert returned_id == child_item_id

        added_child_obj = tree.get_item(child_item_id)
        assert added_child_obj is not None
        assert added_child_obj.data.parent_id == parent_item_id
        
        parent_item_obj = tree.get_item(parent_item_id)
        assert parent_item_obj is not None
        assert child_item_id in parent_item_obj.data.children_ids

        expected_item_added_data = {"item_id": child_item_id, "parent_id": parent_item_id}
        expected_tree_crud_data = {"tree_data": tree.to_dict()}
        calls = [
            call(MTTreeEvent.ITEM_ADDED, expected_item_added_data),
            call(MTTreeEvent.TREE_CRUD, expected_tree_crud_data)
        ]
        mock_event_manager.notify.assert_has_calls(calls, any_order=False)

    def test_add_item_with_index(self, tree, mock_event_manager):
        mock_event_manager.reset_mock()
        item1_id = "item1_idx"
        item1_domain = MTItemDomainDTO(name="Item1_idx", node_type=MTNodeType.INSTRUCTION, parent_id=tree.root_id)
        item1_dto = MTItemDTO(item_id=item1_id, domain_data=item1_domain, ui_state_data=MTItemUIStateDTO())
        
        item2_id = "item2_idx"
        item2_domain = MTItemDomainDTO(name="Item2_idx", node_type=MTNodeType.INSTRUCTION, parent_id=tree.root_id)
        item2_dto = MTItemDTO(item_id=item2_id, domain_data=item2_domain, ui_state_data=MTItemUIStateDTO())

        item3_id = "item3_idx"
        item3_domain = MTItemDomainDTO(name="Item3_idx", node_type=MTNodeType.INSTRUCTION, parent_id=tree.root_id)
        item3_dto = MTItemDTO(item_id=item3_id, domain_data=item3_domain, ui_state_data=MTItemUIStateDTO())

        tree.add_item(item_dto=item1_dto) 
        tree.add_item(item_dto=item2_dto) 
        
        mock_event_manager.reset_mock()
        tree.add_item(item_dto=item3_dto, index=1)
        
        root_children_items = tree.get_children(tree.root_id)
        assert len(root_children_items) == 3
        assert root_children_items[0].id == item1_id
        assert root_children_items[1].id == item3_id
        assert root_children_items[2].id == item2_id

        item3_obj = tree.get_item(item3_id)
        assert item3_obj is not None
        assert item3_obj.data.parent_id == tree.root_id
        
        expected_item_added_data = {"item_id": item3_id, "parent_id": tree.root_id}
        mock_event_manager.notify.assert_any_call(MTTreeEvent.ITEM_ADDED, expected_item_added_data)

    def test_add_item_non_existent_parent(self, tree):
        item_domain = MTItemDomainDTO(name="Item NP", node_type=MTNodeType.INSTRUCTION, parent_id="non_existent_parent")
        item_ui = MTItemUIStateDTO()
        item_dto_np = MTItemDTO(item_id="item_np", domain_data=item_domain, ui_state_data=item_ui)
        with pytest.raises(exc.MTItemNotFoundError):
            tree.add_item(item_dto=item_dto_np)

    def test_remove_item(self, tree, mock_event_manager):
        parent_id_ri = "parent_ri"
        child_id_ri = "child_ri"
        parent_domain = MTItemDomainDTO(name="ParentRI", node_type=MTNodeType.GROUP, parent_id=tree.root_id)
        parent_dto = MTItemDTO(item_id=parent_id_ri, domain_data=parent_domain, ui_state_data=MTItemUIStateDTO())
        tree.add_item(item_dto=parent_dto)
        
        child_domain = MTItemDomainDTO(name="ChildRI", node_type=MTNodeType.INSTRUCTION, parent_id=parent_id_ri)
        child_dto = MTItemDTO(item_id=child_id_ri, domain_data=child_domain, ui_state_data=MTItemUIStateDTO())
        tree.add_item(item_dto=child_dto)
        
        parent_item_obj_before_remove = tree.get_item(parent_id_ri)
        assert parent_item_obj_before_remove is not None

        mock_event_manager.reset_mock()
        tree.remove_item(child_id_ri)
        assert tree.get_item(child_id_ri) is None
        parent_item_obj_after_remove = tree.get_item(parent_id_ri) 
        assert parent_item_obj_after_remove is not None
        assert child_id_ri not in parent_item_obj_after_remove.data.children_ids
        
        expected_item_removed_data = {"item_id": child_id_ri, "parent_id": parent_id_ri}
        mock_event_manager.notify.assert_any_call(MTTreeEvent.ITEM_REMOVED, expected_item_removed_data)

        mock_event_manager.reset_mock()
        tree.remove_item(parent_id_ri)
        assert tree.get_item(parent_id_ri) is None
        root_item_obj = tree.get_item(tree.root_id)
        assert root_item_obj is not None
        assert parent_id_ri not in root_item_obj.data.children_ids
        expected_item_removed_data_2 = {"item_id": parent_id_ri, "parent_id": tree.root_id}
        mock_event_manager.notify.assert_any_call(MTTreeEvent.ITEM_REMOVED, expected_item_removed_data_2)

    def test_remove_item_recursive(self, tree, mock_event_manager):
        item1_id = "item1_rr"
        item1_domain = MTItemDomainDTO(name="Item 1", node_type=MTNodeType.GROUP, parent_id=tree.root_id)
        item1_dto = MTItemDTO(item_id=item1_id, domain_data=item1_domain, ui_state_data=MTItemUIStateDTO())
        tree.add_item(item_dto=item1_dto)

        item2_id = "item2_rr"
        item2_domain = MTItemDomainDTO(name="Item 2", node_type=MTNodeType.GROUP, parent_id=item1_id)
        item2_dto = MTItemDTO(item_id=item2_id, domain_data=item2_domain, ui_state_data=MTItemUIStateDTO())
        tree.add_item(item_dto=item2_dto)

        item3_id = "item3_rr"
        item3_domain = MTItemDomainDTO(name="Item 3", node_type=MTNodeType.INSTRUCTION, parent_id=item2_id)
        item3_dto = MTItemDTO(item_id=item3_id, domain_data=item3_domain, ui_state_data=MTItemUIStateDTO())
        tree.add_item(item_dto=item3_dto)

        assert tree.get_item(item1_id) is not None
        assert tree.get_item(item2_id) is not None
        assert tree.get_item(item3_id) is not None
        
        mock_event_manager.reset_mock()
        tree.remove_item(item1_id)
        
        assert tree.get_item(item1_id) is None
        assert tree.get_item(item2_id) is None
        assert tree.get_item(item3_id) is None

        mock_event_manager.notify.assert_any_call(MTTreeEvent.ITEM_REMOVED, {"item_id": item1_id, "parent_id": tree.root_id})

    def test_remove_non_existent_item(self, tree):
        with pytest.raises(exc.MTItemNotFoundError):
            tree.remove_item("non_existent_item")

    def test_remove_dummy_root_item(self, tree):
        with pytest.raises(exc.MTTreeError, match="더미 루트 아이템은 삭제할 수 없습니다."):
            tree.remove_item(tree.root_id)

    def test_move_item_to_another_parent(self, tree, mock_event_manager):
        item1_id = "item1_mv"
        item1_domain = MTItemDomainDTO(name="Item 1", node_type=MTNodeType.GROUP, parent_id=tree.root_id)
        item1_dto = MTItemDTO(item_id=item1_id, domain_data=item1_domain, ui_state_data=MTItemUIStateDTO())
        tree.add_item(item_dto=item1_dto)

        item2_id = "item2_mv"
        item2_domain = MTItemDomainDTO(name="Item 2", node_type=MTNodeType.GROUP, parent_id=tree.root_id)
        item2_dto = MTItemDTO(item_id=item2_id, domain_data=item2_domain, ui_state_data=MTItemUIStateDTO())
        tree.add_item(item_dto=item2_dto)

        item3_id = "item3_mv"
        item3_domain = MTItemDomainDTO(name="Item 3", node_type=MTNodeType.INSTRUCTION, parent_id=item1_id)
        item3_dto = MTItemDTO(item_id=item3_id, domain_data=item3_domain, ui_state_data=MTItemUIStateDTO())
        tree.add_item(item_dto=item3_dto)
        
        mock_event_manager.reset_mock()
        tree.move_item(item3_id, new_parent_id=item2_id)
        
        item3_obj_after_move = tree.get_item(item3_id)
        assert item3_obj_after_move is not None
        assert item3_obj_after_move.data.parent_id == item2_id
        
        item1_obj_after_move = tree.get_item(item1_id)
        assert item1_obj_after_move is not None
        assert item3_id not in item1_obj_after_move.data.children_ids
        
        item2_obj_after_move = tree.get_item(item2_id)
        assert item2_obj_after_move is not None
        assert item3_id in item2_obj_after_move.data.children_ids
        
        expected_moved_data = {
            "item_id": item3_id, 
            "new_parent_id": item2_id, 
            "old_parent_id": item1_id,
        }
        mock_event_manager.notify.assert_any_call(MTTreeEvent.ITEM_MOVED, expected_moved_data)

    def test_move_item_to_root(self, tree, mock_event_manager):
        item1_id = "item1_mr"
        item1_domain = MTItemDomainDTO(name="Item 1", node_type=MTNodeType.GROUP, parent_id=tree.root_id)
        item1_dto = MTItemDTO(item_id=item1_id, domain_data=item1_domain, ui_state_data=MTItemUIStateDTO())
        tree.add_item(item_dto=item1_dto)

        item2_id = "item2_mr"
        item2_domain = MTItemDomainDTO(name="Item 2", node_type=MTNodeType.INSTRUCTION, parent_id=item1_id)
        item2_dto = MTItemDTO(item_id=item2_id, domain_data=item2_domain, ui_state_data=MTItemUIStateDTO())
        tree.add_item(item_dto=item2_dto)

        mock_event_manager.reset_mock()
        tree.move_item(item2_id, new_parent_id=tree.root_id)
        
        item2_obj_after_move = tree.get_item(item2_id)
        assert item2_obj_after_move is not None
        assert item2_obj_after_move.data.parent_id == tree.root_id
        
        item1_obj_after_move = tree.get_item(item1_id)
        assert item1_obj_after_move is not None
        assert item2_id not in item1_obj_after_move.data.children_ids
        
        root_item_obj = tree.get_item(tree.root_id)
        assert root_item_obj is not None
        assert item2_id in root_item_obj.data.children_ids
        
        expected_moved_data = {
            "item_id": item2_id,
            "new_parent_id": tree.root_id,
            "old_parent_id": item1_id,
        }
        mock_event_manager.notify.assert_any_call(MTTreeEvent.ITEM_MOVED, expected_moved_data)

    def test_move_item_change_order_same_parent(self, tree, mock_event_manager):
        item1_id = "item1_so"
        item1_domain = MTItemDomainDTO(name="Item 1", parent_id=tree.root_id)
        item1_dto = MTItemDTO(item_id=item1_id, domain_data=item1_domain, ui_state_data=MTItemUIStateDTO())
        tree.add_item(item_dto=item1_dto)

        item2_id = "item2_so"
        item2_domain = MTItemDomainDTO(name="Item 2", parent_id=tree.root_id)
        item2_dto = MTItemDTO(item_id=item2_id, domain_data=item2_domain, ui_state_data=MTItemUIStateDTO())
        tree.add_item(item_dto=item2_dto)

        item3_id = "item3_so"
        item3_domain = MTItemDomainDTO(name="Item 3", parent_id=tree.root_id)
        item3_dto = MTItemDTO(item_id=item3_id, domain_data=item3_domain, ui_state_data=MTItemUIStateDTO())
        tree.add_item(item_dto=item3_dto)

        mock_event_manager.reset_mock()
        tree.move_item(item3_id, new_parent_id=tree.root_id, new_index=0)
        
        root_children_items = tree.get_children(tree.root_id)
        assert len(root_children_items) == 3
        assert root_children_items[0].id == item3_id
        assert root_children_items[1].id == item1_id
        assert root_children_items[2].id == item2_id
        
        expected_moved_data = {
            "item_id": item3_id,
            "new_parent_id": tree.root_id,
            "old_parent_id": tree.root_id,
        }
        mock_event_manager.notify.assert_any_call(MTTreeEvent.ITEM_MOVED, expected_moved_data)

    def test_move_item_to_itself_or_descendant(self, tree):
        item1_id = "item1_cyc"
        item1_domain = MTItemDomainDTO(name="Item 1", node_type=MTNodeType.GROUP, parent_id=tree.root_id)
        item1_dto = MTItemDTO(item_id=item1_id, domain_data=item1_domain, ui_state_data=MTItemUIStateDTO())
        tree.add_item(item_dto=item1_dto)

        item2_id = "item2_cyc"
        item2_domain = MTItemDomainDTO(name="Item 2", node_type=MTNodeType.INSTRUCTION, parent_id=item1_id)
        item2_dto = MTItemDTO(item_id=item2_id, domain_data=item2_domain, ui_state_data=MTItemUIStateDTO())
        tree.add_item(item_dto=item2_dto)
        
        with pytest.raises(exc.MTTreeError, match="순환 참조 발생"):
            tree.move_item(item1_id, new_parent_id=item2_id)
        with pytest.raises(exc.MTTreeError, match="순환 참조 발생"):
             tree.move_item(item1_id, new_parent_id=item1_id)

    def test_move_item_non_existent_item_or_parent(self, tree):
        item1_id = "item1_ne"
        item1_domain = MTItemDomainDTO(name="Item 1", parent_id=tree.root_id)
        item1_dto = MTItemDTO(item_id=item1_id, domain_data=item1_domain, ui_state_data=MTItemUIStateDTO())
        tree.add_item(item_dto=item1_dto)

        with pytest.raises(exc.MTItemNotFoundError):
            tree.move_item("non_existent_item", new_parent_id=item1_id)
        with pytest.raises(exc.MTItemNotFoundError):
            tree.move_item(item1_id, new_parent_id="non_existent_parent")

    def test_move_dummy_root_item(self, tree):
        with pytest.raises(exc.MTTreeError, match="더미 루트 아이템은 이동할 수 없습니다."):
            tree.move_item(tree.root_id, new_parent_id=None)

    def test_modify_item(self, tree, mock_event_manager):
        mock_event_manager.reset_mock()
        item_id_mod = "item_to_modify"
        original_domain = MTItemDomainDTO(name="Original Name", node_type=MTNodeType.INSTRUCTION, parent_id=tree.root_id)
        original_ui = MTItemUIStateDTO(is_selected=False)
        original_dto = MTItemDTO(item_id=item_id_mod, domain_data=original_domain, ui_state_data=original_ui)
        tree.add_item(item_dto=original_dto)
        mock_event_manager.reset_mock()

        modified_domain = MTItemDomainDTO(name="Modified Name", node_type=MTNodeType.INSTRUCTION, parent_id=tree.root_id, action_data=Mock()) 
        modified_ui = MTItemUIStateDTO(is_selected=True, is_expanded=True)
        modified_item_dto = MTItemDTO(item_id=item_id_mod, domain_data=modified_domain, ui_state_data=modified_ui)
        
        success = tree.modify_item(item_id_mod, item_dto=modified_item_dto)
        assert success is True

        modified_item_obj = tree.get_item(item_id_mod)
        assert modified_item_obj is not None
        assert modified_item_obj.data.name == "Modified Name"
        assert modified_item_obj.ui_state.is_selected is True
        assert modified_item_obj.ui_state.is_expanded is True
        assert modified_item_obj.data.action_data is not None
        
        expected_changes_dict = modified_item_dto.to_dict()
        expected_modified_data = {"item_id": item_id_mod, "changes": expected_changes_dict}
        expected_tree_crud_data = {"tree_data": tree.to_dict()}
        calls = [
            call(MTTreeEvent.ITEM_MODIFIED, expected_modified_data),
            call(MTTreeEvent.TREE_CRUD, expected_tree_crud_data)
        ]
        mock_event_manager.notify.assert_has_calls(calls, any_order=False)

    def test_modify_non_existent_item(self, tree):
        domain = MTItemDomainDTO(name="test")
        ui_state = MTItemUIStateDTO()
        dto = MTItemDTO(item_id="non_existent_item", domain_data=domain, ui_state_data=ui_state)
        with pytest.raises(exc.MTItemNotFoundError):
            tree.modify_item("non_existent_item", item_dto=dto)

    def test_get_item(self, tree):
        item_id_gi = "item_gi"
        assert tree.get_item(item_id_gi) is None
        
        domain = MTItemDomainDTO(name="Item GI", parent_id=tree.root_id)
        dto = MTItemDTO(item_id=item_id_gi, domain_data=domain, ui_state_data=MTItemUIStateDTO())
        tree.add_item(item_dto=dto)
        
        retrieved_item = tree.get_item(item_id_gi)
        assert retrieved_item is not None
        assert retrieved_item.id == item_id_gi

    def test_get_children_and_dtos(self, tree):
        item1_id = "item1_gcd"
        item1_domain = MTItemDomainDTO(name="Item 1", node_type=MTNodeType.GROUP, parent_id=tree.root_id)
        item1_dto = MTItemDTO(item_id=item1_id, domain_data=item1_domain, ui_state_data=MTItemUIStateDTO())
        tree.add_item(item_dto=item1_dto)

        item2_id = "item2_gcd"
        item2_domain = MTItemDomainDTO(name="Item 2", node_type=MTNodeType.INSTRUCTION, parent_id=item1_id)
        item2_dto = MTItemDTO(item_id=item2_id, domain_data=item2_domain, ui_state_data=MTItemUIStateDTO())
        tree.add_item(item_dto=item2_dto)

        item3_id = "item3_gcd"
        item3_domain = MTItemDomainDTO(name="Item 3", node_type=MTNodeType.INSTRUCTION, parent_id=item1_id)
        item3_dto = MTItemDTO(item_id=item3_id, domain_data=item3_domain, ui_state_data=MTItemUIStateDTO())
        tree.add_item(item_dto=item3_dto)

        root_children_items = tree.get_children(tree.root_id)
        assert len(root_children_items) == 1
        assert root_children_items[0].id == item1_id

        item1_children_items = tree.get_children(item1_id)
        assert len(item1_children_items) == 2
        child_item_ids = {child.id for child in item1_children_items}
        assert child_item_ids == {item2_id, item3_id}

        item1_children_dtos = tree.get_children_dtos(item1_id)
        assert len(item1_children_dtos) == 2
        child_dto_item_ids = {dto.item_id for dto in item1_children_dtos}
        assert child_dto_item_ids == {item2_id, item3_id}
        assert isinstance(item1_children_dtos[0], MTItemDTO)

        assert tree.get_children("non_existent_parent") == []
        assert tree.get_children_dtos("non_existent_parent") == []
        assert tree.get_children(None) == root_children_items

    def test_traverse(self, tree):
        item1_id = "item1_tr"
        item1_domain = MTItemDomainDTO(name="Item 1", node_type=MTNodeType.GROUP, parent_id=tree.root_id)
        item1_dto = MTItemDTO(item_id=item1_id, domain_data=item1_domain, ui_state_data=MTItemUIStateDTO())
        tree.add_item(item_dto=item1_dto)

        item2_id = "item2_tr"
        item2_domain = MTItemDomainDTO(name="Item 2", node_type=MTNodeType.INSTRUCTION, parent_id=item1_id)
        item2_dto = MTItemDTO(item_id=item2_id, domain_data=item2_domain, ui_state_data=MTItemUIStateDTO())
        tree.add_item(item_dto=item2_dto)

        item3_id = "item3_tr"
        item3_domain = MTItemDomainDTO(name="Item 3", parent_id=tree.root_id)
        item3_dto = MTItemDTO(item_id=item3_id, domain_data=item3_domain, ui_state_data=MTItemUIStateDTO())
        tree.add_item(item_dto=item3_dto)

        visited_item_ids = []
        def visitor(item_obj):
            visited_item_ids.append(item_obj.id)
        
        tree.traverse(visitor)
        expected_ids_set = {tree.root_id, item1_id, item2_id, item3_id}
        assert set(visited_item_ids) == expected_ids_set

        visited_item_ids.clear()
        tree.traverse(visitor, node_id=item1_id)
        assert set(visited_item_ids) == {item1_id, item2_id}
        
        empty_tree = MTTree("empty", "Empty", event_manager=Mock())
        visited_item_ids.clear()
        empty_tree.traverse(visitor)
        assert visited_item_ids == []

    def test_reset_tree(self, tree, mock_event_manager):
        item1_id = "item1_rt"
        item1_domain = MTItemDomainDTO(name="Item 1", parent_id=tree.root_id)
        item1_dto = MTItemDTO(item_id=item1_id, domain_data=item1_domain, ui_state_data=MTItemUIStateDTO())
        tree.add_item(item_dto=item1_dto)
        assert tree.get_item(item1_id) is not None
        
        mock_event_manager.reset_mock()
        tree.reset_tree()
        
        assert tree.get_item(item1_id) is None
        dummy_root_item = tree.get_item(tree.root_id)
        assert dummy_root_item is not None
        assert tree.items == {tree.root_id: dummy_root_item} 
        assert dummy_root_item.data.children_ids == []

        expected_reset_data = {}
        expected_crud_data = {"tree_data": tree.to_dict()}
        calls = [
            call(MTTreeEvent.TREE_RESET, expected_reset_data),
            call(MTTreeEvent.TREE_CRUD, expected_crud_data)
        ]
        mock_event_manager.notify.assert_has_calls(calls, any_order=False)

    def test_to_dict_and_from_dict(self, tree, mock_event_manager):
        item1_id = "item1_sfd"
        item1_domain = MTItemDomainDTO(name="Item 1 Serial", node_type=MTNodeType.GROUP, parent_id=tree.root_id)
        item1_dto = MTItemDTO(item_id=item1_id, domain_data=item1_domain, ui_state_data=MTItemUIStateDTO())
        tree.add_item(item_dto=item1_dto)

        item2_id = "item2_sfd"
        item2_domain = MTItemDomainDTO(name="Item 2 Serial", node_type=MTNodeType.INSTRUCTION, parent_id=item1_id)
        item2_dto = MTItemDTO(item_id=item2_id, domain_data=item2_domain, ui_state_data=MTItemUIStateDTO())
        tree.add_item(item_dto=item2_dto)
        
        tree_dict_data = tree.to_dict()
        new_tree = MTTree.from_dict(tree_dict_data, event_manager=mock_event_manager)
        
        assert new_tree.id == tree.id
        assert new_tree.name == tree.name
        assert new_tree.root_id == tree.root_id
        assert len(new_tree.items) == len(tree.items)
        
        retrieved_item1_obj_new = new_tree.get_item(item1_id)
        assert retrieved_item1_obj_new is not None
        assert retrieved_item1_obj_new.data.name == item1_domain.name
        
        retrieved_item2_obj_new = new_tree.get_item(item2_id)
        assert retrieved_item2_obj_new is not None
        assert retrieved_item2_obj_new.data.name == item2_domain.name

    def test_json_serialization_deserialization(self, tree, mock_event_manager):
        item1_id = "item1_json"
        item1_domain = MTItemDomainDTO(name="Item 1 JSON", node_type=MTNodeType.GROUP, parent_id=tree.root_id)
        item1_dto = MTItemDTO(item_id=item1_id, domain_data=item1_domain, ui_state_data=MTItemUIStateDTO())
        tree.add_item(item_dto=item1_dto)

        json_string = tree.tree_to_json()
        assert isinstance(json_string, str)
        
        new_tree = MTTree.json_to_tree(json_string, event_manager=mock_event_manager)
        assert new_tree.id == tree.id
        assert len(new_tree.items) == len(tree.items)
        
        retrieved_item1_obj_new = new_tree.get_item(item1_id)
        assert retrieved_item1_obj_new is not None
        assert retrieved_item1_obj_new.data.name == item1_domain.name

    def test_clone(self, tree, mock_event_manager):
        item1_id = "item1_clone_tc"
        item1_domain = MTItemDomainDTO(name="Item 1 Original", parent_id=tree.root_id)
        item1_dto_orig = MTItemDTO(item_id=item1_id, domain_data=item1_domain, ui_state_data=MTItemUIStateDTO())
        tree.add_item(item_dto=item1_dto_orig)

        item2_id = "item2_clone_tc"
        item2_domain = MTItemDomainDTO(name="Item 2 Original", parent_id=item1_id)
        item2_dto_orig = MTItemDTO(item_id=item2_id, domain_data=item2_domain, ui_state_data=MTItemUIStateDTO())
        tree.add_item(item_dto=item2_dto_orig)

        cloned_tree = tree.clone()

        assert cloned_tree is not tree
        assert cloned_tree.id == tree.id
        assert cloned_tree.name == tree.name
        assert len(cloned_tree.items) == len(tree.items)
        
        cloned_item1_obj = cloned_tree.get_item(item1_id)
        original_item1_obj = tree.get_item(item1_id)
        assert cloned_item1_obj is not original_item1_obj
        assert cloned_item1_obj is not None
        assert original_item1_obj is not None
        assert cloned_item1_obj.data.name == original_item1_obj.data.name
        
        assert cloned_tree._event_manager is None

        modified_domain_orig = MTItemDomainDTO(name="Modified Original Item1", parent_id=tree.root_id)
        modified_dto_for_orig_tree = MTItemDTO(item_id=item1_id, domain_data=modified_domain_orig, ui_state_data=MTItemUIStateDTO())
        tree.modify_item(item1_id, item_dto=modified_dto_for_orig_tree)
        assert cloned_item1_obj.data.name == "Item 1 Original"

        modified_domain_cloned = MTItemDomainDTO(name="Modified Cloned Item2", parent_id=item1_id)
        modified_dto_for_cloned_tree = MTItemDTO(item_id=item2_id, domain_data=modified_domain_cloned, ui_state_data=MTItemUIStateDTO())
        cloned_tree.modify_item(item2_id, item_dto=modified_dto_for_cloned_tree)
        
        original_item2_obj = tree.get_item(item2_id)
        assert original_item2_obj is not None
        assert original_item2_obj.data.name == "Item 2 Original"

    def test_is_descendant(self, tree):
        item1_id = "item1_desc"
        item1_d = MTItemDomainDTO(name="I1", parent_id=tree.root_id, node_type=MTNodeType.GROUP)
        tree.add_item(item_dto=MTItemDTO(item_id=item1_id, domain_data=item1_d, ui_state_data=MTItemUIStateDTO()))

        item2_id = "item2_desc"
        item2_d = MTItemDomainDTO(name="I2", parent_id=item1_id, node_type=MTNodeType.INSTRUCTION)
        tree.add_item(item_dto=MTItemDTO(item_id=item2_id, domain_data=item2_d, ui_state_data=MTItemUIStateDTO()))

        item3_id = "item3_desc"
        item3_d = MTItemDomainDTO(name="I3", parent_id=item2_id, node_type=MTNodeType.INSTRUCTION)
        tree.add_item(item_dto=MTItemDTO(item_id=item3_id, domain_data=item3_d, ui_state_data=MTItemUIStateDTO()))

        assert tree._is_descendant(ancestor_id=item1_id, descendant_id=item2_id)
        assert tree._is_descendant(ancestor_id=item1_id, descendant_id=item3_id)
        assert tree._is_descendant(ancestor_id=item2_id, descendant_id=item3_id)
        
        assert not tree._is_descendant(ancestor_id=item2_id, descendant_id=item1_id)
        assert not tree._is_descendant(ancestor_id=item3_id, descendant_id=item1_id)
        assert not tree._is_descendant(ancestor_id=item1_id, descendant_id=item1_id)
        assert not tree._is_descendant(ancestor_id=item1_id, descendant_id="non_existent")
        assert not tree._is_descendant(ancestor_id="non_existent", descendant_id=item1_id)
        assert tree._is_descendant(ancestor_id=tree.root_id, descendant_id=item1_id)

    def test_dummy_root_properties(self, tree):
        dummy_root = tree.get_item(tree.root_id)
        assert dummy_root is not None
        assert dummy_root.id == MTTree.DUMMY_ROOT_ID
        assert dummy_root.data.name == "Dummy Root"
        assert dummy_root.data.node_type == MTNodeType.GROUP
        assert dummy_root.data.parent_id is None
        assert isinstance(dummy_root.data.children_ids, list)
        assert dummy_root.data.children_ids == [] 