# models/dummy_data.py
from typing import Dict, List, Any
from dataclasses import dataclass, field
from core.tree_state import TreeState

# 애플리케이션 초기 실행 시 사용할 기본 더미 데이터
def get_default_tree() -> TreeState:
    """기본 트리 상태를 반환합니다."""
    nodes = {
        "1": {"parent_id": None, "name": "Root", "inp": "keyboard", "sub_con": "2", "sub": "action"},
        "2": {"parent_id": "1", "name": "Documents", "inp": "keyboard", "sub_con": "1", "sub": "menu"},
        "3": {"parent_id": "1", "name": "Pictures", "inp": "mouse", "sub_con": "0", "sub": "dialog"},
        "4": {"parent_id": "2", "name": "Report.docx", "inp": "keyboard", "sub_con": "3", "sub": "action"},
        "5": {"parent_id": "2", "name": "Budget.xlsx", "inp": "keyboard", "sub_con": "2", "sub": "notification"},
        "6": {"parent_id": "3", "name": "Vacation.jpg", "inp": "touch", "sub_con": "1", "sub": "dialog"},
        "7": {"parent_id": "3", "name": "Family", "inp": "mouse", "sub_con": "0", "sub": "menu"},
        "8": {"parent_id": "7", "name": "Birthday.png", "inp": "gamepad", "sub_con": "2", "sub": "action"}
    }
    
    structure = {
        None: ["1"],
        "1": ["2", "3"],
        "2": ["4", "5"],
        "3": ["6", "7"],
        "4": [],
        "5": [],
        "6": [],
        "7": ["8"],
        "8": []
    }
    
    return TreeState(nodes, structure)

# 테스트용 더미 데이터 함수
def get_test_tree(scenario: str = "default") -> TreeState:
    """특정 테스트 시나리오에 대한 트리 상태를 반환합니다.
    
    Args:
        scenario: 테스트 시나리오 이름 ("single_node", "deep_tree", "wide_tree")
        
    Returns:
        요청된 시나리오의 트리 상태 또는 기본 트리 상태
    """
    if scenario == "single_node":
        nodes = {
            "1": {"parent_id": None, "name": "Root", "inp": "keyboard", "sub_con": "0", "sub": "action"}
        }
        structure = {
            None: ["1"],
            "1": []
        }
        return TreeState(nodes, structure)
    
    elif scenario == "deep_tree":
        nodes = {
            "1": {"parent_id": None, "name": "Root", "inp": "keyboard", "sub_con": "0", "sub": "action"},
            "2": {"parent_id": "1", "name": "Level 1", "inp": "keyboard", "sub_con": "1", "sub": "menu"},
            "3": {"parent_id": "2", "name": "Level 2", "inp": "mouse", "sub_con": "2", "sub": "dialog"}
        }
        structure = {
            None: ["1"],
            "1": ["2"],
            "2": ["3"],
            "3": []
        }
        return TreeState(nodes, structure)
    
    # 기본 트리 반환
    return get_default_tree()