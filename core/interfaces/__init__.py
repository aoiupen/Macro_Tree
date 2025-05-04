"""인터페이스 정의 패키지"""

# * import 대신 명시적 import로 수정
from core.interfaces.base_item import IMTTreeItem, IMTBaseItem
from core.interfaces.base_tree import IMTTree, IMTTreeData, IMTTreeModifiable, IMTTreeTraversable

# 이동된 모듈 참조
from model.action.interfaces import MTNode, MTDevice, MTKeyState, IMTAction, IMTPoint, IMTActionData 