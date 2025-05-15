from core.interfaces.base_item import IMTTreeItem

def test_base_item_protocol():
    assert hasattr(IMTTreeItem, "item_id") 