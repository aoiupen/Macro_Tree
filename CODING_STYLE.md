# 코딩 스타일 가이드

이 문서는 프로젝트의 코딩 스타일 규칙을 정의합니다.

## 명명 규칙

- **클래스**: PascalCase 사용 (예: `TreeWidget`, `DatabaseConnection`)
- **함수/메서드**: snake_case 사용 (예: `load_from_db`, `find_item_by_node_id`)
- **변수**: snake_case 사용 (예: `tree_state`, `node_id`)
- **상수**: UPPER_CASE 사용 (예: `MAX_SNAPSHOTS`, `DEFAULT_PORT`)

### 메서드 네이밍 일관성

- **Public 메서드**: 간결하고 명확한 동작 표현
  - `get_item()`, `add_item()`, `remove_item()`
- **Private 메서드**: 언더스코어 prefix 사용
  - `_notify_event()`, `_check_circular_reference()`
- **Helper 메서드**: 목적을 명확히 표현
  - `_add_to_parent()`, `_remove_from_parent()`

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

## 주석 및 문서화

### Docstring 스타일
- **간결성 우선**: 한 줄로 핵심 기능을 명확히 표현
- **자연스러운 표현**: AI 스타일의 과도한 Args/Returns 문서 지양
- **한글 사용**: 모든 docstring은 한글로 작성
- **원칙**: 모든 함수/메서드는 한 줄 요약 docstring만 작성 (예외는 아래 참고)
- **예외**: 복잡한 함수(파라미터 4개 이상, 반환값이 복잡, 부작용/예외가 중요한 경우)나 공개 API에 한해 한 줄 요약 + 한두 줄 추가 설명 허용
- **공개 API/라이브러리**: 외부 문서화가 중요한 경우에만 Sphinx 스타일(Args/Returns/Raises) 부분 허용

#### 권장 스타일
```python
# 좋은 예시
def add_item(self, item_dto: MTItemDTO) -> str | None:
    """아이템을 트리에 추가하고 ID를 반환합니다."""

def get_children(self, parent_id: str | None) -> List[IMTItem]:
    """부모의 자식 아이템들을 가져옵니다."""

# 복잡한 로직/공개 API인 경우만 추가 설명
def move_item(self, item_id: str, new_parent_id: str | None = None) -> bool:
    """아이템을 다른 부모로 이동시킵니다.
    
    순환 참조를 검사하고 부모-자식 관계를 업데이트합니다.
    """
```

#### 지양해야 할 스타일
```python
# 과도한 AI 스타일 - 지양
def add_item(self, item_dto: MTItemDTO, index: int = -1) -> str | None:
    """
    트리에 아이템을 추가합니다.
    Args:
        item_dto (MTItemDTO): 새 아이템 DTO (domain_data.parent_id로 부모 지정)
        index (int): 자식 목록에 삽입할 위치, -1이면 맨 뒤
    Returns:
        str | None: 생성된 아이템 ID 또는 실패 시 None
    Raises:
        MTItemNotFoundError: 부모 아이템이 존재하지 않을 때
    """
```

### 인라인 주석
- 복잡한 로직에만 필요시 추가
- 코드가 명확하면 주석 생략
- 변수명과 메서드명이 의미를 충분히 전달하도록 네이밍에 집중

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