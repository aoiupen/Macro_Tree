"""트리 데이터 구조 모듈

트리 상태를 표현하는 데이터 클래스를 제공합니다.
"""
from dataclasses import dataclass
from typing import Dict, List, Any, Optional
import json
import copy


@dataclass
class TreeState:
    """트리 상태 데이터 클래스
    
    트리의 노드와 구조 정보를 저장합니다.
    """
    
    nodes: Dict[str, Dict[str, Any]]
    """노드 정보를 저장하는 딕셔너리
    
    키: 노드 ID
    값: 노드 속성 딕셔너리
    """
    
    structure: Dict[str, List[str]]
    """트리 구조 정보를 저장하는 딕셔너리
    
    키: 부모 노드 ID
    값: 자식 노드 ID 리스트
    """
    
    def __init__(self, items: List[Dict[str, Any]] = None):
        self.items = items or []
    
    def to_dict(self) -> Dict[str, Any]:
        """상태를 딕셔너리로 변환"""
        return {
            "items": copy.deepcopy(self.items),
            "version": "1.0"
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TreeState':
        """딕셔너리에서 상태 객체 생성"""
        return cls(items=copy.deepcopy(data.get("items", [])))
    
    def to_json(self) -> str:
        """JSON 문자열로 직렬화"""
        return json.dumps(self.to_dict())
    
    @classmethod
    def from_json(cls, json_str: str) -> 'TreeState':
        """JSON 문자열에서 상태 객체 생성"""
        return cls.from_dict(json.loads(json_str))
    
    def apply_changes(self, changes: Dict[str, Any]) -> 'TreeState':
        """변경 사항을 적용한 새 상태 반환"""
        # 변경 사항만 적용하는 로직 구현
        new_state = copy.deepcopy(self)
        # 변경 로직 적용...
        return new_state 