"""
이 모듈은 트리 아이템의 속성 키 상수를 정의합니다.
"""

class DomainKeys:
    """트리 아이템의 도메인 속성 키 상수"""
    DOMAIN = "domain"
    NAME = "name"
    PARENT_ID = "parent_id"
    CHILDREN = "children_ids"
    NODE_TYPE = "node_type"
    DEVICE = "device"
    ACTION = "action"
    ACTION_DATA = "action_data"

class UIStateKeys:
    """트리 아이템의 UI 상태/확장/부가 속성 키 상수"""
    UI_STATE = "ui_state"
    EXPANDED = "expanded"
    SELECTED = "selected"
    VISIBLE = "visible"
    ICON = "icon"