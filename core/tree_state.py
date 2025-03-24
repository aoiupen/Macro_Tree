"""트리 상태 모듈

트리의 상태를 나타내는 클래스를 제공합니다.
"""
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
import json
import copy


@dataclass
class TreeNodeState:
    """트리 노드의 상태를 나타내는 클래스"""
    id: str
    text: str
    description: str = ""
    parent_id: Optional[str] = None
    children_ids: List[str] = field(default_factory=list)
    expanded: bool = False
    data: Dict[str, Any] = field(default_factory=dict)


class TreeState:
    """트리의 전체 상태를 나타내는 클래스
    
    트리의 모든 노드와 그들의 관계, 상태를 저장합니다.
    """
    
    def __init__(self, nodes: Dict[str, Dict[str, Any]] = None, structure: Dict[str, List[str]] = None):
        """TreeState 생성자
        
        Args:
            nodes: 노드 정보 딕셔너리 (선택적)
            structure: 구조 정보 딕셔너리 (선택적)
        """
        self.nodes = nodes or {}
        self.structure = structure or {}
        self._node_states: Dict[str, TreeNodeState] = {}
        
        # 노드 상태 초기화 (호환성 유지)
        if nodes and structure:
            self._init_node_states()
    
    def _init_node_states(self):
        """노드 상태를 초기화합니다."""
        for node_id, node_data in self.nodes.items():
            parent_id = node_data.get('parent_id')
            node_state = TreeNodeState(
                id=node_id,
                text=node_data.get('name', ''),
                description=node_data.get('sub_con', ''),
                parent_id=parent_id,
                data=node_data
            )
            self._node_states[node_id] = node_state
            
            # 자식 ID 설정
            if parent_id in self.structure:
                children = self.structure.get(node_id, [])
                node_state.children_ids = children
    
    @property
    def root_id(self) -> Optional[str]:
        """루트 노드의 ID를 반환합니다."""
        if None in self.structure and self.structure[None]:
            return self.structure[None][0]
        return None
    
    @root_id.setter
    def root_id(self, value: str):
        """루트 노드의 ID를 설정합니다."""
        if None not in self.structure:
            self.structure[None] = []
        if value not in self.structure[None]:
            self.structure[None] = [value]
    
    def add_node(self, node: TreeNodeState):
        """노드를 추가합니다.
        
        Args:
            node: 추가할 노드 상태
        """
        # 노드 상태 저장
        self._node_states[node.id] = node
        
        # 노드 정보 저장 (호환성 유지)
        self.nodes[node.id] = node.data or {
            'name': node.text,
            'sub_con': node.description,
            'parent_id': node.parent_id
        }
        
        # 구조 정보 저장 (호환성 유지)
        parent_id = node.parent_id
        if parent_id not in self.structure:
            self.structure[parent_id] = []
        if node.id not in self.structure[parent_id]:
            self.structure[parent_id].append(node.id)
    
    def get_node(self, node_id: str) -> Optional[TreeNodeState]:
        """지정된 ID의 노드를 반환합니다.
        
        Args:
            node_id: 노드 ID
            
        Returns:
            노드 상태. 없으면 None
        """
        return self._node_states.get(node_id)
    
    def get_all_nodes(self) -> Dict[str, TreeNodeState]:
        """모든 노드를 반환합니다.
        
        Returns:
            노드 ID를 키로 하는 노드 상태 딕셔너리
        """
        return self._node_states.copy()
    
    def clear(self):
        """모든 노드를 제거합니다."""
        self.nodes.clear()
        self.structure.clear()
        self._node_states.clear()
    
    def clone(self) -> 'TreeState':
        """현재 트리 상태의 복제본을 생성합니다.
        
        Returns:
            복제된 TreeState 객체
        """
        cloned_nodes = copy.deepcopy(self.nodes)
        cloned_structure = copy.deepcopy(self.structure)
        return TreeState(cloned_nodes, cloned_structure)
    
    def serialize_to_json(self) -> str:
        """트리 상태를 JSON 문자열로 직렬화합니다.
        
        Returns:
            JSON 형식의 트리 상태 문자열
        """
        data = {
            "nodes": copy.deepcopy(self.nodes),
            "structure": copy.deepcopy(self.structure),
            "version": "1.0"
        }
        return json.dumps(data)
    
    @classmethod
    def deserialize_from_json(cls, json_str: str) -> 'TreeState':
        """JSON 문자열에서 트리 상태를 역직렬화하여 생성합니다.
        
        Args:
            json_str: 트리 상태 정보가 담긴 JSON 문자열
            
        Returns:
            생성된 TreeState 인스턴스
        """
        data = json.loads(json_str)
        return cls(
            nodes=copy.deepcopy(data.get("nodes", {})),
            structure=copy.deepcopy(data.get("structure", {}))
        ) 