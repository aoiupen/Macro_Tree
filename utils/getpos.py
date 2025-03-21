"""화면 위치 추적 위젯 모듈

이 모듈은 마우스 위치를 추적하고 표시하는 프레임 없는 위젯을 제공합니다.
"""
import os
import sys
from typing import Optional
from screeninfo import get_monitors
from PyQt6.QtGui import QPainter, QPen
from PyQt6.QtWidgets import QWidget, QLabel, QShortcut, QApplication, QGraphicsOpacityEffect
from PyQt6.QtCore import Qt, QPoint
import pynput
from pynput.mouse import Controller


class FramelessWidget(QWidget):
    """프레임이 없는 반투명 위젯
    
    마우스 위치를 추적하고 화면에 표시하는 위젯입니다.
    """

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        """FramelessWidget 생성자
        
        Args:
            parent: 부모 위젯 (기본값: None)
        """
        super(FramelessWidget, self).__init__(parent)
        self.setWindowTitle("Test")
        self.setWindowFlags(Qt.FramelessWindowHint)
        monitor = get_monitors()[0]
        self.resolution_width = monitor.width
        self.resolution_height = monitor.height
        
        self.label = QLabel("", self)
        self.offset: Optional[QPoint] = None
        self.quit_shortcut1 = QShortcut(QKeySequence('Ctrl+Q'), self)
        self.quit_shortcut1.activated.connect(self.self_close)
        self.quit_shortcut2 = QShortcut(QKeySequence('Ctrl+M'), self)
        self.quit_shortcut2.activated.connect(self.set_maximize)
        self.quit_shortcut3 = QShortcut(QKeySequence('Ctrl+S'), self)
        self.quit_shortcut3.activated.connect(self.set_minimize)
        
        opacity_effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(opacity_effect)
        self.setAutoFillBackground(True)
        self.setWindowOpacity(0.3)
        
        self.x = 0
        self.y = 0
        self.offset = QPoint(0, 0)

    def set_minimize(self) -> None:
        """윈도우를 최소화 상태로 설정합니다."""
        self.setGeometry(0, 0, 20, 20)
        self.setStyleSheet("background-color: yellow;")
        opacity_effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(opacity_effect)
        self.setAutoFillBackground(True)
        self.setWindowOpacity(1)

    def set_maximize(self) -> None:
        """윈도우를 최대화 상태로 설정합니다."""
        self.setGeometry(0, 0, self.resolution_width,
                        self.resolution_height - 100)
        self.setStyleSheet("background-color: white;")
        opacity_effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(opacity_effect)
        self.setAutoFillBackground(True)
        self.setWindowOpacity(0.1)

    def mousePressEvent(self, event: QMouseEvent) -> None:
        """마우스 클릭 이벤트 처리
        
        Args:
            event: 마우스 이벤트 객체
        """
        if event.button() == Qt.LeftButton:
            self.offset = event.pos()
            self.x = self.offset.x()
            self.y = self.offset.y()
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

    def paintEvent(self, event: QPaintEvent) -> None:
        """위젯 그리기 이벤트 처리
        
        Args:
            event: 페인트 이벤트 객체
        """
        painter = QPainter(self)
        painter.setPen(QPen(Qt.green, 8, Qt.SolidLine))
        painter.drawEllipse(self.offset, 40, 40)

    def self_close(self) -> None:
        """위젯을 닫습니다."""
        self.close()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FramelessWidget()
    window.setGeometry(300, 300, 300, 300)
    window.show()
    sys.exit(app.exec_())
