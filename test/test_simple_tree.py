import sys
import os
import unittest
import tempfile
import json

# Python 경로 설정
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from model.implementations.simple_tree import SimpleTree
from model.implementations.simple_tree_item import SimpleTreeItem

class TestSimpleTree(unittest.TestCase):
    def setUp(self):
        self.tree = SimpleTree()
        
        # 테스트용 아이템 추가
        self.root = SimpleTreeItem("root", "Root Item")
        self.tree.add_item(self.root)
        
        self.group1 = SimpleTreeItem("group1", "Group 1")
        self.tree.add_item(self.group1, "root")
        
        self.item1 = SimpleTreeItem("item1", "Item 1")
        self.tree.add_item(self.item1, "group1")
    
    def test_add_and_get_item(self):
        # 아이템 추가 테스트
        item = self.tree.get_item("item1")
        self.assertIsNotNone(item)
        self.assertEqual(item.get_id(), "item1")
        self.assertEqual(item.get_property("name"), "Item 1")
        self.assertEqual(item.get_property("parent_id"), "group1")
    
    def test_remove_item(self):
        # 아이템 제거 테스트
        self.assertTrue(self.tree.remove_item("group1"))
        
        # 제거된 아이템 확인
        self.assertIsNone(self.tree.get_item("group1"))
        self.assertIsNone(self.tree.get_item("item1"))  # 자식도 함께 제거되어야 함
        self.assertIsNotNone(self.tree.get_item("root"))  # 다른 아이템은 남아있어야 함
    
    def test_update_item(self):
        # 이름 업데이트 테스트
        self.assertTrue(self.tree.update_item("item1", name="Updated Item"))
        item = self.tree.get_item("item1")
        self.assertEqual(item.get_property("name"), "Updated Item")
        
        # 부모 업데이트 테스트
        self.assertTrue(self.tree.update_item("item1", parent_id="root"))
        item = self.tree.get_item("item1")
        self.assertEqual(item.get_property("parent_id"), "root")
    
    def test_circular_reference_prevention(self):
        # 순환 참조 시도 (자기 자신을 부모로)
        self.assertFalse(self.tree.update_item("root", parent_id="root"))
        
        # 순환 참조 시도 (자식을 부모로)
        self.assertFalse(self.tree.update_item("root", parent_id="group1"))
    
    def test_json_serialization(self):
        # JSON 직렬화 테스트
        json_str = self.tree.to_json()
        
        # JSON 파싱 가능 여부 확인
        data = json.loads(json_str)
        self.assertIn("root", data)
        self.assertIn("group1", data)
        self.assertIn("item1", data)
        
        # 데이터 정확성 확인
        self.assertEqual(data["root"]["name"], "Root Item")
        self.assertEqual(data["group1"]["parent_id"], "root")
        self.assertEqual(data["item1"]["parent_id"], "group1")
    
    def test_json_deserialization(self):
        # 직렬화
        json_str = self.tree.to_json()
        
        # 역직렬화하여 새 트리 생성
        new_tree = SimpleTree.from_json(json_str)
        
        # 데이터 정확성 확인
        self.assertIsNotNone(new_tree.get_item("root"))
        self.assertIsNotNone(new_tree.get_item("group1"))
        self.assertIsNotNone(new_tree.get_item("item1"))
        
        item = new_tree.get_item("item1")
        self.assertEqual(item.get_property("name"), "Item 1")
        self.assertEqual(item.get_property("parent_id"), "group1")
    
    def test_file_save_and_load(self):
        # 임시 파일 생성
        with tempfile.NamedTemporaryFile(delete=False, suffix='.json') as tmp:
            temp_path = tmp.name
        
        try:
            # 파일에 저장
            self.assertTrue(self.tree.save_to_file(temp_path))
            
            # 파일에서 로드
            loaded_tree = SimpleTree.load_from_file(temp_path)
            self.assertIsNotNone(loaded_tree)
            
            # 데이터 정확성 확인
            self.assertIsNotNone(loaded_tree.get_item("root"))
            self.assertIsNotNone(loaded_tree.get_item("group1"))
            self.assertIsNotNone(loaded_tree.get_item("item1"))
            
            item = loaded_tree.get_item("item1")
            self.assertEqual(item.get_property("name"), "Item 1")
            self.assertEqual(item.get_property("parent_id"), "group1")
        
        finally:
            # 임시 파일 삭제
            if os.path.exists(temp_path):
                os.remove(temp_path)

if __name__ == "__main__":
    unittest.main()