import unittest
import sys
import os

# temp 패키지를 Python 경로에 추가
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from temp.model.implementations.simple_tree import SimpleTree
from temp.model.implementations.simple_tree_item import SimpleTreeItem

class TestSimpleTree(unittest.TestCase):
    def test_add_and_get_item(self):
        # Given
        tree = SimpleTree()
        item = SimpleTreeItem("test-1", "Test Item")
        
        # When
        success = tree.add_item(item)
        
        # Then
        self.assertTrue(success)
        retrieved = tree.get_item("test-1")
        self.assertEqual(retrieved.get_id(), "test-1")
        self.assertEqual(retrieved.get_property("name"), "Test Item")

if __name__ == "__main__":
    unittest.main()
