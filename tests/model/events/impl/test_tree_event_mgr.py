import pytest
from unittest.mock import Mock, call

from src.model.events.impl.tree_event_mgr import MTTreeEventManager
from src.model.events.interfaces.base_tree_event_mgr import MTTreeEvent, TreeEventCallback

class TestMTTreeEventManager:

    @pytest.fixture
    def event_manager(self):
        return MTTreeEventManager()

    @pytest.fixture
    def mock_callback_one(self):
        return Mock(spec=TreeEventCallback)

    @pytest.fixture
    def mock_callback_two(self):
        return Mock(spec=TreeEventCallback)

    def test_initialization(self, event_manager):
        """Test that the event manager initializes with empty subscriber lists for all event types."""
        for event_type in MTTreeEvent:
            assert event_type in event_manager._subscribers
            assert len(event_manager._subscribers[event_type]) == 0

    def test_subscribe_single_callback(self, event_manager, mock_callback_one):
        """Test subscribing a single callback to an event."""
        event_manager.subscribe(MTTreeEvent.ITEM_ADDED, mock_callback_one)
        assert mock_callback_one in event_manager._subscribers[MTTreeEvent.ITEM_ADDED]
        assert len(event_manager._subscribers[MTTreeEvent.ITEM_ADDED]) == 1

    def test_subscribe_multiple_callbacks_same_event(self, event_manager, mock_callback_one, mock_callback_two):
        """Test subscribing multiple callbacks to the same event."""
        event_manager.subscribe(MTTreeEvent.ITEM_REMOVED, mock_callback_one)
        event_manager.subscribe(MTTreeEvent.ITEM_REMOVED, mock_callback_two)
        
        assert mock_callback_one in event_manager._subscribers[MTTreeEvent.ITEM_REMOVED]
        assert mock_callback_two in event_manager._subscribers[MTTreeEvent.ITEM_REMOVED]
        assert len(event_manager._subscribers[MTTreeEvent.ITEM_REMOVED]) == 2

    def test_subscribe_callbacks_different_events(self, event_manager, mock_callback_one, mock_callback_two):
        """Test subscribing callbacks to different events."""
        event_manager.subscribe(MTTreeEvent.ITEM_MODIFIED, mock_callback_one)
        event_manager.subscribe(MTTreeEvent.ITEM_MOVED, mock_callback_two)

        assert mock_callback_one in event_manager._subscribers[MTTreeEvent.ITEM_MODIFIED]
        assert len(event_manager._subscribers[MTTreeEvent.ITEM_MODIFIED]) == 1
        assert mock_callback_two in event_manager._subscribers[MTTreeEvent.ITEM_MOVED]
        assert len(event_manager._subscribers[MTTreeEvent.ITEM_MOVED]) == 1
        # 다른 이벤트 타입의 구독자 목록은 비어있어야 함 (예: ITEM_ADDED)
        if MTTreeEvent.ITEM_ADDED not in [MTTreeEvent.ITEM_MODIFIED, MTTreeEvent.ITEM_MOVED]:
             assert len(event_manager._subscribers[MTTreeEvent.ITEM_ADDED]) == 0


    def test_notify_single_subscriber(self, event_manager, mock_callback_one):
        """Test notifying a single subscriber."""
        event_data = {"item_id": "test1", "parent_id": "root"}
        event_manager.subscribe(MTTreeEvent.ITEM_ADDED, mock_callback_one)
        event_manager.notify(MTTreeEvent.ITEM_ADDED, event_data)
        
        mock_callback_one.assert_called_once_with(MTTreeEvent.ITEM_ADDED, event_data)

    def test_notify_multiple_subscribers_same_event(self, event_manager, mock_callback_one, mock_callback_two):
        """Test notifying multiple subscribers of the same event."""
        event_data = {"item_id": "test2"}
        event_manager.subscribe(MTTreeEvent.ITEM_REMOVED, mock_callback_one)
        event_manager.subscribe(MTTreeEvent.ITEM_REMOVED, mock_callback_two)
        event_manager.notify(MTTreeEvent.ITEM_REMOVED, event_data)

        mock_callback_one.assert_called_once_with(MTTreeEvent.ITEM_REMOVED, event_data)
        mock_callback_two.assert_called_once_with(MTTreeEvent.ITEM_REMOVED, event_data)

    def test_notify_no_subscribers(self, event_manager, mock_callback_one):
        """Test that notify does nothing if there are no subscribers for an event."""
        event_data = {"item_id": "test3"}
        # ITEM_MODIFIED에는 구독했지만, ITEM_ADDED에는 구독 안 함
        event_manager.subscribe(MTTreeEvent.ITEM_MODIFIED, mock_callback_one)
        event_manager.notify(MTTreeEvent.ITEM_ADDED, event_data) # ITEM_ADDED 이벤트 발생

        mock_callback_one.assert_not_called() # ITEM_MODIFIED 구독자는 호출되지 않아야 함

    def test_notify_correct_subscribers_for_event(self, event_manager, mock_callback_one, mock_callback_two):
        """Test that only subscribers for the specific event are notified."""
        event_data_added = {"item_id": "added_item"}
        event_data_removed = {"item_id": "removed_item"}

        event_manager.subscribe(MTTreeEvent.ITEM_ADDED, mock_callback_one)
        event_manager.subscribe(MTTreeEvent.ITEM_REMOVED, mock_callback_two)

        event_manager.notify(MTTreeEvent.ITEM_ADDED, event_data_added)

        mock_callback_one.assert_called_once_with(MTTreeEvent.ITEM_ADDED, event_data_added)
        mock_callback_two.assert_not_called() # ITEM_REMOVED 구독자는 호출되지 않아야 함

    def test_unsubscribe_single_callback(self, event_manager, mock_callback_one, mock_callback_two):
        """Test unsubscribing a single callback."""
        event_manager.subscribe(MTTreeEvent.ITEM_MODIFIED, mock_callback_one)
        event_manager.subscribe(MTTreeEvent.ITEM_MODIFIED, mock_callback_two)
        
        event_manager.unsubscribe(MTTreeEvent.ITEM_MODIFIED, mock_callback_one)
        
        assert mock_callback_one not in event_manager._subscribers[MTTreeEvent.ITEM_MODIFIED]
        assert mock_callback_two in event_manager._subscribers[MTTreeEvent.ITEM_MODIFIED]
        assert len(event_manager._subscribers[MTTreeEvent.ITEM_MODIFIED]) == 1

        # 알림 테스트: mock_callback_one은 호출되지 않아야 함
        event_data = {"changes": {"name": "new_name"}}
        event_manager.notify(MTTreeEvent.ITEM_MODIFIED, event_data)
        mock_callback_one.assert_not_called()
        mock_callback_two.assert_called_once_with(MTTreeEvent.ITEM_MODIFIED, event_data)


    def test_unsubscribe_non_subscribed_callback(self, event_manager, mock_callback_one, mock_callback_two):
        """Test unsubscribing a callback that was not subscribed."""
        event_manager.subscribe(MTTreeEvent.ITEM_MOVED, mock_callback_one)
        # mock_callback_two는 구독하지 않음
        
        initial_subscribers = list(event_manager._subscribers[MTTreeEvent.ITEM_MOVED])
        
        event_manager.unsubscribe(MTTreeEvent.ITEM_MOVED, mock_callback_two) # 존재하지 않는 콜백 구독 해제
        
        # 구독자 목록은 변경되지 않아야 함
        assert event_manager._subscribers[MTTreeEvent.ITEM_MOVED] == initial_subscribers
        assert len(event_manager._subscribers[MTTreeEvent.ITEM_MOVED]) == 1


    def test_unsubscribe_from_event_with_no_subscribers(self, event_manager, mock_callback_one):
        """Test unsubscribing from an event type that has no subscribers."""
        # ITEM_ADDED 에는 아무도 구독하지 않음
        event_manager.unsubscribe(MTTreeEvent.ITEM_ADDED, mock_callback_one)
        assert len(event_manager._subscribers[MTTreeEvent.ITEM_ADDED]) == 0 # 여전히 0이어야 함

    def test_subscribe_unsubscribe_idempotency(self, event_manager, mock_callback_one):
        """Test that subscribing multiple times and unsubscribing works as expected."""
        event_manager.subscribe(MTTreeEvent.TREE_RESET, mock_callback_one)
        event_manager.subscribe(MTTreeEvent.TREE_RESET, mock_callback_one) # 동일 콜백 다시 구독
        assert len(event_manager._subscribers[MTTreeEvent.TREE_RESET]) == 2 # 중복 허용 (현재 구현)

        event_manager.unsubscribe(MTTreeEvent.TREE_RESET, mock_callback_one)
        # 현재 unsubscribe는 일치하는 모든 콜백을 제거
        assert len(event_manager._subscribers[MTTreeEvent.TREE_RESET]) == 0
        
        # 다시 구독 및 알림 테스트
        event_manager.subscribe(MTTreeEvent.TREE_RESET, mock_callback_one)
        event_data = {"tree_id": "new_tree"}
        event_manager.notify(MTTreeEvent.TREE_RESET, event_data)
        mock_callback_one.assert_called_once_with(MTTreeEvent.TREE_RESET, event_data) 