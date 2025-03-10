# utils/tree_generator.py
import random
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field

@dataclass
class TreeState:
    nodes: Dict[int, Dict[str, Any]] = field(default_factory=dict)
    structure: Dict[int, List[int]] = field(default_factory=dict)

def generate_random_tree(
    node_count: int = 10, 
    max_depth: int = 3,
    max_children_per_node: int = 5,
    input_types: List[str] = None,
    sub_types: List[str] = None
) -> TreeState:
    """랜덤한 트리 구조를 생성합니다.
    
    Args:
        node_count: 생성할 노드 수
        max_depth: 최대 트리 깊이 (1-3)
        max_children_per_node: 노드당 최대 자식 수
        input_types: 가능한 입력 타입 목록
        sub_types: 가능한 서브 타입 목록
        
    Returns:
        생성된 랜덤 트리 상태
    """
    if input_types is None:
        input_types = ["keyboard", "mouse", "gamepad", "touch"]
    
    if sub_types is None:
        sub_types = ["action", "menu", "dialog", "notification"]
    
    # 최대 깊이 제한
    max_depth = min(max(1, max_depth), 3)
    
    tree_state = TreeState()
    
    # 루트 노드 생성
    root_id = 1
    tree_state.nodes[root_id] = {
        "parent_id": None,
        "name": "Root",
        "inp": random.choice(input_types),
        "sub_con": random.randint(0, 3),
        "sub": random.choice(sub_types),
        "type": "folder"  # 루트는 항상 폴더 타입
    }
    tree_state.structure[root_id] = []
    
    # 남은 노드 수
    remaining_nodes = node_count - 1
    if remaining_nodes <= 0:
        return tree_state
    
    # 각 레벨에 노드 할당 (레벨이 깊어질수록 노드 수 감소)
    level_nodes = []
    if max_depth == 1:
        level_nodes = [remaining_nodes]
    elif max_depth == 2:
        level1_nodes = min(remaining_nodes, random.randint(2, max(2, remaining_nodes - 2)))
        level_nodes = [level1_nodes, remaining_nodes - level1_nodes]
    else:  # max_depth == 3
        level1_nodes = min(remaining_nodes, random.randint(2, max(2, remaining_nodes - 4)))
        remaining_after_level1 = remaining_nodes - level1_nodes
        level2_nodes = min(remaining_after_level1, random.randint(2, max(2, remaining_after_level1 - 2)))
        level_nodes = [level1_nodes, level2_nodes, remaining_after_level1 - level2_nodes]
    
    # 현재 레벨의 노드들 (다음 레벨의 부모가 될 노드들)
    current_level_nodes = [root_id]
    next_node_id = 2
    
    # 각 레벨에 노드 생성
    for level, nodes_to_create in enumerate(level_nodes):
        if nodes_to_create <= 0 or not current_level_nodes:
            break
            
        next_level_nodes = []
        
        # 현재 레벨의 각 노드에 자식 노드 분배
        nodes_per_parent = max(1, nodes_to_create // len(current_level_nodes))
        extra_nodes = nodes_to_create % len(current_level_nodes)
        
        for parent_id in current_level_nodes:
            # 이 부모에게 할당할 자식 노드 수
            children_for_this_parent = nodes_per_parent
            if extra_nodes > 0:
                children_for_this_parent += 1
                extra_nodes -= 1
                
            # 이미 할당된 자식 수 확인
            existing_children = len(tree_state.structure[parent_id])
            available_slots = max(0, max_children_per_node - existing_children)
            children_for_this_parent = min(children_for_this_parent, available_slots)
            
            # 자식 노드 생성
            for _ in range(children_for_this_parent):
                if next_node_id > node_count:
                    break
                    
                # 마지막 레벨이거나 랜덤하게 파일 타입 결정
                is_file = (level == max_depth - 1) or (random.random() < 0.3)
                node_type = "file" if is_file else "folder"
                
                # 노드 생성
                tree_state.nodes[next_node_id] = {
                    "parent_id": parent_id,
                    "name": f"Node {next_node_id}",
                    "inp": random.choice(input_types),
                    "sub_con": random.randint(0, 3),
                    "sub": random.choice(sub_types),
                    "type": node_type
                }
                
                # 구조 업데이트
                tree_state.structure[parent_id].append(next_node_id)
                tree_state.structure[next_node_id] = []
                
                # 폴더 타입인 경우 다음 레벨의 부모 후보에 추가
                if node_type == "folder":
                    next_level_nodes.append(next_node_id)
                    
                next_node_id += 1
                
        # 다음 레벨의 부모 노드 업데이트
        current_level_nodes = next_level_nodes
    
    return tree_state

def generate_balanced_tree(
    depth: int = 2,
    children_per_node: int = 3,
    input_types: List[str] = None,
    sub_types: List[str] = None
) -> TreeState:
    """균형 잡힌 트리 구조를 생성합니다.
    
    Args:
        depth: 트리 깊이 (1-3)
        children_per_node: 각 노드의 자식 수
        input_types: 가능한 입력 타입 목록
        sub_types: 가능한 서브 타입 목록
        
    Returns:
        생성된 균형 트리 상태
    """
    # 최대 깊이 제한
    depth = min(max(1, depth), 3)
    
    # 총 노드 수 계산 (완전 트리)
    total_nodes = sum(children_per_node ** i for i in range(depth + 1))
    
    return generate_random_tree(
        node_count=total_nodes,
        max_depth=depth,
        max_children_per_node=children_per_node,
        input_types=input_types,
        sub_types=sub_types
    )