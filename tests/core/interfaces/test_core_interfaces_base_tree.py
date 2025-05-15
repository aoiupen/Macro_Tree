from core.interfaces.base_tree import IMTTree

def test_base_tree_protocol():
    # Protocol은 직접 인스턴스화할 수 없으므로, 타입 확인만
    assert hasattr(IMTTree, "add_item") 