from typing import Any, Dict, List, TypedDict, TypeVar

from core.interfaces.base_item_action import IMTAction, IMTActionData, MTNode

class TreeItemData(TypedDict, total=False): # dict 의 value 값 검증을 위해 타입을 규정함
    """트리 아이템 데이터 구조 (total=False: 모든 필드 선택적)"""
    node_type: MTNode  # 노드 유형 (그룹/지시 등)
    name: str  # 아이템 이름
    parent_id: str | None  # 부모 아이템 ID
    children_ids: List[str]  # 자식 아이템 ID 목록
    action_type: IMTAction | None  # 액션 타입
    action_data: IMTActionData | None  # 액션 데이터

T = TypeVar('T')  # 제네릭 타입 변수 정의

class TreeItemKeys:
    """트리 아이템 속성 키 상수 정의
    
    이 클래스는 두 그룹으로 나뉩니다:
    1. TreeItemData 필드에 직접 매핑되는 키
    2. 추가적인 UI 및 기능 관련 키
    """
    # TreeItemData에 매핑되는 키
    NAME = "name"                # TreeItemData.name
    PARENT_ID = "parent_id"      # TreeItemData.parent_id
    CHILDREN = "children"        # TreeItemData.children_ids
    TYPE = "type"                # TreeItemData.node_type
    ACTION = "action"            # TreeItemData.action_type
    ACTION_DATA = "action_data"  # TreeItemData.action_data
    
    # 추가 기능 키 (TreeItemData에 직접 매핑되지 않음)
    ID = "id"
    DATA = "data"
    EXPANDED = "expanded"
    SELECTED = "selected"
    VISIBLE = "visible"
    ICON = "icon" 