import pytest
from unittest.mock import Mock, call, patch

from src.viewmodel.impl.tree_viewmodel import MTTreeViewModel
from src.core.interfaces.base_tree import IMTTree
from src.core.impl.tree import MTTree # 실제 MTTree도 필요할 수 있음
from src.core.impl.item import MTTreeItem
from src.core.interfaces.base_item_data import MTNodeType
from src.model.state.interfaces.base_tree_state_mgr import IMTTreeStateManager
from src.model.events.interfaces.base_tree_event_mgr import IMTTreeEventManager, MTTreeEvent
from PyQt6.QtCore import QObject # ViewModel이 QObject를 상속하므로 필요


# ViewModel의 생성자에 많은 의존성이 있으므로, Mock 객체를 준비
@pytest.fixture
def mock_tree():
    # 실제 MTTree의 DUMMY_ROOT_ID를 사용하거나, Mock에 해당 속성 설정
    tree = Mock(spec=IMTTree)
    tree.DUMMY_ROOT_ID = "__MTTREE_DUMMY_ROOT__" # MTTree.DUMMY_ROOT_ID 와 일치시켜야 함
    return tree

@pytest.fixture
def mock_state_manager():
    return Mock(spec=IMTTreeStateManager)

@pytest.fixture
def mock_event_manager():
    return Mock(spec=IMTTreeEventManager)

@pytest.fixture
def mock_ui_view():
    # TreeView 클래스의 인터페이스를 모킹 (on_viewmodel_signal, on_tree_undoredo_signal 등)
    view = Mock()
    view.on_viewmodel_signal = Mock()
    view.on_tree_undoredo_signal = Mock()
    return view

@pytest.fixture
@patch('src.viewmodel.impl.tree_viewmodel.MTTreeViewModelCore')
@patch('src.viewmodel.impl.tree_viewmodel.MTTreeViewModelModel')
@patch('src.viewmodel.impl.tree_viewmodel.MTTreeViewModelView')
def view_model(MockViewModelView, MockViewModelModel, MockViewModelCore, 
               mock_tree, mock_state_manager, mock_event_manager, mock_ui_view):
    
    # Core, Model, View 모듈의 Mock 인스턴스 생성
    mock_core_instance = MockViewModelCore.return_value
    mock_model_instance = MockViewModelModel.return_value
    # mock_view_instance = MockViewModelView.return_value # 사용되지 않으므로 주석 처리

    # MTTreeViewModel 생성 시 _state_mgr는 _model을 통해 접근하므로, _model에 설정
    # view_model 생성자에서 state_manager를 직접 받으므로, mock_model_instance에 설정할 필요 없음
    # mock_model_instance._state_mgr = mock_state_manager 
    
    # MTTreeViewModel 인스턴스 생성
    vm = MTTreeViewModel(tree=mock_tree, 
                         state_manager=mock_state_manager, # 생성자에 직접 전달
                         event_manager=mock_event_manager,
                         parent=None) # QObject 부모로 None 전달
    vm.set_view(mock_ui_view)
    
    # ViewModel 내부의 _core, _model, _view는 생성자에서 이미 patch된 클래스로부터 생성된 mock 인스턴스임
    # 따라서 여기서 다시 할당할 필요 없음
    return vm


class TestMTTreeViewModel:

    def test_initialization(self, view_model, mock_event_manager, mock_state_manager, 
                            MockViewModelCore, MockViewModelModel, MockViewModelView):
        """Test ViewModel initialization and subscription to events."""
        assert view_model._tree is not None
        # 생성자에서 MTTreeViewModelCore 등이 직접 인스턴스화되므로, 타입 체크가 정확함
        assert isinstance(view_model._core, MockViewModelCore) 
        assert isinstance(view_model._model, MockViewModelModel)
        assert isinstance(view_model._view, MockViewModelView)
        assert view_model._event_manager == mock_event_manager
        # ViewModel은 state_manager를 직접 들고 있지 않고, _model을 통해 접근함 (수정: 생성자에서 직접 받음)
        assert view_model._model._state_mgr == mock_state_manager

        if mock_event_manager:
            expected_event_subs = [
                call(MTTreeEvent.ITEM_ADDED, view_model.on_tree_mod_event),
                call(MTTreeEvent.ITEM_REMOVED, view_model.on_tree_mod_event),
                call(MTTreeEvent.ITEM_MOVED, view_model.on_tree_mod_event),
                call(MTTreeEvent.ITEM_MODIFIED, view_model.on_tree_mod_event),
                call(MTTreeEvent.TREE_RESET, view_model.on_tree_mod_event),
                call(MTTreeEvent.TREE_CRUD, view_model.on_tree_crud_event)
            ]
            mock_event_manager.subscribe.assert_has_calls(expected_event_subs, any_order=True)
            # assert mock_event_manager.subscribe.call_count >= len(expected_event_subs) # 정확한 호출 횟수 확인

        if mock_state_manager:
            expected_state_subs = [
                call(MTTreeEvent.TREE_UNDO, view_model.on_tree_undoredo_event),
                call(MTTreeEvent.TREE_REDO, view_model.on_tree_undoredo_event)
            ]
            mock_state_manager.subscribe.assert_has_calls(expected_state_subs, any_order=True)
            # assert mock_state_manager.subscribe.call_count == len(expected_state_subs)


    def test_set_view(self, view_model, mock_ui_view):
        """Test the set_view method."""
        assert view_model._ui_view == mock_ui_view
        
        new_mock_view = Mock()
        view_model.set_view(new_mock_view)
        assert view_model._ui_view == new_mock_view

    def test_on_tree_crud_event_saves_state(self, view_model, mock_state_manager):
        """Test that TREE_CRUD event triggers saving state via StateManager."""
        tree_data_snapshot = {"id": "tree1", "items": {}}
        event_data = {"tree_data": tree_data_snapshot}
        
        if not (hasattr(view_model._model, '_state_mgr') and view_model._model._state_mgr):
            pytest.skip("StateManager not available on model for this test.")
            return

        view_model.on_tree_crud_event(MTTreeEvent.TREE_CRUD, event_data)
        view_model._model._state_mgr.new_undo.assert_called_once_with(tree_data_snapshot)
            
    def test_on_tree_mod_event_emits_item_modified_signal(self, qtbot, view_model):
        """Test that ITEM_MODIFIED tree event emits the item_modified Qt signal."""
        event_data = {"item_id": "item1", "changes": {"name": "new_name"}}
        
        with qtbot.waitSignal(view_model.item_modified, timeout=100) as blocker:
            view_model.on_tree_mod_event(MTTreeEvent.ITEM_MODIFIED, event_data)
        
        assert blocker.signal_triggered
        assert blocker.args == [event_data]

    def test_on_tree_mod_event_notifies_ui_view(self, view_model, mock_ui_view):
        """Test that tree modification events notify the UI view."""
        added_data = {"item_id": "added1", "parent_id": "root"}
        removed_data = {"item_id": "removed1"}
        moved_data = {"item_id": "moved1", "new_parent_id": "p1", "old_parent_id": "p0"}
        reset_data = {}
        modified_data = {"item_id": "modified1", "changes": {}}

        view_model.on_tree_mod_event(MTTreeEvent.ITEM_ADDED, added_data)
        mock_ui_view.on_viewmodel_signal.assert_called_with('item_added', added_data)
        
        mock_ui_view.reset_mock() # 각 이벤트 후 mock 리셋
        view_model.on_tree_mod_event(MTTreeEvent.ITEM_REMOVED, removed_data)
        mock_ui_view.on_viewmodel_signal.assert_called_with('item_removed', removed_data)

        mock_ui_view.reset_mock()
        view_model.on_tree_mod_event(MTTreeEvent.ITEM_MOVED, moved_data)
        mock_ui_view.on_viewmodel_signal.assert_called_with('item_moved', moved_data)

        mock_ui_view.reset_mock()
        view_model.on_tree_mod_event(MTTreeEvent.TREE_RESET, reset_data)
        mock_ui_view.on_viewmodel_signal.assert_called_with('tree_reset', reset_data)
        
        mock_ui_view.reset_mock()
        view_model.on_tree_mod_event(MTTreeEvent.ITEM_MODIFIED, modified_data)
        # ITEM_MODIFIED는 시그널 발생과 함께 on_viewmodel_signal도 호출
        mock_ui_view.on_viewmodel_signal.assert_called_with('item_modified', modified_data)


    def test_on_tree_undoredo_event_restores_tree_and_notifies_view(self, view_model, mock_ui_view):
        """Test that Undo/Redo events restore tree state via Core and notify the UI view."""
        snapshot_data = {"id": "tree_snapshot", "items": {"item1": {"name": "Restored"}}}
        
        view_model.on_tree_undoredo_event(MTTreeEvent.TREE_UNDO, snapshot_data)
        mock_ui_view.on_tree_undoredo_signal.assert_called_with(MTTreeEvent.TREE_UNDO, snapshot_data)
        view_model._core.restore_tree_from_snapshot.assert_called_with(snapshot_data)
        
        mock_ui_view.reset_mock()
        view_model._core.reset_mock()

        view_model.on_tree_undoredo_event(MTTreeEvent.TREE_REDO, snapshot_data)
        mock_ui_view.on_tree_undoredo_signal.assert_called_with(MTTreeEvent.TREE_REDO, snapshot_data)
        view_model._core.restore_tree_from_snapshot.assert_called_with(snapshot_data)

    def test_get_node_type_delegates_to_core(self, view_model):
        item_id = "item_x"
        expected_type = MTNodeType.GROUP
        view_model._core.get_item_node_type.return_value = expected_type
        
        actual_type = view_model.get_node_type(item_id)
        
        view_model._core.get_item_node_type.assert_called_once_with(item_id)
        assert actual_type == expected_type

    def test_add_item_logic_no_selection(self, view_model, mock_tree):
        item_name = "New Root Item"
        item_type = MTNodeType.INSTRUCTION
        new_item_id = "new_item_123"
        
        # ViewModel의 get_dummy_root_id는 self._core.get_dummy_root_id()를 호출함.
        # view_model._core는 MockViewModelCore의 인스턴스이므로, 이 mock에 설정.
        view_model._core.get_dummy_root_id.return_value = mock_tree.DUMMY_ROOT_ID
        view_model._core.add_item.return_value = new_item_id

        result_id = view_model.add_item(name=item_name, new_item_node_type=item_type, selected_potential_parent_id=None)
        
        view_model._core.add_item.assert_called_once_with(
            name=item_name, 
            parent_id=mock_tree.DUMMY_ROOT_ID, 
            index=-1, 
            node_type=item_type
        )
        assert result_id == new_item_id

    def test_add_item_logic_selected_group(self, view_model):
        item_name = "New Child Item"
        item_type = MTNodeType.INSTRUCTION
        selected_group_id = "group1"
        new_item_id = "child_item_456"

        view_model._core.get_item_node_type.return_value = MTNodeType.GROUP
        view_model._core.add_item.return_value = new_item_id

        result_id = view_model.add_item(name=item_name, new_item_node_type=item_type, selected_potential_parent_id=selected_group_id)
        
        view_model._core.get_item_node_type.assert_called_once_with(selected_group_id)
        view_model._core.add_item.assert_called_once_with(
            name=item_name,
            parent_id=selected_group_id, 
            index=-1,
            node_type=item_type
        )
        assert result_id == new_item_id

    def test_add_item_logic_selected_instruction(self, view_model):
        item_name = "New Sibling Item"
        item_type = MTNodeType.INSTRUCTION
        selected_instr_id = "instr1"
        parent_of_selected = "parent_group1"
        siblings_of_selected = ["other_instr0", selected_instr_id, "other_instr2"]
        new_item_id = "sibling_item_789"

        view_model._core.get_item_node_type.return_value = MTNodeType.INSTRUCTION
        view_model._core.get_item_parent_id.return_value = parent_of_selected
        view_model._core.get_children_ids.return_value = siblings_of_selected
        view_model._core.add_item.return_value = new_item_id

        result_id = view_model.add_item(name=item_name, new_item_node_type=item_type, selected_potential_parent_id=selected_instr_id)

        view_model._core.get_item_node_type.assert_called_once_with(selected_instr_id)
        view_model._core.get_item_parent_id.assert_called_once_with(selected_instr_id)
        view_model._core.get_children_ids.assert_called_once_with(parent_of_selected)
        view_model._core.add_item.assert_called_once_with(
            name=item_name,
            parent_id=parent_of_selected, 
            index=2, 
            node_type=item_type
        )
        assert result_id == new_item_id

    def test_remove_item_delegates_to_core(self, view_model):
        item_id_to_remove = "item_to_delete"
        view_model._core.remove_item.return_value = True
        
        result = view_model.remove_item(item_id_to_remove)
        
        view_model._core.remove_item.assert_called_once_with(item_id_to_remove)
        assert result is True

    def test_move_item_delegates_to_core(self, view_model):
        item_id_to_move = "item_xyz"
        new_parent_id = "new_parent_abc"
        view_model._core.move_item.return_value = True
        
        result = view_model.move_item(item_id_to_move, new_parent_id)
        
        view_model._core.move_item.assert_called_once_with(item_id_to_move, new_parent_id)
        assert result is True

    def test_can_undo_redo_delegates_to_state_manager(self, view_model, mock_state_manager):
        if not hasattr(view_model._model, '_state_mgr') or not view_model._model._state_mgr:
             pytest.skip("StateManager not available on model for this test.")
             return

        view_model._model._state_mgr.can_undo.return_value = True
        assert view_model.can_undo() is True
        view_model._model._state_mgr.can_undo.assert_called_once()

        view_model._model._state_mgr.can_redo.return_value = False
        assert view_model.can_redo() is False
        view_model._model._state_mgr.can_redo.assert_called_once()

    def test_get_selected_items_delegates_to_view_module(self, view_model):
        expected_selection = ["item1", "item2"]
        view_model._view.get_selected_item_ids.return_value = expected_selection
        
        actual_selection = view_model.get_selected_items()
        
        view_model._view.get_selected_item_ids.assert_called_once()
        assert actual_selection == expected_selection

    def test_toggle_expanded_delegates_to_view_module(self, view_model):
        item_id = "group_a"
        expanded_state = True
        view_model._view.set_item_expanded_state.return_value = True

        result = view_model.toggle_expanded(item_id, expanded_state)
        
        view_model._view.set_item_expanded_state.assert_called_once_with(item_id, expanded_state)
        assert result is True 