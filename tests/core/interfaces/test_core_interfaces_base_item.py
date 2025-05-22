from core.interfaces.base_item import IMTItem

def test_base_item_protocol():
    assert hasattr(IMTItem, "item_id") 