import os
import shutil
import re

# 소스 코드 기준 폴더 구조 매핑 (필요에 따라 추가/수정)
FOLDER_MAP = {
    "core_impl":      "core/impl",
    "core_interfaces": "core/interfaces",
    "core":           "core",
    "model_store_repo_interfaces": "model/store/repo/interfaces",
    "model_store_repo": "model/store/repo",
    "model_store":    "model/store",
    "model":          "model",
    "viewmodel":      "viewmodel",
    "view":           "view",
    "platforms":      "platforms",
    "debug":          "debug",
}

# 테스트 파일명 패턴 예시: test_core_impl_tree.py → core/impl
def get_target_subdir(filename):
    # 예: test_core_impl_tree.py → core_impl
    m = re.match(r"test_([a-zA-Z0-9_]+)_", filename)
    if m:
        key = m.group(1)
        return FOLDER_MAP.get(key)
    # 예: test_tree_state_mgr.py 등은 직접 분류 필요
    return None

def main():
    tests_dir = "tests"
    for fname in os.listdir(tests_dir):
        fpath = os.path.join(tests_dir, fname)
        if not os.path.isfile(fpath) or not fname.startswith("test_") or not fname.endswith(".py"):
            continue
        target_subdir = get_target_subdir(fname)
        if target_subdir:
            dest_dir = os.path.join(tests_dir, target_subdir)
            os.makedirs(dest_dir, exist_ok=True)
            dest_path = os.path.join(dest_dir, fname)
            print(f"Moving {fname} → {dest_path}")
            shutil.move(fpath, dest_path)
        else:
            print(f"SKIP: {fname} (분류 불가, 수동 확인 필요)")

if __name__ == "__main__":
    main()
