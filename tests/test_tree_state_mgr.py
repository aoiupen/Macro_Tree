import pytest
from unittest.mock import Mock, call

# 프로젝트 구조에 따라 올바른 경로로 수정해야 할 수 있습니다.
# 예를 들어, `PYTHONPATH`에 `src`가 포함되어 있거나, `pytest`가 이를 자동으로 처리하는 경우:
from model.state.impl.tree_state_mgr import MTTreeStateManager
from core.interfaces.base_tree import IMTTree # IMTTree를 Mocking하기 위해 import

# 테스트용 더미 상태 데이터
DUMMY_STATE_1 = {"id": "root", "children": [{"id": "child1"}]}
DUMMY_STATE_2 = {"id": "root", "children": [{"id": "child1"}, {"id": "child2"}]}
DUMMY_STATE_3 = {"id": "root", "children": [{"id": "child3"}]}
INITIAL_STATE = {"id": "initial"}

@pytest.fixture
def mock_tree():
    """IMTTree 인터페이스를 만족하는 Mock 객체를 생성합니다."""
    tree = Mock(spec=IMTTree)
    tree.to_dict = Mock(return_value=INITIAL_STATE)
    return tree

@pytest.fixture
def state_manager(mock_tree):
    """테스트를 위한 MTTreeStateManager 인스턴스를 생성합니다."""
    # MTTreeStateManager 생성 시 __init__에서 mock_tree.to_dict()를 호출하여 _stage를 설정
    return MTTreeStateManager(tree=mock_tree, max_history=3)

@pytest.fixture
def state_manager_default_history(mock_tree):
    """기본 max_history를 사용하는 StateManager 인스턴스입니다."""
    return MTTreeStateManager(tree=mock_tree)

def test_initial_state(state_manager, mock_tree):
    """초기 상태 설정 테스트"""
    mock_tree.to_dict.assert_called_once()
    assert state_manager._stage == INITIAL_STATE # _stage 직접 확인
    assert not state_manager.can_undo()
    assert not state_manager.can_redo()
    assert state_manager._undo_stack == []
    assert state_manager._redo_stack == []

def test_set_initial_state_resets_history(state_manager, mock_tree):
    """set_initial_state가 히스토리를 초기화하고 _stage를 변경하는지 테스트"""
    # 초기 상태: _stage = INITIAL_STATE
    state_manager.new_undo(DUMMY_STATE_1) # _stage=S1, undo=[I]
    state_manager.undo(DUMMY_STATE_1)     # _stage=I, redo=[S1]

    assert not state_manager.can_undo()
    assert state_manager.can_redo()
    assert state_manager._stage == INITIAL_STATE

    new_initial_state_dict = {"id": "new_initial"}
    mock_new_tree = Mock(spec=IMTTree)
    mock_new_tree.to_dict = Mock(return_value=new_initial_state_dict)

    state_manager.set_initial_state(mock_new_tree)

    mock_new_tree.to_dict.assert_called_once()
    assert state_manager._stage == new_initial_state_dict
    assert state_manager._undo_stack == []
    assert state_manager._redo_stack == []
    assert not state_manager.can_undo()
    assert not state_manager.can_redo()

def test_new_undo_basic(state_manager):
    """new_undo 기본 동작 테스트"""
    # 초기 상태: _stage = INITIAL_STATE
    current_stage_before_op = state_manager._stage # INITIAL_STATE

    returned_stage = state_manager.new_undo(DUMMY_STATE_1)

    assert returned_stage == DUMMY_STATE_1
    assert state_manager.can_undo()
    assert state_manager._undo_stack == [current_stage_before_op]
    assert state_manager._stage == DUMMY_STATE_1
    assert state_manager._redo_stack == []

def test_new_undo_clears_redo_stack(state_manager):
    """new_undo가 redo 스택을 비우는지 테스트"""
    # 초기 _stage = INITIAL_STATE
    state_manager.new_undo(DUMMY_STATE_1) # _stage=S1, undo=[I]
    state_manager.new_undo(DUMMY_STATE_2) # _stage=S2, undo=[I,S1]
    state_manager.undo(DUMMY_STATE_2)     # _stage=S1, undo=[I], redo=[S2]
    
    assert state_manager.can_redo()
    assert state_manager._redo_stack == [DUMMY_STATE_2]
    current_stage_before_new_op = state_manager._stage # DUMMY_STATE_1

    returned_stage = state_manager.new_undo(DUMMY_STATE_3)

    assert returned_stage == DUMMY_STATE_3
    assert state_manager._undo_stack == [INITIAL_STATE, current_stage_before_new_op]
    assert state_manager._stage == DUMMY_STATE_3
    assert not state_manager.can_redo()
    assert state_manager._redo_stack == []

def test_undo_basic(state_manager):
    """undo 기본 동작 테스트"""
    # 초기 _stage = INITIAL_STATE
    state_manager.new_undo(DUMMY_STATE_1) # _stage=S1, undo=[I]
    state_manager.new_undo(DUMMY_STATE_2) # _stage=S2, undo=[I,S1]

    current_stage_for_undo_arg = state_manager._stage # DUMMY_STATE_2
    undone_state_as_new_stage = state_manager.undo(current_stage_for_undo_arg)

    assert undone_state_as_new_stage == DUMMY_STATE_1
    assert state_manager._stage == DUMMY_STATE_1
    assert state_manager.can_undo()
    assert state_manager.can_redo()
    assert state_manager._undo_stack == [INITIAL_STATE]
    assert state_manager._redo_stack == [DUMMY_STATE_2]

def test_undo_empty_stack(state_manager):
    """빈 undo 스택에서 undo 시도"""
    # 초기 _stage = INITIAL_STATE, undo_stack = []
    assert not state_manager.can_undo()
    assert state_manager.undo(state_manager._stage) is None
    assert state_manager._stage == INITIAL_STATE
    assert not state_manager.can_redo()

def test_redo_basic(state_manager):
    """redo 기본 동작 테스트"""
    # 초기 _stage = INITIAL_STATE
    state_manager.new_undo(DUMMY_STATE_1)  # _stage=S1, undo=[I]
    state_manager.new_undo(DUMMY_STATE_2)  # _stage=S2, undo=[I, S1]
    state_manager.undo(DUMMY_STATE_2)      # _stage=S1, undo=[I], redo=[S2]

    current_stage_for_redo_arg = state_manager._stage # DUMMY_STATE_1
    redone_state_as_new_stage = state_manager.redo(current_stage_for_redo_arg)

    assert redone_state_as_new_stage == DUMMY_STATE_2
    assert state_manager._stage == DUMMY_STATE_2
    assert state_manager.can_undo()
    assert not state_manager.can_redo()
    assert state_manager._undo_stack == [INITIAL_STATE, DUMMY_STATE_1]
    assert state_manager._redo_stack == []

def test_redo_empty_stack(state_manager):
    """빈 redo 스택에서 redo 시도"""
    # 초기 _stage = INITIAL_STATE, redo_stack = []
    assert not state_manager.can_redo()
    assert state_manager.redo(state_manager._stage) is None
    assert state_manager._stage == INITIAL_STATE

def test_stack_limit_undo(state_manager): # max_history=3
    """undo 스택 최대치 제한 테스트"""
    # _stage = INITIAL_STATE
    state_manager.new_undo(DUMMY_STATE_1) # undo=[I], _stage=S1
    state_manager.new_undo(DUMMY_STATE_2) # undo=[I,S1], _stage=S2
    state_manager.new_undo(DUMMY_STATE_3) # undo=[I,S1,S2], _stage=S3
    assert len(state_manager._undo_stack) == 3
    
    state_4 = {"id": "state4"}
    state_manager.new_undo(state_4) # undo=[S1,S2,S3], _stage=S4 (INITIAL_STATE 제거됨)
    assert len(state_manager._undo_stack) == 3
    assert state_manager._undo_stack[0] == DUMMY_STATE_1 
    assert state_manager._undo_stack[-1] == DUMMY_STATE_3
    assert state_manager._stage == state_4

def test_stack_limit_redo(state_manager): # max_history=3
    """redo 스택 최대치 제한 테스트"""
    s0, s1, s2, s3, s4 = INITIAL_STATE, DUMMY_STATE_1, DUMMY_STATE_2, DUMMY_STATE_3, {"id": "S4"}

    state_manager.new_undo(s1)  # U:[s0], _stage=s1
    state_manager.new_undo(s2)  # U:[s0,s1], _stage=s2
    state_manager.new_undo(s3)  # U:[s0,s1,s2], _stage=s3
    state_manager.new_undo(s4)  # U:[s1,s2,s3], _stage=s4 (s0 제거)

    current_stage = s4
    current_stage = state_manager.undo(current_stage) # R:[s4], _stage=s3, U:[s1,s2]
    current_stage = state_manager.undo(current_stage) # R:[s4,s3], _stage=s2, U:[s1]
    current_stage = state_manager.undo(current_stage) # R:[s4,s3,s2], _stage=s1, U:[]
    assert len(state_manager._redo_stack) == 3
    
    state_manager._undo_stack = [{"id": "temp_for_undo"}] # 임시로 undo 가능하게 만듦
    # 현재 state_manager._stage == s1
    
    current_stage = state_manager.undo(s1) # R:[s3,s2,s1], _stage=temp_for_undo, U:[] (s4 제거)
    assert len(state_manager._redo_stack) == 3
    assert state_manager._redo_stack[0] == DUMMY_STATE_3 # s3
    assert state_manager._redo_stack[-1] == DUMMY_STATE_1 # s1
    assert state_manager._stage == {"id": "temp_for_undo"}

def test_subscription(state_manager):
    """구독 및 알림 테스트"""
    mock_callback = Mock()
    state_manager.subscribe(mock_callback)

    # new_undo는 조작 후 데이터를 받음, _stage는 DUMMY_STATE_1로 변경됨
    # _notify_subscribers는 변경된 _stage (DUMMY_STATE_1)를 전달
    state_manager.new_undo(DUMMY_STATE_1)
    mock_callback.assert_called_with(DUMMY_STATE_1)
    
    mock_callback.reset_mock()
    # undo 호출, 현재 _stage는 DUMMY_STATE_1, undo 후 _stage는 INITIAL_STATE가 됨
    # _notify_subscribers는 변경된 _stage (INITIAL_STATE)를 전달
    state_manager.undo(DUMMY_STATE_1)
    mock_callback.assert_called_with(INITIAL_STATE)

    mock_callback.reset_mock()
    # redo 호출, 현재 _stage는 INITIAL_STATE, redo 후 _stage는 DUMMY_STATE_1이 됨
    # _notify_subscribers는 변경된 _stage (DUMMY_STATE_1)를 전달
    state_manager.redo(INITIAL_STATE)
    mock_callback.assert_called_with(DUMMY_STATE_1)

    mock_callback.reset_mock()
    state_manager.unsubscribe(mock_callback)
    state_manager.new_undo(DUMMY_STATE_2) # _stage는 DUMMY_STATE_2로 변경
    mock_callback.assert_not_called() # 구독 해지했으므로 호출 안됨

def test_can_undo_redo_behavior(state_manager):
    """can_undo, can_redo 정확성 테스트"""
    # 초기 _stage = INITIAL_STATE
    assert not state_manager.can_undo()
    assert not state_manager.can_redo()

    state_manager.new_undo(DUMMY_STATE_1) # _stage=S1, undo=[I]
    assert state_manager.can_undo()
    assert not state_manager.can_redo()

    current_stage_before_undo = state_manager._stage # DUMMY_STATE_1
    state_manager.undo(current_stage_before_undo) # _stage=I, undo=[], redo=[S1]
    assert not state_manager.can_undo()
    assert state_manager.can_redo()

    current_stage_before_redo = state_manager._stage # INITIAL_STATE
    state_manager.redo(current_stage_before_redo) # _stage=S1, undo=[I], redo=[]
    assert state_manager.can_undo()
    assert not state_manager.can_redo()
    assert state_manager._stage == DUMMY_STATE_1

def test_max_history_default(mock_tree):
    """기본 max_history 값 테스트"""
    manager = MTTreeStateManager(tree=mock_tree) # _stage = INITIAL_STATE
    assert manager._max_history == 100

    current_stage = manager._stage # INITIAL_STATE
    for i in range(101):
        new_stage_data = {"id": f"state_{i}"}
        manager.new_undo(new_stage_data) # 이전 _stage가 undo 스택으로, new_stage_data가 현재 _stage가 됨
        # current_stage 변수는 이 루프 내에서는 직접 사용되지 않음 (manager 내부의 _stage가 중요)
        
    assert len(manager._undo_stack) == 100
    # 첫 new_undo: undo=[INITIAL_STATE], _stage=state_0
    # 두번째 new_undo: undo=[INITIAL_STATE, state_0], _stage=state_1
    # ...
    # 101번째 new_undo (i=100): undo=[state_0, ..., state_99], _stage=state_100 (INITIAL_STATE 제거)
    assert manager._undo_stack[0] == {"id": "state_0"}
    assert manager._undo_stack[-1] == {"id": "state_99"}
    assert manager._stage == {"id": "state_100"} 