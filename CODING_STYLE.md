# 코딩 스타일 가이드

이 문서는 프로젝트의 코딩 스타일 규칙을 정의합니다.

## 명명 규칙

- **클래스**: PascalCase 사용 (예: `TreeWidget`, `DatabaseConnection`)
- **함수/메서드**: snake_case 사용 (예: `load_from_db`, `find_item_by_node_id`)
- **변수**: snake_case 사용 (예: `tree_state`, `node_id`)
- **상수**: UPPER_CASE 사용 (예: `MAX_SNAPSHOTS`, `DEFAULT_PORT`)

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