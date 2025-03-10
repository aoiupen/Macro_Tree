"""트리 데이터 구조 모듈

트리 상태를 표현하는 데이터 클래스를 제공합니다.
"""
from dataclasses import dataclass
from typing import Dict, List, Any


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