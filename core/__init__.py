"""
매크로 트리 코어 패키지

이 패키지는 매크로 트리의 핵심 도메인 모델과 인터페이스를 제공합니다.
"""

# 인터페이스 - 주요 공개 API
from core.interfaces.base_tree import IMTTree, IMTTreeData, IMTTreeModifiable, IMTTreeTraversable
from core.interfaces.base_item import IMTTreeItem, IMTBaseItem
from core.interfaces.base_item_action import IMTAction, MTDevice, MTTreeEvent

# 기본 구현체 - 편의성을 위해 제한적으로 노출
from core.impl.tree import MTTree
from core.impl.item import MTTreeItem
from core.impl.item_action import MTMouseAction, MTKeyboardAction