"""코어 패키지

애플리케이션의 핵심 비즈니스 로직과 도메인 모델을 포함합니다.
이 패키지는 플랫폼 독립적이며, 다른 UI 프레임워크나 환경에서도 재사용할 수 있습니다.
"""

from core.tree_state import TreeState

__all__ = ['TreeState'] 