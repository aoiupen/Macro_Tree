"""위치 선택 윈도우 모듈

마우스 위치를 선택하고 추적하는 윈도우를 제공합니다.
"""
from typing import Dict, List, Callable, Optional
from PyQt6.QtWidgets import (
    QWidget, QGraphicsOpacityEffect
)
from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtGui import QPainter, QPen, QMouseEvent, QPaintEvent, QShortcut, QGuiApplication, QAction
from view.components import compo as cp

# screeninfo 모듈 가져오기 시도
try:
    from screeninfo import get_monitors
    USE_SCREENINFO = True
except ImportError:
    USE_SCREENINFO = False


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
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setStyleSheet("background-color: rgba(0, 0, 0, 0);")
        
        # 화면 크기 설정
        if USE_SCREENINFO:
            monitor = get_monitors()[0]
            self.screen_width = monitor.width
            self.screen_height = monitor.height
        else:
            # PyQt의 QDesktopWidget 사용
            screen = QGuiApplication.primaryScreen()
            screen_geometry = screen.geometry()
            self.screen_width = screen_geometry.width()
            self.screen_height = screen_geometry.height()
            
        self.setGeometry(0, 0, self.screen_width, self.screen_height)
        
        # 마우스 추적 변수
        self.tracking = False
        self.mouse_pos = QPoint(0, 0)
        
        # 단축키 설정
        self.esc_shortcut = QShortcut(Qt.Key.Key_Escape, self)
        self.esc_shortcut.activated.connect(self.close_window)
        
        # 투명도 효과
        self.opacity_effect = QGraphicsOpacityEffect()
        self.opacity_effect.setOpacity(0.5)
        self.setGraphicsEffect(self.opacity_effect)
        
        # 최소화 상태로 시작
        self.minimize_window()
        
        # 윈도우 표시
        self.show()

    def minimize_window(self) -> None:
        """윈도우를 최소화합니다."""
        self.setGeometry(0, 0, 1, 1)

    def maximize_window(self) -> None:
        """윈도우를 최대화합니다."""
        # 화면 크기 업데이트
        if USE_SCREENINFO:
            monitor = get_monitors()[0]
            self.screen_width = monitor.width
            self.screen_height = monitor.height
        else:
            # PyQt의 QDesktopWidget 사용
            screen = QGuiApplication.primaryScreen()
            screen_geometry = screen.geometry()
            self.screen_width = screen_geometry.width()
            self.screen_height = screen_geometry.height()
        
        # 전체 화면으로 설정
        self.setGeometry(0, 0, self.screen_width, self.screen_height)
        self.activateWindow()

    def mousePressEvent(self, event: QMouseEvent) -> None:
        """마우스 클릭 이벤트를 처리합니다.
        
        Args:
            event: 마우스 이벤트 객체
        """
        if event.button() == Qt.MouseButton.LeftButton:
            self.tracking = True
            self.mouse_pos = event.pos()
            
            # 좌표 업데이트
            if hasattr(self.pos_widget, 'update_position'):
                self.pos_widget.update_position(self.mouse_pos.x(), self.mouse_pos.y())
            
            # 좌표 문자열 업데이트
            if hasattr(self.pos_widget, 'coor_str'):
                self.pos_widget.coor_str = f"{self.mouse_pos.x()},{self.mouse_pos.y()}"
            
            # 좌표 표시 업데이트
            if hasattr(self.pos_widget, 'coor_x_edit') and hasattr(self.pos_widget, 'coor_y_edit'):
                self.pos_widget.coor_x_edit.setText(str(self.mouse_pos.x()))
                self.pos_widget.coor_y_edit.setText(str(self.mouse_pos.y()))
            
            self.update()

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        """마우스 이동 이벤트를 처리합니다.
        
        Args:
            event: 마우스 이벤트 객체
        """
        if self.tracking:
            self.mouse_pos = event.pos()
            
            # 좌표 업데이트
            if hasattr(self.pos_widget, 'update_position'):
                self.pos_widget.update_position(self.mouse_pos.x(), self.mouse_pos.y())
            
            self.update()

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        """마우스 버튼 해제 이벤트를 처리합니다.
        
        Args:
            event: 마우스 이벤트 객체
        """
        if event.button() == Qt.MouseButton.LeftButton:
            self.tracking = False
            self.close_window()

    def close_window(self) -> None:
        """윈도우를 닫습니다."""
        self.hide()
        self.minimize_window()

    def paintEvent(self, event: QPaintEvent) -> None:
        """그리기 이벤트를 처리합니다.
        
        Args:
            event: 그리기 이벤트 객체
        """
        painter = QPainter(self)
        painter.setPen(QPen(Qt.GlobalColor.red, 2))
        
        # 십자선 그리기
        if self.tracking:
            painter.drawLine(self.mouse_pos.x(), 0, self.mouse_pos.x(), self.screen_height)
            painter.drawLine(0, self.mouse_pos.y(), self.screen_width, self.mouse_pos.y())

    def center_window(self):
        qr = self.frameGeometry()
        cp = QGuiApplication.primaryScreen().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def get_dpi(self):
        dpi = QGuiApplication.primaryScreen().physicalDotsPerInchX()
        return dpi

# 모든 화면 목록 얻기
screens = QGuiApplication.screens()

# 기본 화면(주 모니터) 정보 얻기
primary_screen = QGuiApplication.primaryScreen()

# 특정 화면의 크기 정보
for i, screen in enumerate(screens):
    print(f"Screen {i}: {screen.name()}")
    print(f" - Size: {screen.size().width()}x{screen.size().height()}")
    print(f" - Available geometry: {screen.availableGeometry().width()}x{screen.availableGeometry().height()}") 