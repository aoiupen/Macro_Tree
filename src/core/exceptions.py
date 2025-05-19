"""
이 모듈은 매크로 트리(MTTree)에서 사용하는 예외 클래스를 정의합니다.
"""

class MTTreeError(Exception):
    """MTTree 관련 기본 예외 클래스입니다."""
    pass

class MTTreeItemNotFoundError(MTTreeError):
    """트리 아이템을 찾을 수 없을 때 발생하는 예외입니다."""
    pass

class MTTreeItemAlreadyExistsError(MTTreeError):
    """트리 아이템이 이미 존재할 때 발생하는 예외입니다."""
    pass

class InvalidMTTreeItemDataError(MTTreeError):
    """트리 아이템 데이터가 유효하지 않을 때 발생하는 예외입니다."""
    pass

# 필요에 따라 예외 클래스를 추가로 정의할 수 있습니다. 