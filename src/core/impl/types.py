from core.interfaces.base_types import IMTPoint
from typing import Optional
from core.interfaces.base_tree import IMTTreeItem
from core.interfaces.base_item_data import MTItemDomainDTO

"""
이 모듈은 트리에서 사용하는 좌표(Point) 타입의 구현을 제공합니다.
"""

class MTPoint(IMTPoint):
    """
    2차원 좌표를 나타내는 클래스입니다.
    """
    def __init__(self, x: int, y: int):
        """
        MTPoint 인스턴스를 초기화합니다.
        Args:
            x (int): X 좌표
            y (int): Y 좌표
        """
        self._x = x
        self._y = y

    @property
    def x(self) -> int:
        """
        X 좌표를 반환합니다.
        Returns:
            int: X 좌표
        """
        return self._x

    @property
    def y(self) -> int:
        """
        Y 좌표를 반환합니다.
        Returns:
            int: Y 좌표
        """
        return self._y

    def clone(self) -> 'MTPoint':
        """
        현재 좌표의 복제본을 반환합니다.
        Returns:
            MTPoint: 복제된 좌표 객체
        """
        return MTPoint(self._x, self._y)