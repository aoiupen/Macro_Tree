"""트리 위젯 아이템 로직 모듈

트리 위젯 아이템의 비즈니스 로직을 처리하는 클래스를 제공합니다.
"""
from typing import List, Union


class TreeWidgetItemLogic:
    """트리 위젯 아이템 로직 클래스
    
    트리 위젯 아이템의 상태와 동작을 관리합니다.
    """

    def __init__(self, row: List[str]) -> None:
        """TreeWidgetItemLogic 생성자
        
        Args:
            row: 아이템 데이터 리스트
                [0]: 부모 ID
                [1]: 이름
                [2]: 입력 타입 (M/K)
                [3]: 서브 액션
                [4]: 값
        """
        self.name = row[0] if row else ""
        self.inp = row[1] if len(row) > 1 else "M"
        self.sub_con_val = row[2] if len(row) > 2 else ""
        self.sub = row[3] if len(row) > 3 else "click"
        self.is_group_val = self.name.startswith("G:")
        self.is_inst_val = self.name.startswith("I:")
    
    def is_group(self) -> bool:
        """그룹 아이템인지 확인합니다.
        
        Returns:
            그룹 아이템 여부
        """
        return self.is_group_val
    
    def is_inst(self) -> bool:
        """인스턴스 아이템인지 확인합니다.
        
        Returns:
            인스턴스 아이템 여부
        """
        return self.is_inst_val
    
    @property
    def sub_con(self) -> str:
        """서브 액션 값을 반환합니다.
        
        Returns:
            서브 액션 값
        """
        return self.sub_con_val
    
    @sub_con.setter
    def sub_con(self, value: str) -> None:
        """서브 액션 값을 설정합니다.
        
        Args:
            value: 설정할 서브 액션 값
        """
        self.sub_con_val = value
    
    def toggle_input(self) -> None:
        """입력 타입을 토글합니다.
        
        M -> K -> M 순으로 변경됩니다.
        """
        if self.inp == "M":
            self.inp = "K"
            self.sub = "typing"
        else:
            self.inp = "M"
            self.sub = "click"
    
    def toggle_subact(self) -> None:
        """서브 액션을 토글합니다.
        
        입력 타입에 따라 다음 순서로 변경됩니다:
        - M: click -> double -> click
        - K: typing -> copy -> paste -> typing
        """
        if self.inp == "M":
            self.sub = "double" if self.sub == "click" else "click"
        else:  # self.inp == "K"
            if self.sub == "typing":
                self.sub = "copy"
            elif self.sub == "copy":
                self.sub = "paste"
            else:
                self.sub = "typing" 