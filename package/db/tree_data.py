from dataclasses import dataclass
from typing import Dict, List

@dataclass
class TreeState:
    nodes: Dict[int, Dict]
    structure: Dict[int, List[int]]