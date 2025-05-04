# Macro_Tree

> [!NOTE]
> 이 프로젝트는 현재 리팩토링 및 구현 중이며, 아직 정상적인 운영을 위한 준비가 되어 있지 않습니다. 현재 데모 버전은 제공되지 않습니다.

트리 구조 기반 매크로 관리 애플리케이션입니다. 이 프로젝트는 실무 환경에서 생산성을 3배 향상시킨 자동화 프로그램에서 착안하여 보안 관련 요소를 제거하고 범용 컨셉으로 확장성과 유연성을 확보하였습니다.

*다른 언어로 읽기: [English](README.md)*

## 주요 기능
- 트리 노드 이동, 삽입, 삭제
- Undo, Redo
- 마우스 좌표 획득
- 그룹화 및 인스턴스 생성
- 데이터 영속성 (저장 및 불러오기)
- 계층 구조 시각화 및 조작

## 개발 상태
### 구현 완료된 기능
- MVVM 아키텍처 구현
- Protocol 기반 인터페이스 설계
- 인터페이스-구현체 분리를 통한 클린 아키텍처
- 트리 상태 관리 및 조작
- PyQt6 기반 사용자 인터페이스
- 다양한 구현체를 가진 데이터 저장소 레이어
- API 문서 생성 (pdoc3 활용)

### 진행 중인 기능
- 다크 테마
- 단축키 지원 (Ctrl+C, Ctrl+V)
- 매크로 실행 기능 확장
- 트리 노드 드래그앤드롭

## 기술 스택
- **백엔드:** Python 3.10
- **프론트엔드:** PyQt6
- **데이터 관리:** PostgreSQL
- **아키텍처:** MVVM 패턴
- **테스팅:** pytest
- **빌드 도구:** pyinstaller
- **주요 라이브러리:**
  - numpy, pandas
  - pynput (키보드/마우스 입력)
  - PyAutoGUI (자동화)
  - screeninfo (화면 정보)

## 아키텍처 개요
- **코어 모듈:** 
  - 코어 인터페이스(IMTTree, IMTTreeItem)와 구현체
  - 기본 트리 구조 및 핵심 데이터 타입
  - 기반 컴포넌트에 대한 추상 인터페이스
- **모델 레이어:** 
  - 비즈니스 로직 인터페이스와 구현체
  - 데이터 저장소, 상태 관리 및 액션 처리기
  - 도메인 특화 작업
- **뷰모델 레이어:** 모델과 뷰 레이어 간의 브릿지
- **뷰 레이어:** UI 컴포넌트 및 이벤트 처리
- **상태 관리:** 트리 상태 및 작업 추적

## 프로젝트 구조
```
├── core/                     # 핵심 비즈니스 로직
│   ├── interfaces/           # 코어 인터페이스
│   │   ├── base_tree.py      # 트리 인터페이스
│   │   ├── base_item.py      # 아이템 인터페이스
│   │   └── __init__.py       # 인터페이스 초기화
│   ├── impl/                 # 코어 구현체
│   │   ├── tree.py           # 트리 구현
│   │   ├── tree_item.py      # 트리 아이템 구현
│   │   └── __init__.py       # 구현체 초기화
│   ├── types/                # 타입 정의
│   │   └── item_types.py     # 아이템 타입 정의
│   └── __init__.py           # 코어 모듈 초기화
├── model/                    # 비즈니스 로직 계층
│   ├── repository/           # 저장소 구현체
│   │   ├── simple_tree_repository.py   # 파일 기반 저장소
│   │   ├── postgresql_tree_repository.py # 데이터베이스 저장소
│   │   └── __init__.py       # 저장소 초기화
│   ├── state/                # 상태 관리
│   │   ├── simple_tree_state_mgr.py    # 트리 상태 관리자
│   │   └── __init__.py       # 상태 관리 초기화
│   ├── action/               # 액션 처리
│   │   └── __init__.py       # 액션 모듈 초기화
│   ├── tree_repo.py          # 저장소 인터페이스
│   ├── tree_state_mgr.py     # 상태 관리자 인터페이스
│   └── __init__.py           # 모델 모듈 초기화
├── viewmodel/                # 뷰모델 계층
│   ├── implementations/      # 뷰모델 구현체
│   └── tree_viewmodel.py     # 트리 뷰모델 인터페이스
├── view/                     # 뷰 계층
│   ├── implementations/      # 뷰 구현체
│   ├── tree_bridge.py        # UI와 로직 사이의 브릿지
│   └── tree_view.py          # 트리 뷰 컴포넌트
├── docs/                     # API 문서
├── platform/                 # 플랫폼 특화 코드
├── test/                     # 테스트 모듈
├── examples/                 # 예제 구현
└── .venv/                    # 가상 환경
```

## 인터페이스 구조
- **코어 인터페이스:** 트리 및 아이템 컴포넌트의 기본 인터페이스
- **모델 인터페이스:** 비즈니스 로직 인터페이스 (저장소, 상태 관리자)
- **구현 클래스:** 인터페이스의 구체적인 구현체
- **TreeStateManager:** 트리 상태 추적 및 관리
- **TreeRepository:** 데이터 영속성 작업
- **TreeViewModel:** 트리 데이터를 위한 표현 로직
- **TreeView:** 사용자 인터페이스 컴포넌트

## 요구사항
- Python 3.10 이상
- 데이터 영속성을 위한 PostgreSQL
- Windows 운영체제 (현재 주로 Windows용으로 설계됨)

## 라이선스
이 프로젝트는 MIT 라이선스를 따릅니다 - 자세한 내용은 [LICENSE](LICENSE) 파일을 참조하세요.

## 데모
![main](https://user-images.githubusercontent.com/110750614/211150674-dfd5aa99-2ea1-47f3-839d-2494f83ab985.gif)
(과거 레거시 코드 기반의 데모 영상입니다) 