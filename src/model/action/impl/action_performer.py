from core.interfaces.base_item_data import IMTActionPerformer, IMTMouseActionData, IMTKeyboardActionData

class MouseClickPerformer(IMTActionPerformer):
    def perform(self, action_data: IMTMouseActionData) -> None:
        print(f"[더미] 마우스 클릭 액션 실행: {action_data}")

class KeyboardTypePerformer(IMTActionPerformer):
    def perform(self, action_data: IMTKeyboardActionData) -> None:
        print(f"[더미] 키보드 입력 액션 실행: {action_data}")