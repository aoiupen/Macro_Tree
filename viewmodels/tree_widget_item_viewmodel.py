"""트리 위젯 아이템 뷰모델 모듈

트리 위젯 아이템의 데이터와 상태를 관리하는 클래스를 제공합니다.
"""
from typing import List, Union


class TreeWidgetItemViewModel:
    """트리 위젯 아이템 뷰모델 클래스
    
    트리 위젯 아이템의 상태와 데이터를 관리합니다.
    """

    def __init__(self, row: List[str]) -> None:
        """TreeWidgetItemViewModel 생성자
        
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
        
        # 서브 액션 값 설정 (접두사 추가)
        sub_value = row[3] if len(row) > 3 else "click"
        if sub_value.startswith("M_") or sub_value.startswith("K_"):
            self.sub = sub_value
        else:
            # 기존 값에 접두사 추가
            default_inp = self.inp
            if default_inp == "M" and not sub_value.startswith("M_"):
                self.sub = f"M_{sub_value}"
            elif default_inp == "K" and not sub_value.startswith("K_"):
                self.sub = f"K_{sub_value}"
            else:
                self.sub = sub_value
                
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
            value: 설정할 값
        """
        self.sub_con_val = value
    
    def toggle_input(self) -> None:
        """입력 타입을 토글합니다."""
        if self.inp == "M":
            self.inp = "K"
            self.sub = "K_typing"
        else:
            self.inp = "M"
            self.sub = "M_click"
    
    def toggle_sub(self) -> None:
        """서브 액션을 토글합니다."""
        if self.inp == "M":
            self.sub = "M_double" if self.sub == "M_click" else "M_click"
        elif self.inp == "K":
            if self.sub == "K_typing":
                self.sub = "K_copy"
            elif self.sub == "K_copy":
                self.sub = "K_paste"
            else:
                self.sub = "K_typing" 