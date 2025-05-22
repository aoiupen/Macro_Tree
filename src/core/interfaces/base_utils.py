from typing import Optional
from core.interfaces.base_tree import IMTItem
from core.interfaces.base_item_data import MTItemDomainDTO

def to_tree_item_data(
    item: IMTItem,
    parent_id: Optional[str],
    selected: bool = False
) -> MTItemDomainDTO:
    """
    IMTItem 객체와 parent_id, selected 정보를 받아 MTItemDomainDTO로 변환하는 함수의 인터페이스입니다.
    """
    # RF : 클래스 밖에 있는 함수는 인터페이스여도 pass나 ... 대신 raise NotImplementedError 을 추가해야 mypy 정적 검사 통과
    raise NotImplementedError