"""
매크로 트리 모델 패키지

이 패키지는 핵심 도메인 모델을 확장하는 서비스들을 제공합니다.
"""

# 영속성 관련 API
from model.persistence.interfaces.base_tree_repository import IMTTreeRepository
from model.persistence.impl.file_tree_repository import MTFileTreeRepository

# 이벤트 관련 API
from model.events.interfaces.base_tree_event_mgr import IMTTreeEventHandler
from model.events.impl.tree_event_manager import MTTreeEventManager 