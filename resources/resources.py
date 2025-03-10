import os
from utils.config_manager import ConfigManager

# ConfigManager를 사용하여 프로젝트 루트 경로 가져오기
config = ConfigManager()
PROJECT_ROOT = config.get("paths", "project_root", ".")

rsc = {
    "header": ["Name", "M/K", "Value", "Act", ""],
    "win_geo": [100, 100, 500, 400],
    "inputs": {
        "M": {"icon": os.path.join(PROJECT_ROOT, "src", "mouse.png"), "subacts": ["click", "double"]},
        "K": {"icon": os.path.join(PROJECT_ROOT, "src", "key.png"), "subacts": ["typing", "copy", "paste"]},
    },
    "coor": {"icon": os.path.join(PROJECT_ROOT, "src", "coor.png")},
    "subacts": {
        "click": {"icon": os.path.join(PROJECT_ROOT, "src", "click.png")},
        "double": {"icon": os.path.join(PROJECT_ROOT, "src", "double.png")},
        "typing": {"icon": os.path.join(PROJECT_ROOT, "src", "typing.png")},
        "copy": {"icon": os.path.join(PROJECT_ROOT, "src", "copy.png")},
        "paste": {"icon": os.path.join(PROJECT_ROOT, "src", "paste.png")},
        "all": {"icon": os.path.join(PROJECT_ROOT, "src", "all.png")},
    },
    "tree_icons": {
        "G": {"icon": os.path.join(PROJECT_ROOT, "src", "group.png")},
        "I": {"icon": os.path.join(PROJECT_ROOT, "src", "inst.png")},
    },
}

def get_resources():
    return rsc

# 리소스 경로 유효성 검사 (선택 사항)
for key, value in rsc.items():
    if isinstance(value, dict):
        if "icon" in value and not os.path.exists(value["icon"]):
            print(f"Warning: Resource file '{value['icon']}' does not exist.")
    elif isinstance(value, dict):
        for sub_key, sub_value in value.items():
            if isinstance(sub_value, dict) and "icon" in sub_value and not os.path.exists(sub_value["icon"]):
                print(f"Warning: Resource file '{sub_value['icon']}' does not exist.") 