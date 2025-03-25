from typing import Protocol, runtime_checkable

@runtime_checkable
class IItemViewModel(Protocol):
    """아이템 데이터 접근 인터페이스
    
    아이템의 데이터 속성과 상태 변경 작업을 정의합니다.
    """
    id: str
    name: str
    inp: str
    sub: str
    sub_con: str
    expanded: bool
    
    def is_group(self) -> bool: ...
    def is_inst(self) -> bool: ...
    # 기타 필요한 메서드...
