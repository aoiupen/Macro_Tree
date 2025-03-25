"""UseCase 실행 인터페이스 모듈

비즈니스 로직 실행을 위한 인터페이스를 정의합니다.
"""
from typing import Protocol, Dict, Any, Optional

class IExecutor(Protocol):
    """UseCase 실행 인터페이스"""
    
    def execute_item(self, item_id: str) -> bool:
        """아이템을 실행합니다.
        
        Args:
            item_id: 실행할 아이템의 ID
            
        Returns:
            실행 성공 여부
        """
        ... 