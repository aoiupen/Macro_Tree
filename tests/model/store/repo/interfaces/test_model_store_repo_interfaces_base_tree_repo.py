from model.store.repo.interfaces.base_tree_repo import IMTTreeRepository

def test_base_tree_repo_protocol():
    assert hasattr(IMTTreeRepository, "save_tree") 