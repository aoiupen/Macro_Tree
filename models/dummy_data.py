# models/dummy_data.py
from typing import Dict, List, Any
from dataclasses import dataclass, field

@dataclass
class TreeState:
    nodes: Dict[int, Dict[str, Any]] = field(default_factory=dict)
    structure: Dict[int, List[int]] = field(default_factory=dict)

# 애플리케이션 초기 실행 시 사용할 기본 더미 데이터
DEFAULT_TREE_STATE = TreeState(
    nodes={
        1: {"parent_id": None, "name": "Root", "inp": "keyboard", "sub_con": 2, "sub": "action", "type": "folder"},
        2: {"parent_id": 1, "name": "Documents", "inp": "keyboard", "sub_con": 1, "sub": "menu", "type": "folder"},
        3: {"parent_id": 1, "name": "Pictures", "inp": "mouse", "sub_con": 0, "sub": "dialog", "type": "folder"},
        4: {"parent_id": 2, "name": "Report.docx", "inp": "keyboard", "sub_con": 3, "sub": "action", "type": "file"},
        5: {"parent_id": 2, "name": "Budget.xlsx", "inp": "keyboard", "sub_con": 2, "sub": "notification", "type": "file"},
        6: {"parent_id": 3, "name": "Vacation.jpg", "inp": "touch", "sub_con": 1, "sub": "dialog", "type": "file"},
        7: {"parent_id": 3, "name": "Family", "inp": "mouse", "sub_con": 0, "sub": "menu", "type": "folder"},
        8: {"parent_id": 7, "name": "Birthday.png", "inp": "gamepad", "sub_con": 2, "sub": "action", "type": "file"}
    },
    structure={
        1: [2, 3],
        2: [4, 5],
        3: [6, 7],
        4: [],
        5: [],
        6: [],
        7: [8],
        8: []
    }
)

# 테스트용 더미 데이터 (다양한 시나리오 테스트를 위한 데이터)
TEST_TREE_STATES = {
    # 1. 단일 노드 트리 (엣지 케이스)
    "single_node": TreeState(
        nodes={
            1: {"parent_id": None, "name": "Root", "inp": "keyboard", "sub_con": 0, "sub": "action", "type": "folder"}
        },
        structure={
            1: []
        }
    ),
    
    # 2. 깊은 트리 (최대 깊이 테스트)
    "deep_tree": TreeState(
        nodes={
            1: {"parent_id": None, "name": "Root", "inp": "keyboard", "sub_con": 0, "sub": "action", "type": "folder"},
            2: {"parent_id": 1, "name": "Level 1", "inp": "keyboard", "sub_con": 1, "sub": "menu", "type": "folder"},
            3: {"parent_id": 2, "name": "Level 2", "inp": "mouse", "sub_con": 2, "sub": "dialog", "type": "folder"},
            4: {"parent_id": 3, "name": "Level 3", "inp": "touch", "sub_con": 3, "sub": "notification", "type": "file"}
        },
        structure={
            1: [2],
            2: [3],
            3: [4],
            4: []
        }
    ),
    
    # 3. 넓은 트리 (많은 자식 노드 테스트)
    "wide_tree": TreeState(
        nodes={
            1: {"parent_id": None, "name": "Root", "inp": "keyboard", "sub_con": 0, "sub": "action", "type": "folder"},
            2: {"parent_id": 1, "name": "Child 1", "inp": "keyboard", "sub_con": 1, "sub": "menu", "type": "file"},
            3: {"parent_id": 1, "name": "Child 2", "inp": "mouse", "sub_con": 2, "sub": "dialog", "type": "file"},
            4: {"parent_id": 1, "name": "Child 3", "inp": "touch", "sub_con": 3, "sub": "notification", "type": "file"},
            5: {"parent_id": 1, "name": "Child 4", "inp": "gamepad", "sub_con": 0, "sub": "action", "type": "file"},
            6: {"parent_id": 1, "name": "Child 5", "inp": "keyboard", "sub_con": 1, "sub": "menu", "type": "file"},
            7: {"parent_id": 1, "name": "Child 6", "inp": "mouse", "sub_con": 2, "sub": "dialog", "type": "file"},
            8: {"parent_id": 1, "name": "Child 7", "inp": "touch", "sub_con": 3, "sub": "notification", "type": "file"}
        },
        structure={
            1: [2, 3, 4, 5, 6, 7, 8],
            2: [], 3: [], 4: [], 5: [], 6: [], 7: [], 8: []
        }
    )
}

# 간편한 접근을 위한 함수
def get_default_tree() -> TreeState:
    """기본 트리 상태를 반환합니다."""
    return DEFAULT_TREE_STATE

def get_test_tree(scenario: str = "default") -> TreeState:
    """특정 테스트 시나리오에 대한 트리 상태를 반환합니다.
    
    Args:
        scenario: 테스트 시나리오 이름 ("single_node", "deep_tree", "wide_tree")
        
    Returns:
        요청된 시나리오의 트리 상태 또는 기본 트리 상태
    """
    return TEST_TREE_STATES.get(scenario, DEFAULT_TREE_STATE)