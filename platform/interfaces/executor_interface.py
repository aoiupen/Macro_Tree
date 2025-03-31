from typing import Protocol, runtime_checkable

@runtime_checkable
class IExecutor(Protocol):
    """실행 작업 인터페이스
    
    아이템 실행 관련 작업을 정의합니다.
    """
    def execute_item(self, item_id: str) -> bool: ...
    # 기타 필요한 메서드...
