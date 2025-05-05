from core.interfaces.base_types import IMTPoint

class MTPoint(IMTPoint):
    def __init__(self, x: int, y: int):
        self._x = x
        self._y = y

    @property
    def x(self) -> int:
        return self._x

    @property
    def y(self) -> int:
        return self._y

    def clone(self) -> 'MTPoint':
        return MTPoint(self._x, self._y)