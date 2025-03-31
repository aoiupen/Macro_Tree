"""아이템 뷰모델 인터페이스 모듈

아이템 뷰모델의 인터페이스를 정의합니다.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from .viewmodel_base_interface import IViewModel


class IItemViewModel(IViewModel):
    """아이템 뷰모델 인터페이스
    
    트리 아이템 뷰모델의 인터페이스를 정의합니다.
    """
    
    @property
    @abstractmethod
    def name(self) -> str:
        """아이템 이름"""
        pass
    
    @name.setter
    @abstractmethod
    def name(self, value: str) -> None:
        """아이템 이름 설정"""
        pass
    
    @property
    @abstractmethod
    def inp(self) -> str:
        """입력 타입"""
        pass
    
    @inp.setter
    @abstractmethod
    def inp(self, value: str) -> None:
        """입력 타입 설정"""
        pass
    
    @property
    @abstractmethod
    def sub_con(self) -> str:
        """하위 연결"""
        pass
    
    @sub_con.setter
    @abstractmethod
    def sub_con(self, value: str) -> None:
        """하위 연결 설정"""
        pass
    
    @property
    @abstractmethod
    def sub(self) -> str:
        """하위 액션"""
        pass
    
    @sub.setter
    @abstractmethod
    def sub(self, value: str) -> None:
        """하위 액션 설정"""
        pass
    
    @property
    @abstractmethod
    def expanded(self) -> bool:
        """확장 상태"""
        pass
    
    @expanded.setter
    @abstractmethod
    def expanded(self, value: bool) -> None:
        """확장 상태 설정"""
        pass
    
    @property
    @abstractmethod
    def id(self) -> str:
        """아이템 ID"""
        pass
    
    @property
    @abstractmethod
    def parentId(self) -> str:
        """부모 아이템 ID"""
        pass
    
    @property
    @abstractmethod
    def childrenIds(self) -> List[str]:
        """자식 아이템 ID 목록"""
        pass
    
    @abstractmethod
    def getNextInputType(self) -> str:
        """다음 입력 타입을 반환합니다."""
        pass
    
    @abstractmethod
    def getSubActions(self, input_type: str) -> List[str]:
        """입력 타입에 따른 하위 액션 목록을 반환합니다."""
        pass
    
    @abstractmethod
    def toggleInputType(self) -> bool:
        """입력 타입을 토글합니다."""
        pass
    
    @abstractmethod
    def updateFromDict(self, data_dict: Dict[str, Any]) -> None:
        """딕셔너리로부터 데이터를 업데이트합니다."""
        pass
    
    @abstractmethod
    def toDict(self) -> Dict[str, Any]:
        """현재 데이터를 딕셔너리로 변환합니다."""
        pass
    
    @abstractmethod
    def is_group(self) -> bool:
        """그룹 아이템 여부를 반환합니다."""
        pass
    
    @abstractmethod
    def is_inst(self) -> bool:
        """인스턴스 아이템 여부를 반환합니다."""
        pass 