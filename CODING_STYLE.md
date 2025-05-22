# 코딩 스타일 가이드

이 문서는 프로젝트의 코딩 스타일 규칙을 정의합니다.

## 명명 규칙

- **클래스**: PascalCase 사용 (예: `TreeWidget`, `DatabaseConnection`)
- **함수/메서드**: snake_case 사용 (예: `load_from_db`, `find_item_by_node_id`)
- **변수**: snake_case 사용 (예: `tree_state`, `node_id`)
- **상수**: UPPER_CASE 사용 (예: `MAX_SNAPSHOTS`, `DEFAULT_PORT`)

## 데이터/트리 구조 네이밍 및 타입 가이드라인

- **트리/아이템 ID**
  - 트리의 고유 식별자는 `tree_id`로 통일
  - 아이템의 고유 식별자는 `item_id`로 통일 (DTO, dict key, 함수 인자/반환값 등 모두)
- **부모/자식**
  - 부모 ID는 항상 `parent_id`로 사용
  - 이동/변경 등에서만 `new_parent_id`, `old_parent_id` 등 구분
- **자식 목록**
  - 자식 아이템의 ID 목록은 `children_ids: List[str]`
  - 자식 아이템 객체 목록은 `children: List[MTItemDTO]`
- **아이템 딕셔너리**
  - 전체 아이템 dict는 `items: Dict[str, MTItemDTO]`
- **DTO/트리 아이템**
  - 데이터 전달/직렬화/계층 간 통신에는 `MTItemDTO`를 사용
  - 내부 트리 로직에서만 필요한 경우에만 `MTItem` 사용
  - 가능하면 외부 계층(ViewModel, View, Store 등)에서는 `MTItemDTO`만 사용
- **함수/메서드 시그니처**
  - 인자/반환형/타입 힌트 모두 위 네이밍/타입을 일관되게 사용
- **내부 변수 연속 접근**
  - `self._tree._items[item_id]`와 같은 패턴은 메서드(`get_item(item_id)`, `get_children(parent_id)` 등)로 추출하여 사용

## 상태 표현 (State Representation)

- **트리 상태 (Tree State)**: `MTTree.to_dict()` 메서드가 반환하는 딕셔너리로 표현됩니다. 이 딕셔너리는 Undo/Redo 스택 및 파일 저장 시 사용됩니다.
  - 타입 힌트로는 `Dict[str, Any]`를 기본으로 사용하되, 좀 더 구체적인 표현을 위해 다음과 같은 `TypedDict` 구조를 참조할 수 있습니다 (실제 코드에 TypedDict를 필수로 정의하지 않아도 됨):
    ```python
    # 예시 TypedDict 구조 (참고용)
    # class ItemDict(TypedDict):
    #     item_id: str
    #     domain_data: Dict[str, Any] # MTItemDomainDTO.to_dict()의 결과
    #     ui_state_data: Dict[str, Any] # MTItemUIStateDTO.to_dict()의 결과
    # 
    # class TreeStateDict(TypedDict):
    #     id: str # Tree ID
    #     name: str
    #     root_id: str | None
    #     items: Dict[str, ItemDict]
    ```

## 들여쓰기 및 공백

- 들여쓰기는 4칸 공백 사용
- 연산자 앞뒤에 공백 추가 (예: `a + b`, `x = 1`)
- 콤마 뒤에 공백 추가 (예: `func(a, b, c)`)
- 함수 정의와 호출 시 괄호 앞에 공백 없음 (예: `def func():`, `func()`)

## 주석

- 모든 모듈, 클래스, 함수에 문서 문자열(docstring) 추가
- 문서 문자열은 한글로 작성
- 복잡한 로직에는 인라인 주석 추가

## 임포트

- 표준 라이브러리, 서드파티 라이브러리, 로컬 모듈 순으로 그룹화
- 각 그룹 사이에 빈 줄 추가
- 알파벳 순으로 정렬

## 예외 처리

- 구체적인 예외 타입 사용 (예: `except ValueError:` 대신 `except (ValueError, TypeError):`)
- 빈 `except:` 블록 사용 금지
- 예외 메시지는 명확하게 작성

## 타입 힌트

- 모든 함수와 메서드에 타입 힌트 추가
- 복잡한 타입은 `typing` 모듈 사용 (예: `List[int]`, `Dict[str, Any]`)
- Optional 타입은 Union 타입(|) 사용 (예: `str | None` 대신 `Optional[str]`)