import os
from utils.config_manager import ConfigManager

# ConfigManager를 사용하여 프로젝트 루트 경로 가져오기
config = ConfigManager()
PROJECT_ROOT = config.get("paths", "project_root", ".")

rsc = {
    "header": ["Name", "M/K", "Value", "Act", ""],
    "win_geo": [100, 100, 500, 400],
    "inputs": {
        "M": {"icon": os.path.join(PROJECT_ROOT, "resources", "icons", "mouse.png"), "subacts": ["click", "double"]},
        "K": {"icon": os.path.join(PROJECT_ROOT, "resources", "icons", "key.png"), "subacts": ["typing", "copy", "paste"]},
    },
    "input": ["M", "K"],  # 이터레이터로 사용할 리스트
    "coor": {"icon": os.path.join(PROJECT_ROOT, "resources", "icons", "coor.png")},
    "subacts": {
        "click": {"icon": os.path.join(PROJECT_ROOT, "resources", "icons", "click.png")},
        "double": {"icon": os.path.join(PROJECT_ROOT, "resources", "icons", "double.png")},
        "typing": {"icon": os.path.join(PROJECT_ROOT, "resources", "icons", "typing.png")},
        "copy": {"icon": os.path.join(PROJECT_ROOT, "resources", "icons", "copy.png")},
        "paste": {"icon": os.path.join(PROJECT_ROOT, "resources", "icons", "paste.png")},
        "all": {"icon": os.path.join(PROJECT_ROOT, "resources", "icons", "all.png")},
    },
    "tree_icons": {
        "G": {"icon": os.path.join(PROJECT_ROOT, "resources", "icons", "group.png")},
        "I": {"icon": os.path.join(PROJECT_ROOT, "resources", "icons", "inst.png")},
    },
    "M": {"icon": os.path.join(PROJECT_ROOT, "resources", "icons", "mouse.png")},
    "K": {"icon": os.path.join(PROJECT_ROOT, "resources", "icons", "key.png")},
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