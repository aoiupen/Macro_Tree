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
                [2]: 입력 타입
                [3]: 하위 동작 내용
                [4]: 하위 동작 타입
        """
        self.parent_id = row[0]
        self.name = row[1]
        self.inp = row[2]
        self.__sub_con = row[3]
        self.sub = row[4]
        self.typ = "G" if self.is_group() else "I"

    def is_group(self) -> bool:
        """아이템이 그룹인지 확인합니다.
        
        Returns:
            그룹 여부
        """
        return self.inp == ""

    def is_inst(self) -> bool:
        """아이템이 인스턴스인지 확인합니다.
        
        Returns:
            인스턴스 여부
        """
        return self.inp != ""

    @property
    def sub_con(self) -> str:
        """하위 동작 내용을 반환합니다.
        
        Returns:
            하위 동작 내용 또는 'Empty'
        """
        if self.__sub_con:
            return self.__sub_con
        return "Empty"

    @sub_con.setter
    def sub_con(self, value: str) -> None:
        """하위 동작 내용을 설정합니다.
        
        Args:
            value: 설정할 하위 동작 내용
        """
        self.__sub_con = value

    def toggle_input(self) -> None:
        """입력 타입을 토글합니다.
        
        'M'과 'K' 사이를 전환합니다.
        """
        if self.inp == "M":
            self.inp = "K"
        else:
            self.inp = "M"

    def toggle_subact(self) -> None:
        """하위 동작 타입을 토글합니다.
        
        입력 타입이 'M'인 경우: 'click'과 'double' 사이를 전환
        그 외의 경우: 'typing', 'copy', 'paste' 순으로 전환
        """
        if self.inp == "M":
            if self.sub == "click":
                self.sub = "double"
            else:
                self.sub = "click"
        else:
            if self.sub == "typing":
                self.sub = "copy"
            elif self.sub == "copy":
                self.sub = "paste"
            else:
                self.sub = "typing"