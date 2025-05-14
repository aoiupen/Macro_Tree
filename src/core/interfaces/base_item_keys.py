class DataKeys:
    """트리 아이템의 속성 키 상수 (도메인 + UI/확장)"""
    # 도메인 속성 키
    ID = "id"
    NAME = "name"
    PARENT_ID = "parent_id"
    CHILDREN = "children_ids"
    NODE_TYPE = "node_type"
    DEVICE = "device"
    ACTION = "action"
    ACTION_DATA = "action_data"

class UIKeys:
    """트리 아이템의 UI/확장/부가 속성 키 상수"""
    DATA = "data"
    EXPANDED = "expanded"
    SELECTED = "selected"
    VISIBLE = "visible"
    ICON = "icon"