"""커스텀 위젯 모듈

사용자 정의 위젯 컴포넌트들을 제공합니다.
"""
from typing import Optional, Tuple, Union
from PyQt5.QtWidgets import QPushButton, QLineEdit, QWidget, QGridLayout
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import pyqtSignal
from package.resources.resources import rsc
from package.db.tree_snapshot_manager import TreeSnapshotManager
from package.db.tree_db_dao import TreeDbDao
from package.db.tree_db import TreeDB

class InpTogBtn(QPushButton):
    """입력 토글 버튼 클래스
    
    입력 상태를 토글하는 버튼을 제공합니다.
    """
    
    inp_changed = pyqtSignal()

    def __init__(self, parent: QWidget, inp: str) -> None:
        """InpTogBtn 생성자
        
        Args:
            parent: 부모 위젯
            inp: 입력 상태 문자열
        """
        super().__init__()
        self.parent = parent
        self._inp = inp
        if (self._inp is not None and self._inp in rsc["inputs"] and 
            "icon" in rsc["inputs"][self._inp]):
            self.setFixedSize(30, 25)
            self.setIcon(QIcon(rsc["inputs"][self._inp]["icon"]))
            self.clicked.connect(self.inp_changed.emit)
        else:
            print(f"Warning: Invalid _inp value: {self._inp}, skipping icon setting.")

    @property
    def inp(self) -> str:
        """현재 입력 상태를 반환합니다."""
        return self._inp

    @inp.setter
    def inp(self, value: str) -> None:
        """입력 상태를 설정합니다.
        
        Args:
            value: 설정할 입력 상태 문자열
        """
        self._inp = value
        self.setIcon(QIcon(rsc["inputs"][self._inp]["icon"]))

class SubTogBtn(QPushButton):
    """하위 동작 토글 버튼 클래스
    
    하위 동작 상태를 토글하는 버튼을 제공합니다.
    """
    
    sub_changed = pyqtSignal()

    def __init__(self, parent: QWidget, inp: str, sub: str) -> None:
        """SubTogBtn 생성자
        
        Args:
            parent: 부모 위젯
            inp: 입력 상태 문자열
            sub: 하위 동작 상태 문자열
        """
        super().__init__()
        self.parent = parent
        self._sub = sub
        if (self._sub is not None and self._sub in rsc["subacts"] and 
            "icon" in rsc["subacts"][self._sub]):
            self.setFixedSize(30, 25)
            self.setIcon(QIcon(rsc["subacts"][self._sub]["icon"]))
            self.clicked.connect(self.sub_changed.emit)
        else:
            print(f"Warning: Invalid _sub value: {self._sub}, skipping icon setting.")

    @property
    def sub(self) -> str:
        """현재 하위 동작 상태를 반환합니다."""
        return self._sub

    @sub.setter
    def sub(self, value: str) -> None:
        """하위 동작 상태를 설정합니다.
        
        Args:
            value: 설정할 하위 동작 상태 문자열
        """
        self._sub = value
        self.setIcon(QIcon(rsc["subacts"][self._sub]["icon"]))

class PosWidget(QWidget):
    """위치 입력 위젯 클래스
    
    X, Y 좌표를 입력받는 위젯을 제공합니다.
    """
    
    position_changed = pyqtSignal(int, int)

    def __init__(self, x: Union[int, str], y: Union[int, str]) -> None:
        """PosWidget 생성자
        
        Args:
            x: X 좌표 값 또는 문자열
            y: Y 좌표 값 또는 문자열
        """
        super().__init__()
        self.x_edit = QLineEdit(str(x))
        self.y_edit = QLineEdit(str(y))
        layout = QGridLayout(self)
        layout.addWidget(self.x_edit, 0, 0)
        layout.addWidget(self.y_edit, 0, 1)

        self.x_edit.textChanged.connect(self.on_position_changed)
        self.y_edit.textChanged.connect(self.on_position_changed)

    def on_position_changed(self) -> None:
        """위치 값이 변경되었을 때 호출되는 메서드입니다."""
        try:
            x = int(self.x_edit.text())
            y = int(self.y_edit.text())
            self.position_changed.emit(x, y)
        except ValueError:
            pass  # 숫자가 아닌 값이 입력되었을 때 무시

    def get_position(self) -> Optional[Tuple[int, int]]:
        """현재 입력된 위치 값을 반환합니다.
        
        Returns:
            (x, y) 좌표 튜플 또는 None (잘못된 입력의 경우)
        """
        try:
            x = int(self.x_edit.text())
            y = int(self.y_edit.text())
            return x, y
        except ValueError:
            return None  # 숫자가 아닌 값이 입력되었을 때 None 반환

