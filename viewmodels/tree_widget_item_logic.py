"""트리 위젯 아이템 로직 모듈

트리 위젯 아이템의 데이터와 상태를 관리하는 클래스를 제공합니다.
"""
from typing import List, TypeVar, Generic, Optional
from dataclasses import dataclass

# 순환 리스트 클래스 정의
T = TypeVar('T')

class CyclicList(Generic[T]):
    """순환 리스트 클래스
    
    리스트의 요소를 순환적으로 접근할 수 있는 기능을 제공합니다.
    이 클래스는 여러 값을 순차적으로 순환해야 하는 경우 코드를 간결하게 유지하는 데 도움이 됩니다.
    """
    
    def __init__(self, items: List[T]):
        """CyclicList 생성자
        
        Args:
            items: 순환할 아이템 목록
        """
        self.items = items
    
    def next(self, current: T) -> T:
        """현재 아이템의 다음 아이템을 반환합니다.
        
        Args:
            current: 현재 아이템
            
        Returns:
            다음 아이템. 현재 아이템이 목록에 없으면 첫 번째 아이템 반환
        """
        try:
            idx = self.items.index(current)
            return self.items[(idx + 1) % len(self.items)]
        except (ValueError, IndexError):
            # 목록이 비어있거나 현재 아이템이 목록에 없는 경우
            return self.items[0] if self.items else current


@dataclass
class TreeItemData:
    """트리 아이템 데이터 클래스
    
    트리 위젯 아이템의 데이터를 저장합니다.
    불변성을 보장하기 위해 데이터 클래스로 구현되었습니다.
    """
    name: str = ""
    inp: str = "M"
    sub: str = "M_click"
    sub_con: str = ""
    
    @property
    def is_group(self) -> bool:
        """그룹 아이템인지 확인합니다."""
        return self.name.startswith("G:")
    
    @property
    def is_inst(self) -> bool:
        """인스턴스 아이템인지 확인합니다."""
        return self.name.startswith("I:")


class TreeWidgetItemViewModel:
    """트리 위젯 아이템 뷰모델 클래스
    
    트리 위젯 아이템의 상태와 데이터를 관리합니다.
    상태 변경 시 새로운 객체를 생성하는 불변 방식으로 구현되었습니다.
    """
    # 입력 타입에 따른 서브 액션 목록 (클래스 변수로 정의)
    _M_ACTIONS = CyclicList(["M_click", "M_double"])
    _K_ACTIONS = CyclicList(["K_typing", "K_copy", "K_paste"])
    
    # 입력 타입 목록 (현재는 2개지만 확장성과 통일성을 위해 순환 리스트 사용)
    _INPUT_ACTIONS = CyclicList(["M", "K"])

    def __init__(self, row: List[str] = None, data: TreeItemData = None) -> None:
        """TreeWidgetItemViewModel 생성자
        
        Args:
            row: 아이템 데이터 리스트 (data가 None인 경우에만 사용)
                [0]: 이름
                [1]: 입력 타입 (M/K)
                [2]: 서브 액션 값
                [3]: 서브 액션
            data: TreeItemData 객체 (우선적으로 사용)
        """
        if data is not None:
            self.data = data
        else:
            row = row or []
            name = row[0] if row else ""
            inp = row[1] if len(row) > 1 else "M"
            sub_con = row[2] if len(row) > 2 else ""
            
            # 서브 액션 값 설정
            sub = row[3] if len(row) > 3 else "M_click"
            
            self.data = TreeItemData(
                name=name,
                inp=inp,
                sub=sub,
                sub_con=sub_con
            )
    
    @property
    def name(self) -> str:
        return self.data.name
    
    @property
    def inp(self) -> str:
        return self.data.inp
    
    @property
    def sub(self) -> str:
        return self.data.sub
    
    @property
    def sub_con(self) -> str:
        return self.data.sub_con
    
    @sub_con.setter
    def sub_con(self, value: str) -> None:
        # 불변 객체 패턴에서는 setter가 새 객체를 생성해야 하지만,
        # 기존 코드와의 호환성을 위해 예외적으로 직접 수정 허용
        # 실제 프로덕션 코드에서는 새 객체를 반환하는 방식으로 변경 권장
        self.data = TreeItemData(
            name=self.data.name,
            inp=self.data.inp,
            sub=self.data.sub,
            sub_con=value
        )
    
    def is_group(self) -> bool:
        """그룹 아이템인지 확인합니다.
        
        Returns:
            그룹 아이템 여부
        """
        return self.data.is_group
    
    def is_inst(self) -> bool:
        """인스턴스 아이템인지 확인합니다.
        
        Returns:
            인스턴스 아이템 여부
        """
        return self.data.is_inst
    
    def toggle_input(self) -> 'TreeWidgetItemViewModel':
        """입력 타입을 토글합니다.
        
        M -> K -> M 순으로 변경됩니다.
        순환 리스트를 사용하여 확장성과 일관성을 보장합니다.
        
        Returns:
            새로운 TreeWidgetItemViewModel 인스턴스
        """
        # 다음 입력 타입 가져오기
        next_inp = self._INPUT_ACTIONS.next(self.data.inp)
        
        # 새 입력 타입의 기본 서브 액션 설정
        default_sub = "M_click" if next_inp == "M" else "K_typing"
        
        # 새 데이터 객체 생성
        new_data = TreeItemData(
            name=self.data.name,
            inp=next_inp,
            sub=default_sub,
            sub_con=self.data.sub_con
        )
        
        return TreeWidgetItemViewModel(data=new_data)
    
    def toggle_sub(self) -> 'TreeWidgetItemViewModel':
        """서브 액션을 토글합니다.
        
        입력 타입에 따라 다음 순서로 변경됩니다:
        - M: M_click -> M_double -> M_click
        - K: K_typing -> K_copy -> K_paste -> K_typing
        
        순환 리스트를 사용하여 코드를 간결하게 유지합니다.
        
        Returns:
            새로운 TreeWidgetItemViewModel 인스턴스
        """
        if self.data.inp == "M":
            next_sub = self._M_ACTIONS.next(self.data.sub)
        elif self.data.inp == "K":
            next_sub = self._K_ACTIONS.next(self.data.sub)
        else:
            next_sub = self.data.sub
        
        # 새 데이터 객체 생성
        new_data = TreeItemData(
            name=self.data.name,
            inp=self.data.inp,
            sub=next_sub,
            sub_con=self.data.sub_con
        )
        
        return TreeWidgetItemViewModel(data=new_data) 