from typing import Any, Dict, List, Protocol

from viewmodel.tree_viewmodel import IMTTreeViewModel


class IMTTreeBridge(Protocol):
    """QML-PyQt 브릿지 인터페이스"""
    
    def __init__(self, viewmodel: IMTTreeViewModel):
        """브릿지 초기화"""
        ...
    
    def get_items_for_qml(self) -> List[Dict[str, Any]]:
        """QML용 아이템 데이터 변환"""
        ...
    
    def handle_qml_item_selected(self, item_id: str) -> None:
        """QML에서의 아이템 선택 처리"""
        ...
    
    # 다른 메서드들...
