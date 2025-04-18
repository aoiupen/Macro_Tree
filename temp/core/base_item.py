from typing import Any, Dict, Protocol


class IMTBaseItem(Protocol):
    """기본 아이템 인터페이스"""
    @property
    def id(self) -> str: ...
    
    @property
    def data(self) -> Dict[str, Any]: ...
