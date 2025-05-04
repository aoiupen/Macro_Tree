# Macro_Tree

> [!NOTE]
> 이 프로젝트는 현재 아키텍처 리팩토링 진행 중입니다.

트리 구조 기반 매크로 관리 애플리케이션입니다. 실무 환경에서 생산성을 3배 향상시킨 자동화 프로그램에서 착안하여 보안 관련 요소를 제거하고 범용 컨셉으로 확장성과 유연성을 확보하였습니다.

*다른 언어로 읽기: [English](README.md)*

## 프로젝트 상태

현재 이 프로젝트는 아키텍처 리팩토링 진행 중입니다:

- ✅ Core 모듈: 완료 (인터페이스 설계 및 기본 구현)
- 🔄 Model 계층: 진행 중 (extension/infra/service 분리 작업)
- 📅 ViewModel/View: 리팩토링 예정
- 📅 Platform (Adapter): 리팩토링 예정

이 저장소는 클린 아키텍처와 SOLID 원칙을 적용한 설계 사례를 보여주는 포트폴리오 목적으로 공개되었습니다.

## 주요 기능
- 트리 노드 이동, 삽입, 삭제
- Undo, Redo 기능
- 마우스 좌표 획득
- 그룹화 및 인스턴스 생성
- 데이터 영속성 (저장 및 불러오기)
- 계층 구조 시각화 및 조작

## 아키텍처 설계 특징

이 프로젝트는 다음 설계 원칙과 패턴을 적용했습니다:

- **SOLID 원칙**: 단일 책임(SRP), 개방-폐쇄(OCP), 리스코프 치환(LSP), 인터페이스 분리(ISP), 의존성 역전(DIP)
- **인터페이스 기반 설계**: Protocol을 활용한 명확한 계약 정의
- **계층화된 아키텍처**: Core, Model, ViewModel, Platform(Adapter), View로 관심사 분리

<details>
<summary>아키텍처 상세 보기</summary>

### Core 모듈
- **핵심 인터페이스**: 시스템의 기본 동작을 정의하는 프로토콜 집합
- **도메인 모델**: 비즈니스 개념을 표현하는 클래스 구조
- **비즈니스 규칙**: 도메인 로직 및 검증 규칙

### Model 계층
- **Repository**: 데이터 접근 및 저장 관련 클래스
- **Service**: 비즈니스 로직 구현 클래스
- **State Management**: 상태 관리 및 히스토리 추적
- **Event Handling**: 이벤트 기반 아키텍처 지원

### ViewModel & View 계층
- **State Transformation**: 모델 데이터를 뷰에 적합한 형태로 변환
- **UI Components**: PyQt6/QML 기반 UI 구현
</details>

## 기술 스택

- **백엔드**: Python 3.10
- **프론트엔드**: PyQt6, QML
- **데이터 관리**: PostgreSQL, File-based 저장소
- **아키텍처**: MVVM 패턴, Protocol 기반 인터페이스
- **자동화**: PyAutoGUI, pynput

<details>
<summary>프로젝트 구조</summary>

```
├── core/                     # 핵심 비즈니스 로직
│   ├── interfaces/           # 코어 인터페이스
│   └── impl/                 # 코어 구현체
├── model/                    # 비즈니스 로직 확장 계층
│   ├── persistence/          # 데이터 영속성 관리
│   ├── services/             # 비즈니스 서비스
│   ├── action/               # 액션 처리
│   └── events/               # 이벤트 처리
├── viewmodel/                # 뷰모델 계층
├── view/                     # 뷰 계층
├── platform/                 # 플랫폼 특화 코드
└── test/                     # 테스트 코드
```
</details>

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
- PostgreSQL (데이터 영속성)
- Windows 운영체제

## 라이선스
이 프로젝트는 MIT 라이선스를 따릅니다 - 자세한 내용은 [LICENSE](LICENSE) 파일을 참조하세요.

## 데모

현재 이 프로젝트는 아키텍처 리팩토링 중으로, 포트폴리오 제출 시점에는 다음 기능이 포함된 최소 기능 데모를 제공할 예정입니다:

- 트리 노드 생성, 편집, 삭제 기능
- 기본적인 매크로 설정 및 관리
- 간단한 UI 시각화

## 데모 영상
![main](https://user-images.githubusercontent.com/110750614/211150674-dfd5aa99-2ea1-47f3-839d-2494f83ab985.gif)
(과거 레거시 코드 기반의 데모 영상입니다) 