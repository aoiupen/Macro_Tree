import unittest
from unittest.mock import Mock, patch, call
from typing import Dict, Any

from src.model.state.impl.tree_state_mgr import MTTreeStateManager
from src.core.interfaces.base_tree import IMTTree # IMTTree를 import해야 합니다.
from src.model.events.interfaces.base_tree_event_mgr import MTTreeEvent # MTTreeEvent를 import해야 합니다.


class TestMTTreeStateManager(unittest.TestCase):

    def _create_mock_tree(self, tree_id: str, name: str, root_id: str, items: Dict[str, Any]) -> IMTTree:
        mock_tree = Mock(spec=IMTTree)
        mock_tree.to_dict.return_value = {
            "id": tree_id,
            "name": name,
            "root_id": root_id,
            "items": items
        }
        return mock_tree

    def setUp(self):
        self.initial_items = {
            "root": {"id": "root", "data": Mock(children_ids=["item1"]), "name": "Root"},
            "item1": {"id": "item1", "data": Mock(children_ids=[]), "name": "Item 1"}
        }
        self.mock_initial_tree = self._create_mock_tree("tree1", "Initial Tree", "root", self.initial_items)
        self.state_manager = MTTreeStateManager(tree=self.mock_initial_tree, max_history=3)

        # 각 테스트에서 사용할 stage 데이터
        self.stage0 = self.mock_initial_tree.to_dict() # 초기 상태
        self.stage1 = {"id": "tree1", "name": "State 1", "root_id": "root", "items": {"root": {"id": "root", "name": "Root"}, "item1": {"id": "item1", "name": "Item 1 v2"}}}
        self.stage2 = {"id": "tree1", "name": "State 2", "root_id": "root", "items": {"root": {"id": "root", "name": "Root"}, "item2": {"id": "item2", "name": "Item 2"}}}
        self.stage3 = {"id": "tree1", "name": "State 3", "root_id": "root", "items": {"root": {"id": "root", "name": "Root"}, "item3": {"id": "item3", "name": "Item 3"}}}
        self.stage4 = {"id": "tree1", "name": "State 4", "root_id": "root", "items": {"root": {"id": "root", "name": "Root"}, "item4": {"id": "item4", "name": "Item 4"}}}


    def test_initialization_and_set_initial_state(self):
        self.assertEqual(self.state_manager._new_stage, self.stage0)
        self.assertFalse(self.state_manager.can_undo())
        self.assertFalse(self.state_manager.can_redo())
        self.assertEqual(len(self.state_manager._undo_stack), 0)
        self.assertEqual(len(self.state_manager._redo_stack), 0)

        new_items = {"root": {"id": "root", "data": Mock(children_ids=[]), "name": "New Root"}}
        mock_new_initial_tree = self._create_mock_tree("tree2", "New Initial Tree", "root", new_items)
        new_initial_stage = mock_new_initial_tree.to_dict()

        self.state_manager.set_initial_state(mock_new_initial_tree)
        self.assertEqual(self.state_manager._new_stage, new_initial_stage)
        self.assertFalse(self.state_manager.can_undo())
        self.assertFalse(self.state_manager.can_redo())

    @patch.object(MTTreeStateManager, '_notify_subscribers')
    def test_new_undo(self, mock_notify):
        # 첫 번째 new_undo
        returned_stage = self.state_manager.new_undo(self.stage1)
        self.assertEqual(returned_stage, self.stage1)
        self.assertEqual(self.state_manager._new_stage, self.stage1)
        self.assertTrue(self.state_manager.can_undo())
        self.assertFalse(self.state_manager.can_redo())
        self.assertEqual(len(self.state_manager._undo_stack), 1)
        self.assertEqual(self.state_manager._undo_stack[0], self.stage0)
        self.assertEqual(len(self.state_manager._redo_stack), 0)
        mock_notify.assert_called_once_with(MTTreeEvent.TREE_CRUD, self.stage1)
        mock_notify.reset_mock()

        # 두 번째 new_undo
        returned_stage_2 = self.state_manager.new_undo(self.stage2)
        self.assertEqual(returned_stage_2, self.stage2)
        self.assertEqual(self.state_manager._new_stage, self.stage2)
        self.assertEqual(len(self.state_manager._undo_stack), 2)
        self.assertEqual(self.state_manager._undo_stack[0], self.stage0)
        self.assertEqual(self.state_manager._undo_stack[1], self.stage1)
        self.assertFalse(self.state_manager.can_redo()) # new_undo 시 redo 스택은 비워짐
        mock_notify.assert_called_once_with(MTTreeEvent.TREE_CRUD, self.stage2)

    @patch.object(MTTreeStateManager, '_notify_subscribers')
    def test_new_undo_clears_redo_stack(self, mock_notify):
        # Undo/Redo 히스토리 생성
        self.state_manager.new_undo(self.stage1) # undo: [stage0], new_stage: stage1
        self.state_manager.new_undo(self.stage2) # undo: [stage0, stage1], new_stage: stage2
        mock_notify.reset_mock()

        # Undo 실행 -> Redo 스택에 stage2가 들어감
        self.state_manager.undo(self.state_manager._new_stage) # undo: [stage0], new_stage: stage1, redo: [stage2]
        self.assertTrue(self.state_manager.can_redo())
        self.assertEqual(self.state_manager._redo_stack[0], self.stage2)
        mock_notify.assert_called_once_with(MTTreeEvent.TREE_UNDO, self.stage1)
        mock_notify.reset_mock()

        # 이 상황에서 new_undo 실행 시 redo 스택이 비워져야 함
        self.state_manager.new_undo(self.stage3) # undo: [stage0, stage1], new_stage: stage3, redo: []
        self.assertFalse(self.state_manager.can_redo())
        self.assertEqual(len(self.state_manager._redo_stack), 0)
        self.assertEqual(self.state_manager._new_stage, self.stage3)
        self.assertEqual(len(self.state_manager._undo_stack), 2) # max_history 가 3이므로 아직 안 넘침
        mock_notify.assert_called_once_with(MTTreeEvent.TREE_CRUD, self.stage3)

    @patch.object(MTTreeStateManager, '_notify_subscribers')
    def test_undo_and_redo(self, mock_notify):
        self.state_manager.new_undo(self.stage1) # S0 -> U:[S0], N:S1
        self.state_manager.new_undo(self.stage2) # S1 -> U:[S0,S1], N:S2
        mock_notify.reset_mock()

        # Undo 1
        undone_stage = self.state_manager.undo(self.state_manager._new_stage) # N:S2가 R:[S2]로, U 스택에서 pop된 S1이 N:S1
        self.assertEqual(undone_stage, self.stage1)
        self.assertEqual(self.state_manager._new_stage, self.stage1)
        self.assertTrue(self.state_manager.can_undo())
        self.assertTrue(self.state_manager.can_redo())
        self.assertEqual(len(self.state_manager._undo_stack), 1) # [S0]
        self.assertEqual(self.state_manager._undo_stack[0], self.stage0)
        self.assertEqual(len(self.state_manager._redo_stack), 1) # [S2]
        self.assertEqual(self.state_manager._redo_stack[0], self.stage2)
        mock_notify.assert_called_once_with(MTTreeEvent.TREE_UNDO, self.stage1)
        mock_notify.reset_mock()

        # Undo 2
        undone_stage_2 = self.state_manager.undo(self.state_manager._new_stage) # N:S1이 R:[S2,S1]로, U 스택에서 pop된 S0이 N:S0
        self.assertEqual(undone_stage_2, self.stage0)
        self.assertEqual(self.state_manager._new_stage, self.stage0)
        self.assertFalse(self.state_manager.can_undo()) # Undo 스택 비었음
        self.assertTrue(self.state_manager.can_redo())
        self.assertEqual(len(self.state_manager._undo_stack), 0)
        self.assertEqual(len(self.state_manager._redo_stack), 2) # [S2, S1]
        self.assertEqual(self.state_manager._redo_stack[0], self.stage2)
        self.assertEqual(self.state_manager._redo_stack[1], self.stage1)
        mock_notify.assert_called_once_with(MTTreeEvent.TREE_UNDO, self.stage0)
        mock_notify.reset_mock()

        # Redo 1
        redone_stage = self.state_manager.redo(self.state_manager._new_stage) # N:S0이 U:[S0]로, R 스택에서 pop된 S1이 N:S1
        self.assertEqual(redone_stage, self.stage1)
        self.assertEqual(self.state_manager._new_stage, self.stage1)
        self.assertTrue(self.state_manager.can_undo())
        self.assertTrue(self.state_manager.can_redo())
        self.assertEqual(len(self.state_manager._undo_stack), 1) # [S0]
        self.assertEqual(self.state_manager._undo_stack[0], self.stage0)
        self.assertEqual(len(self.state_manager._redo_stack), 1) # [S2]
        self.assertEqual(self.state_manager._redo_stack[0], self.stage2)
        mock_notify.assert_called_once_with(MTTreeEvent.TREE_REDO, self.stage1)
        mock_notify.reset_mock()

        # Redo 2
        redone_stage_2 = self.state_manager.redo(self.state_manager._new_stage) # N:S1이 U:[S0,S1]로, R 스택에서 pop된 S2이 N:S2
        self.assertEqual(redone_stage_2, self.stage2)
        self.assertEqual(self.state_manager._new_stage, self.stage2)
        self.assertTrue(self.state_manager.can_undo())
        self.assertFalse(self.state_manager.can_redo()) # Redo 스택 비었음
        self.assertEqual(len(self.state_manager._undo_stack), 2) # [S0,S1]
        self.assertEqual(self.state_manager._undo_stack[0], self.stage0)
        self.assertEqual(self.state_manager._undo_stack[1], self.stage1)
        self.assertEqual(len(self.state_manager._redo_stack), 0)
        mock_notify.assert_called_once_with(MTTreeEvent.TREE_REDO, self.stage2)

    def test_undo_redo_when_stacks_are_empty(self):
        self.assertFalse(self.state_manager.can_undo())
        self.assertIsNone(self.state_manager.undo(self.state_manager._new_stage)) # 아무 변화 없음
        self.assertEqual(self.state_manager._new_stage, self.stage0) # new_stage는 그대로

        self.assertFalse(self.state_manager.can_redo())
        self.assertIsNone(self.state_manager.redo(self.state_manager._new_stage)) # 아무 변화 없음
        self.assertEqual(self.state_manager._new_stage, self.stage0) # new_stage는 그대로

    @patch.object(MTTreeStateManager, '_notify_subscribers')
    def test_max_history_limit_for_undo_stack(self, mock_notify):
        # max_history = 3
        self.state_manager.new_undo(self.stage1) # U:[S0], N:S1
        self.state_manager.new_undo(self.stage2) # U:[S0,S1], N:S2
        self.state_manager.new_undo(self.stage3) # U:[S0,S1,S2], N:S3
        self.assertEqual(len(self.state_manager._undo_stack), 3)
        self.assertEqual(self.state_manager._undo_stack[0], self.stage0)
        self.assertEqual(self.state_manager._undo_stack[1], self.stage1)
        self.assertEqual(self.state_manager._undo_stack[2], self.stage2)

        # 여기서 한 번 더 new_undo하면 가장 오래된 S0이 사라져야 함
        self.state_manager.new_undo(self.stage4) # U:[S1,S2,S3], N:S4
        self.assertEqual(len(self.state_manager._undo_stack), 3)
        self.assertEqual(self.state_manager._undo_stack[0], self.stage1)
        self.assertEqual(self.state_manager._undo_stack[1], self.stage2)
        self.assertEqual(self.state_manager._undo_stack[2], self.stage3)
        self.assertEqual(self.state_manager._new_stage, self.stage4)
        mock_notify.assert_called_with(MTTreeEvent.TREE_CRUD, self.stage4) # 마지막 호출 검증

    @patch.object(MTTreeStateManager, '_notify_subscribers')
    def test_max_history_limit_for_redo_stack(self, mock_notify):
        # 히스토리 생성 (U:[S0,S1,S2], N:S3)
        self.state_manager.new_undo(self.stage1)
        self.state_manager.new_undo(self.stage2)
        self.state_manager.new_undo(self.stage3)
        self.state_manager.new_undo(self.stage4) # 현재: U:[S1,S2,S3], N:S4. max_history=3

        # Undo를 3번 하여 Redo 스택 채우기
        # 1. Undo (N:S4 -> R:[S4], U:[S1,S2], N:S3)
        self.state_manager.undo(self.state_manager._new_stage)
        self.assertEqual(len(self.state_manager._redo_stack), 1)
        self.assertEqual(self.state_manager._redo_stack[0], self.stage4)

        # 2. Undo (N:S3 -> R:[S4,S3], U:[S1], N:S2)
        self.state_manager.undo(self.state_manager._new_stage)
        self.assertEqual(len(self.state_manager._redo_stack), 2)
        self.assertEqual(self.state_manager._redo_stack[1], self.stage3)

        # 3. Undo (N:S2 -> R:[S4,S3,S2], U:[], N:S1)
        self.state_manager.undo(self.state_manager._new_stage)
        self.assertEqual(len(self.state_manager._redo_stack), 3)
        self.assertEqual(self.state_manager._redo_stack[2], self.stage2)
        self.assertEqual(self.state_manager._redo_stack, [self.stage4, self.stage3, self.stage2]) # 순서 확인

        # 이 상태에서 Redo 스택이 꽉 찼으므로 (max_history=3)
        # 추가적인 Undo는 불가능 (Undo 스택이 비었음)
        # 만약 Undo가 더 가능해서 Redo 스택에 push될 때, _limit_stack이 호출됨.
        # 현재 코드는 undo 메소드 내에서 redo_stack에 append 후 _limit_stack을 호출.
        # 새로운 상태를 만들어 undo 스택에 넣고, 그 상태를 redo 스택으로 옮기는 상황을 만들어야 함.
        # 이를 테스트하기 위해, 먼저 redo를 한 번 해서 undo 스택에 공간을 만들고
        # 그 다음 new_undo를 하고, 다시 undo를 여러번 해서 redo 스택이 넘치도록 한다.

        # 현재: U:[], N:S1, R:[S4,S3,S2]
        # Redo 한번 (N:S1 -> U:[S1], R:[S4,S3], N:S2)
        self.state_manager.redo(self.state_manager._new_stage)
        # 이제 다시 Undo할 수 있는 상태가 됨. U:[S1], N:S2, R:[S4,S3]

        # 새로운 상태 추가
        stage5 = {"id": "tree1", "name": "State 5", "root_id": "root", "items": {}}
        self.state_manager.new_undo(stage5) # U:[S1,S2], N:S5, R:[] (redo 스택 clear)

        # 다시 undo해서 redo 스택을 채운다.
        self.state_manager.undo(self.state_manager._new_stage) # U:[S1], N:S2, R:[S5]
        self.state_manager.undo(self.state_manager._new_stage) # U:[], N:S1, R:[S5,S2]

        # redo 스택에 S1을 추가하기 위해 stage1을 redo
        # 먼저 stage1을 new_undo로 만들어야 함.
        # 현재: U:[], N:S1, R:[S5,S2]
        # new_undo (S0_variant)
        s0_variant = self.stage0.copy()
        s0_variant["name"] = "S0 Variant"
        self.state_manager.new_undo(s0_variant) # U:[S1], N:S0_variant, R:[]
        self.state_manager.undo(self.state_manager._new_stage) # U:[], N:S1, R:[S0_variant]

        # redo 스택이 [S5, S2, S0_variant] 가 될 수 있도록 조작
        self.state_manager._redo_stack = [self.stage4, self.stage3, self.stage2] # 강제 설정
        self.state_manager._new_stage = self.stage1 # 현재 상태
        self.state_manager._undo_stack = [] # undo 스택 비움

        # undo 호출 (이때 stage1이 redo_stack에 들어가면서 limit_stack이 호출됨)
        # self.state_manager.undo(self.stage_that_would_go_to_redo)
        # undo 시에는 new_stage가 redo_stack으로.
        # 이 테스트 케이스는 redo() 메소드가 redo_stack에서 pop하고 undo_stack에 push할 때,
        # undo_stack이 _limit_stack의 대상이 되는 것을 검증해야 함.
        # redo() 메소드에서는 self._undo_stack.append(stage) 이후 self._limit_stack(self._undo_stack) 호출.
        
        # redo_stack을 초과하게 만들고 redo를 실행
        self.state_manager._undo_stack = []
        self.state_manager._redo_stack = [self.stage1, self.stage2, self.stage3] # 꽉 참
        self.state_manager._new_stage = self.stage0 # 현재 상태
        
        # stage0을 undo 스택에 넣고, stage1을 redo에서 꺼내 new_stage로. undo_stack은 [stage0]
        self.state_manager.redo(self.state_manager._new_stage) 
        self.assertEqual(self.state_manager._new_stage, self.stage1)
        self.assertEqual(self.state_manager._undo_stack, [self.stage0])
        self.assertEqual(self.state_manager._redo_stack, [self.stage2, self.stage3])

        # stage1을 undo 스택에 넣고, stage2를 redo에서 꺼내 new_stage로. undo_stack은 [stage0, stage1]
        self.state_manager.redo(self.state_manager._new_stage)
        self.assertEqual(self.state_manager._new_stage, self.stage2)
        self.assertEqual(self.state_manager._undo_stack, [self.stage0, self.stage1])
        self.assertEqual(self.state_manager._redo_stack, [self.stage3])

        # stage2를 undo 스택에 넣고, stage3을 redo에서 꺼내 new_stage로. undo_stack은 [stage0, stage1, stage2] (꽉 참)
        self.state_manager.redo(self.state_manager._new_stage)
        self.assertEqual(self.state_manager._new_stage, self.stage3)
        self.assertEqual(self.state_manager._undo_stack, [self.stage0, self.stage1, self.stage2])
        self.assertEqual(self.state_manager._redo_stack, [])

        # 이제 undo_stack이 꽉 찼으므로, 여기서 redo를 한 번 더 실행하면 (redo 스택은 비어있음)
        # 아무일도 안일어남.
        # 만약 redo_stack에 아이템이 더 있고, undo_stack이 꽉찬 상태에서 redo를 하면,
        # undo_stack에 append할 때 가장 오래된 것이 밀려나야 함.
        self.state_manager._redo_stack = [self.stage4] # redo 할 아이템 하나 더 추가
        # 현재: U:[S0,S1,S2], N:S3, R:[S4]
        
        self.state_manager.redo(self.state_manager._new_stage)
        # N:S3이 U로 들어가면서 S0이 밀려나야 함 -> U:[S1,S2,S3]
        # R에서 S4가 N으로 -> N:S4
        self.assertEqual(self.state_manager._new_stage, self.stage4)
        self.assertEqual(self.state_manager._undo_stack, [self.stage1, self.stage2, self.stage3])
        self.assertEqual(self.state_manager._redo_stack, [])

    @patch('src.model.state.impl.tree_state_mgr.deepcopy') # deepcopy 사용 여부 확인 (현재 코드에는 없음)
    def test_deepcopy_not_used_on_stack_operations(self, mock_deepcopy):
        # 현재 MTTreeStateManager는 to_dict()를 통해 받은 dict를 그대로 사용하고,
        # 스택에 추가할 때 deepcopy를 명시적으로 사용하지 않습니다.
        # ViewModel이나 Tree 객체에서 to_dict()를 호출할 때 반환되는 dict가
        # 내부 상태의 복사본이라는 가정 하에 동작합니다.
        # 이 테스트는 MTTreeStateManager가 내부적으로 deepcopy를 호출하지 않음을 확인합니다.
        self.state_manager.new_undo(self.stage1)
        self.state_manager.undo(self.state_manager._new_stage)
        self.state_manager.redo(self.state_manager._new_stage)
        mock_deepcopy.assert_not_called()


if __name__ == '__main__':
    unittest.main() 