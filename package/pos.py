"""위치 선택 윈도우 모듈

마우스 위치를 선택하고 추적하는 윈도우를 제공합니다.
"""
from typing import Dict, List, Callable, Optional
from PyQt5.QtWidgets import (
    QWidget, QShortcut, QGraphicsOpacityEffect
)
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtGui import QPainter, QPen, QMouseEvent, QPaintEvent
from package.components import compo as cp
from screeninfo import get_monitors


class PosWin(QWidget):
    """위치 선택 윈도우 클래스
    
    마우스 위치를 선택하고 추적하는 프레임 없는 윈도우를 제공합니다.
    """

    def __init__(self, pos_widget: QWidget) -> None:
        """PosWin 생성자
        
        Args:
            pos_widget: 위치 정보를 표시할 위젯
        """
        super().__init__()
        self.pos_widget = pos_widget
        self.setWindowFlags(Qt.FramelessWindowHint)  # Frame 없는 Window
        self.monitor_num = 0  # 0번 모니터
        self.monitor = get_monitors()[self.monitor_num]
        self.max_width = self.monitor.width
        self.max_height = self.monitor.height
        self.min_width = 20
        self.min_height = 20
        
        # 단축키 설정
        self.shortcut_info_dict: Dict[str, Callable[[], None]] = {
            'ESC': self.close_window,
            'Ctrl+M': self.maximize_window,
            'Ctrl+S': self.minimize_window
        }
        
        self.shortcut_list: List[QShortcut] = []
        for key_sequence, shortcut_func in self.shortcut_info_dict.items():
            shortcut = QShortcut(QKeySequence(key_sequence), self)
            shortcut.activated.connect(shortcut_func)
            self.shortcut_list.append(shortcut)
        
        # 투명도와 배경색 설정
        effect = QGraphicsOpacityEffect(self)
        alpha = 0.1
        self.setGraphicsEffect(effect)
        self.setAutoFillBackground(True)
        self.setWindowOpacity(alpha)
        
        # 윈도우 최대화 및 버튼 설정
        self.maximize_window()
        
        # 마우스 이벤트 처리를 위한 변수
        self.offset: Optional[QPoint] = None
        
    def minimize_window(self) -> None:
        """윈도우를 최소화 상태로 설정합니다."""
        self.setGeometry(0, 0, self.min_width, self.min_height)
 
    def maximize_window(self) -> None:
        """윈도우를 최대화 상태로 설정합니다."""
        self.setGeometry(0, 0, self.max_width, self.max_height)

    # pos -> treewidgetitem에 저장
    # pos, coor, val 간 naming 기준 필요 : coor_x_val, coor_x_str 로 
    # format : "{상징},{상징}".format(상징=설명,상징=설명)
    # poswidget과 PosWinwin간 변수 통일 필요
    
    def mousePressEvent(self, event: QMouseEvent) -> None:
        """마우스 클릭 이벤트 처리
        
        Args:
            event: 마우스 이벤트 객체
        """
        if event.button() == Qt.LeftButton:
            coord_x = event.pos().x()
            coord_y = event.pos().y()
            coord_str = f"{coord_x},{coord_y}"
            
            if isinstance(self.pos_widget.coord_btn, cp.PosBtn):
                self.pos_widget.coord_btn.pos = coord_str
                self.pos_widget.coord_x_edit.setText(str(coord_x))
                self.pos_widget.coord_y_edit.setText(str(coord_y))
                self.close()
            else:
                self.coord_btn.coord_list.append(coord_str)
                if len(self.coord_btn.coord_list) == 2:
                    self.coord_btn.coord_list.clear()
                    self.close()
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        """마우스 이동 이벤트 처리
        
        Args:
            event: 마우스 이벤트 객체
        """
        if self.offset is not None and event.buttons() == Qt.LeftButton:
            self.move(self.pos() + event.pos() - self.offset)
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        """마우스 버튼 해제 이벤트 처리
        
        Args:
            event: 마우스 이벤트 객체
        """
        self.offset = None
        super().mouseReleaseEvent(event)

    def close_window(self) -> None:
        """윈도우를 닫습니다."""
        self.close()
        
    # move to getpos.py later
    def paintEvent(self, event: QPaintEvent) -> None:
        """위젯 그리기 이벤트 처리
        
        Args:
            event: 페인트 이벤트 객체
        """
        painter = QPainter(self)
        painter.setPen(QPen(Qt.green, 8, Qt.SolidLine))
        painter.drawEllipse(40, 40, 40, 40)
        return
        
