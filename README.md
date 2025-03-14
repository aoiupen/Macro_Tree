# Macro_Tree

트리 구조 기반 매크로 관리 애플리케이션

## 주요 기능
- 트리 노드 이동, 삽입, 삭제
- Undo, Redo
- 마우스 좌표 획득
- 체크박스 기능
- 그룹화 및 그룹 해제
- 저장 및 불러오기

## 개발 중인 기능
- 다크 테마
- 추가, 복사, 붙여넣기
- 실행 기능
- 단축키 지원 (Ctrl+C, Ctrl+V)

## 기술 스택
- **백엔드:** Python
- **프론트엔드:** PyQt/PySide, QML
- **아키텍처:** MVVM 패턴
- **배포:** Docker, PyInstaller (진행 중)

## 프로젝트 구조
```
├── core/          # 핵심 비즈니스 로직
├── models/        # 데이터 모델
├── viewmodels/    # UI와 모델 연결
├── view/          # 사용자 인터페이스
├── utils/         # 유틸리티 함수
└── resources/     # 리소스 파일
```

## 데모
![main](https://user-images.githubusercontent.com/110750614/211150674-dfd5aa99-2ea1-47f3-839d-2494f83ab985.gif)
