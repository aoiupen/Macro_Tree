from typing import Optional

from core.tree import IMTTreeReadable


class MockTree(IMTTreeReadable):
    """테스트용 IMTTreeReadable 목 구현"""
    
    def __init__(self, items_data=None):
        self.items = items_data or []
    
    def get_item(self, item_id):
        for item in self.items:
            if item["id"] == item_id:
                return item
        return None
    
    def get_children(self, parent_id=None):
        return [item for item in self.items if item.get("parent_id") == parent_id]
