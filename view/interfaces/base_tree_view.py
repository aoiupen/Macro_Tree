from typing import List, Dict, Any, Protocol, TypeVar, runtime_checkable
from core.interfaces.base_tree import IMTTreeReadable
from viewmodel.interfaces.base_tree_viewmodel import IMTTreeViewModel

# 타입 변수 정의
T = TypeVar('T')

@runtime_checkable
class IMTTreeView(Protocol[T]):
    """트리 뷰 인터페이스"""
    
    def set_items(self, items: List[Dict[str, Any]]) -> None:
        """트리 아이템 설정"""
        ...
    
    def get_selected_items(self) -> List[str]:
        """선택된 아이템 ID 목록 반환"""
        ...
    
    def set_view_model(self, view_model: IMTTreeViewModel) -> None:
        """뷰 모델 설정"""
        ...
    
    def get_tree_readable(self) -> IMTTreeReadable[T]:
        """트리 읽기 인터페이스 가져오기"""
        ...
    
    # 다른 메서드들...
