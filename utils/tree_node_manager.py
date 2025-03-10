"""트리 노드 관리 모듈

트리 노드를 효율적으로 관리하는 기능을 제공합니다.
"""
from typing import Dict, Optional, List
from PyQt5.QtWidgets import QTreeWidgetItem
from tree_widget_item import TreeWidgetItem


class TreeNodeManager:
    """트리 노드 관리 클래스
    
    트리 노드를 효율적으로 관리합니다.
    """
    
    def __init__(self) -> None:
        """TreeNodeManager 생성자"""
        self.node_map: Dict[str, TreeWidgetItem] = {}
    
    def register_node(self, node_id: str, item: TreeWidgetItem) -> None:
        """노드를 등록합니다.
        
        Args:
            node_id: 노드 ID
            item: 트리 위젯 아이템
        """
        self.node_map[node_id] = item
    
    def unregister_node(self, node_id: str) -> None:
        """노드 등록을 해제합니다.
        
        Args:
            node_id: 노드 ID
        """
        if node_id in self.node_map:
            del self.node_map[node_id]
    
    def get_node(self, node_id: str) -> Optional[TreeWidgetItem]:
        """노드를 가져옵니다.
        
        Args:
            node_id: 노드 ID
            
        Returns:
            트리 위젯 아이템 또는 None
        """
        return self.node_map.get(node_id)
    
    def clear(self) -> None:
        """모든 노드 등록을 해제합니다."""
        self.node_map.clear()
    
    def get_all_nodes(self) -> List[TreeWidgetItem]:
        """모든 노드를 가져옵니다.
        
        Returns:
            모든 트리 위젯 아이템 리스트
        """
        return list(self.node_map.values()) 