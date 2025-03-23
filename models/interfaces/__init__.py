"""모델 인터페이스 패키지

데이터 접근 계층에서 사용하는 인터페이스들을 정의합니다.
"""

from models.interfaces.repository_interface import ITreeDataRepository

__all__ = [
    'ITreeDataRepository'
] 