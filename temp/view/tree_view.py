from typing import Protocol, List, Dict, Any, Callable

class IMTTreeView(Protocol):
    """트리 뷰 인터페이스"""
    
    def set_items(self, items: List[Dict[str, Any]]) -> None:
        """트리 아이템 설정"""
        ...
    
    def get_selected_items(self) -> List[str]:
        """선택된 아이템 ID 목록 반환"""
        ...
    
    # 다른 메서드들...
