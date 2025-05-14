# import os  # setWindowTitle에서만 필요하다면 해당 함수 내에서 import
from PyQt6.QtWidgets import QFileDialog, QMessageBox, QMenuBar
from PyQt6.QtGui import QAction
import os

class ExtTreeAppMixin:
    # 메뉴바 생성 및 파일 메뉴 구성
    def _create_menus(self):
        menubar = self.menuBar()
        file_menu = menubar.addMenu("파일")

        # --- 새로 만들기 액션 ---
        new_action = QAction("새로 만들기", self)
        new_action.setShortcut("Ctrl+N")
        new_action.triggered.connect(self._new_tree)
        file_menu.addAction(new_action)

        # --- 열기 액션 ---
        open_action = QAction("열기", self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self._open_file)
        file_menu.addAction(open_action)

        # --- 저장 액션 ---
        save_action = QAction("저장", self)
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self._save_file)
        file_menu.addAction(save_action)

        # --- 다른 이름으로 저장 액션 ---
        save_as_action = QAction("다른 이름으로 저장", self)
        save_as_action.setShortcut("Ctrl+Shift+S")
        save_as_action.triggered.connect(self._save_file_as)
        file_menu.addAction(save_as_action)

        file_menu.addSeparator()

        # --- 종료 액션 ---
        exit_action = QAction("종료", self)
        exit_action.setShortcut("Alt+F4")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

    # 새 트리 생성
    def _new_tree(self):
        self.tree = self.tree.__class__()
        self.viewmodel = self.viewmodel.__class__(self.tree)
        self.tree_view.set_viewmodel(self.viewmodel)
        self.current_file_path = ""
        self.setWindowTitle("Demo Tree Demo")

    # 파일 열기 다이얼로그 및 트리 로드
    def _open_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "트리 파일 열기", "", "JSON 파일 (*.json);;모든 파일 (*.*)"
        )
        if file_path:
            if self.viewmodel.load_tree(file_path):
                self.current_file_path = file_path
                self.setWindowTitle(f"Demo Tree Demo - {os.path.basename(file_path)}")
                self.tree_view.update_tree_items()
            else:
                QMessageBox.critical(self, "오류", "파일을 불러올 수 없습니다.")

    # 현재 파일 저장
    def _save_file(self):
        if not self.current_file_path:
            self._save_file_as()
        else:
            self._save_to_path(self.current_file_path)

    # 다른 이름으로 저장 다이얼로그
    def _save_file_as(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self, "트리 파일 저장", "", "JSON 파일 (*.json);;모든 파일 (*.*)"
        )
        if file_path:
            self._save_to_path(file_path)

    # 지정된 경로에 파일 저장
    def _save_to_path(self, file_path):
        if self.viewmodel.save_tree(file_path):
            self.current_file_path = file_path
            self.setWindowTitle(f"Demo Tree Demo - {os.path.basename(file_path)}")
        else:
            QMessageBox.critical(self, "오류", "파일을 저장할 수 없습니다.") 