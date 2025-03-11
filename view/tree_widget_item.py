"""트리 위젯 아이템 모듈

트리 위젯의 각 아이템을 관리하는 클래스를 제공합니다.
"""
from typing import Optional, Union
from PyQt5.QtWidgets import QTreeWidgetItem, QLineEdit, QLabel, QTreeWidget
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt
from viewmodels.tree_widget_item_viewmodel import TreeWidgetItemViewModel
from view.components.compo import InpTogBtn, SubTogBtn, PosWidget
from resources.resources import rsc
import json


class TreeWidgetItem(QTreeWidgetItem):
    """트리 위젯의 아이템을 관리하는 클래스
    
    각 아이템의 상태와 동작을 처리합니다.
    """

    def __init__(self, tree_widget: QTreeWidget, parent: Optional[QTreeWidgetItem] = None, 
                 row: str = "", view_model: Optional[TreeWidgetItemViewModel] = None) -> None:
        """TreeWidgetItem 생성자
        
        Args:
            tree_widget: 트리 위젯 인스턴스
            parent: 부모 아이템 (선택적)
            row: 아이템 데이터 리스트 (view_model이 None인 경우에만 사용)
            view_model: TreeWidgetItemViewModel 인스턴스 (우선적으로 사용)
        """
        super().__init__(parent)
        self.tree_widget = tree_widget
        
        # 뷰모델 객체 생성 또는 사용
        if view_model is not None:
            self.logic = view_model
        else:
            self.logic = TreeWidgetItemViewModel(row)
        
        # 아이템 텍스트 설정
        self.setText(0, self.logic.name)
        
        # 아이콘 설정
        if self.logic.is_group():
            self.setIcon(0, QIcon(rsc["tree_icons"]["G"]["icon"]))
        elif self.logic.is_inst():
            self.setIcon(0, QIcon(rsc["tree_icons"]["I"]["icon"]))
        
        # 입력 타입 토글 버튼 설정
        self.inp_btn = InpTogBtn(self, self.logic.inp)
        self.inp_btn.signal.connect(self.toggle_input)
        tree_widget.setItemWidget(self, 1, self.inp_btn)
        
        # 서브 액션 값 위젯 설정
        if self.logic.inp == "M":
            self.pos_widget = PosWidget(0, 0)
            tree_widget.setItemWidget(self, 2, self.pos_widget)
        else:
            self.text_edit = QLineEdit(self.logic.sub_con)
            self.text_edit.textChanged.connect(self.update_sub_con)
            tree_widget.setItemWidget(self, 2, self.text_edit)
        
        # 서브 액션 토글 버튼 설정
        self.sub_btn = SubTogBtn(self, self.logic.inp, self.logic.sub)
        self.sub_btn.signal.connect(self.toggle_sub)
        tree_widget.setItemWidget(self, 3, self.sub_btn)
    
    def toggle_input(self) -> None:
        """입력 타입을 토글합니다."""
        # 로직 객체의 입력 타입 토글 (새 인스턴스 반환)
        self.logic = self.logic.toggle_input()
        
        # 버튼 아이콘 업데이트
        self.inp_btn.cur = self.logic.inp
        self.inp_btn.setIcon(QIcon(rsc[self.logic.inp]["icon"]))
        
        # 서브 액션 값 위젯 변경
        if self.logic.inp == "M":
            # 키보드 -> 마우스로 변경
            self.tree_widget.removeItemWidget(self, 2)
            self.pos_widget = PosWidget(0, 0)
            self.tree_widget.setItemWidget(self, 2, self.pos_widget)
        else:
            # 마우스 -> 키보드로 변경
            self.tree_widget.removeItemWidget(self, 2)
            self.text_edit = QLineEdit("")
            self.text_edit.textChanged.connect(self.update_sub_con)
            self.tree_widget.setItemWidget(self, 2, self.text_edit)
        
        # 서브 액션 버튼 업데이트
        self.tree_widget.removeItemWidget(self, 3)
        self.sub_btn = SubTogBtn(self, self.logic.inp, self.logic.sub)
        self.sub_btn.signal.connect(self.toggle_sub)
        self.tree_widget.setItemWidget(self, 3, self.sub_btn)
    
    def toggle_sub(self) -> None:
        """서브 액션을 토글합니다."""
        # 로직 객체의 서브 액션 토글 (새 인스턴스 반환)
        self.logic = self.logic.toggle_sub()
        
        # 버튼 아이콘 업데이트
        self.sub_btn.cur = self.logic.sub
        self.sub_btn.setIcon(QIcon(rsc["subacts"][self.logic.sub]["icon"]))
    
    def update_sub_con(self, text: str) -> None:
        """서브 액션 값을 업데이트합니다.
        
        Args:
            text: 새로운 서브 액션 값
        """
        self.logic.sub_con = text

    def to_json(self) -> str:
        return json.dumps({'nodes': self.nodes, 'structure': self.structure})
    
    @classmethod
    def from_json(cls, json_str: str) -> 'TreeState':
        data = json.loads(json_str)
        return cls(data['nodes'], data['structure'])

    def save_to_file(self, filename: str) -> None:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(self.to_json())
    
    @classmethod
    def load_from_file(cls, filename: str) -> 'TreeState':
        with open(filename, 'r', encoding='utf-8') as f:
            return cls.from_json(f.read())

    # 향후 확장을 위한 인터페이스 준비
    def export_data(self) -> str:
        """데이터를 내보내기 위한 JSON 문자열 반환"""
        return self.to_json()
    
    @classmethod
    def import_data(cls, data_str: str) -> 'TreeState':
        """JSON 문자열에서 데이터 가져오기"""
        return cls.from_json(data_str) 