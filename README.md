# Macro_Tree

트리 구조 기반 매크로 관리 애플리케이션

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
- 트리 상태 관리 및 조작
- QML 기반 사용자 인터페이스
- 데이터 저장소 레이어

### 진행 중인 기능
- 다크 테마
- 단축키 지원 (Ctrl+C, Ctrl+V)
- 매크로 실행 기능 확장
- 트리 노드 드래그앤드롭

## 기술 스택
- **백엔드:** Python 3.8+
- **프론트엔드:** PyQt6, QML
- **데이터 관리:** PostgreSQL (선택적)
- **아키텍처:** MVVM 패턴, Protocol 기반 인터페이스
- **GUI 패러다임:** 컴포넌트 기반 UI

## 아키텍처 개요
- **인터페이스 기반 설계:** Protocol을 활용한 계층 간 결합도 최소화
- **의존성 역전 원칙:** 상위 계층이 인터페이스에 의존하는 구조
- **시그널-슬롯 메커니즘:** PyQt6의 이벤트 시스템 활용
- **상태 관리:** TreeState 객체를 통한 일관된 상태 관리

## 프로젝트 구조
```
├── core/                  # 핵심 비즈니스 로직
│   ├── tree_state.py      # 트리 상태 클래스
│   ├── tree_state_interface.py  # 상태 관리자 인터페이스
│   └── tree_state_manager.py    # 상태 관리자 구현
├── models/                # 데이터 계층
│   ├── interfaces/        # 데이터 계층 인터페이스
│   ├── tree_data_repository.py  # 트리 데이터 저장소
│   └── database_connection.py   # 데이터베이스 연결
├── viewmodels/            # 뷰모델 계층
│   ├── interfaces/        # 뷰모델 인터페이스
│   ├── tree_viewmodel.py  # 트리 뷰모델
│   ├── item_viewmodel.py  # 아이템 뷰모델
│   └── tree_data_repository_viewmodel.py  # 저장소 뷰모델
├── view/                  # 뷰 계층
│   ├── qml/               # QML 컴포넌트
│   │   ├── components/    # 재사용 컴포넌트
│   │   ├── views/         # 화면 구성 요소
│   │   └── style/         # 스타일 정의
│   ├── tree.py            # 트리 위젯
│   └── main_window.py     # 메인 윈도우
└── utils/                 # 유틸리티 함수
    └── mouse_position.py  # 마우스 위치 관련 기능
```

## 인터페이스 구조
- **ITreeStateManager:** 트리 상태 관리 인터페이스
- **ITreeDataRepository:** 데이터 저장소 인터페이스
- **IRepositoryViewModel:** 저장소 뷰모델 인터페이스
- **ITreeViewModel:** 트리 뷰모델 인터페이스
- **IItemViewModel:** 아이템 데이터 인터페이스
- **IExecutor:** 실행기 인터페이스

## QML 컴포넌트
- **MacroTreeView:** 계층적 데이터 표시를 위한 커스텀 트리 뷰
- **TreeNodeDelegate:** 트리 노드 표현 위임자
- **ActionButtons:** 트리 조작 버튼 그룹
- **MainView:** 메인 뷰 레이아웃

## 설치 및 실행

### 요구 사항
- Python 3.8 이상
- PyQt6 및 QML 지원
- PostgreSQL(선택 사항)

### 설치
```bash
# 의존성 설치
pip install -r requirements.txt

# 추가 QML 플러그인 설치
pip install PyQt6-tools
```

### 실행
```bash
python main.py
```

## 데모
![main](https://user-images.githubusercontent.com/110750614/211150674-dfd5aa99-2ea1-47f3-839d-2494f83ab985.gif)
