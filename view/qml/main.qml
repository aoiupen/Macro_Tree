// qml/main.qml
import QtQuick 6.0
import QtQuick.Controls 6.0
import QtQuick.Layouts 6.0
import QtQuick.Window 2.15
import QtQuick.Controls.Basic 2.15  // 기본 스타일 명시적 임포트
import "./components"
import "./views"
import "./style"

ApplicationWindow {
    id: window
    visible: true
    width: 800
    height: 600
    title: "Macro Tree"
    
    // 기본 스타일 설정 (Windows 스타일 오류 방지)
    Component.onCompleted: {
        console.log("윈도우 초기화 완료")
        console.log("트리 모델 유효성: " + (_treeModel !== null))
    }
    
    // 모델 변경 감지
    Connections {
        target: _treeModel
        function onStateChanged() {
            console.log("트리 모델 상태 변경됨")
            logModelData()
        }
    }
    
    // 트리 모델 정보 로깅 함수
    function logModelData() {
        if (!_treeModel) {
            console.log("트리 모델이 null입니다")
            return
        }
        
        console.log("트리 모델 정보:")
        // 모델 메타데이터 확인
        console.log("- 객체 타입: " + typeof _treeModel)
        
        // 모델 메소드 호출
        var selectedItems = _treeModel.get_selected_items ? _treeModel.get_selected_items() : []
        console.log("- 선택된 항목 수: " + selectedItems.length)
        
        // 현재 모델의 상태 확인
        var state = _treeModel.get_current_state ? _treeModel.get_current_state() : null
        if (state) {
            console.log("- 현재 상태 유효함")
            console.log("- 노드 수: " + (state.nodes ? Object.keys(state.nodes).length : 0))
        } else {
            console.log("- 현재 상태 없음")
        }
    }
    
    // 전역 단축키 설정
    Shortcut {
        sequence: "Ctrl+S"
        onActivated: if (_treeBusinessLogic) _treeBusinessLogic.saveTree()
    }
    
    Shortcut {
        sequence: "F5"
        onActivated: if (_treeBusinessLogic) _treeBusinessLogic.executeSelectedItems()
    }
    
    // 메인 레이아웃
    MainView {
        id: mainView
        anchors.fill: parent
        
        // 트리 뷰
        Item {
            id: treeViewContainer
            anchors.fill: parent
            
            MacroTreeView {
                id: treeView
                anchors.fill: parent
                treeModel: _treeModel || null  // null 체크 추가
                eventHandler: _eventHandler || null  // null 체크 추가
            }
        }
    }
    
    // 디버깅 패널
    Rectangle {
        id: debugPanel
        height: 40
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.bottom: parent.bottom
        color: "#e0e0e0"
        visible: false // 테스트 후 숨기려면 false로 설정
        
        RowLayout {
            anchors.fill: parent
            anchors.margins: 5
            spacing: 10
            
            Button {
                text: "데이터 확인"
                onClicked: {
                    logModelData()
                    // 디버그 메시지를 펼치려면 debugInfo.visible = true
                    if (treeView) {
                        var debugInfoItem = treeView.findChild("debugInfo")
                        if (debugInfoItem) {
                            debugInfoItem.visible = true
                        }
                    }
                }
            }
            
            Button {
                text: "DB 데이터 로드"
                onClicked: {
                    if (_repository) {
                        _repository.load_tree_from_db()
                    }
                }
            }
            
            Button {
                text: "더미 데이터 로드"
                onClicked: {
                    if (_repository) {
                        _repository.create_new_tree()
                    }
                }
            }
            
            Label {
                text: "디버깅 도구"
                Layout.fillWidth: true
                horizontalAlignment: Text.AlignRight
            }
        }
    }
    
    // 메뉴바 - 기본 컴포넌트로 변경
    menuBar: MenuBar {
        Menu {
            title: "파일"
            MenuItem {
                text: "새로 만들기"
                onTriggered: if (_repository) _repository.create_new_tree()
            }
            MenuItem {
                text: "열기"
                onTriggered: if (_repository) _repository.load_tree_from_db()
            }
            MenuItem {
                text: "저장"
                onTriggered: if (_treeBusinessLogic) _treeBusinessLogic.saveTree()
            }
            MenuItem {
                text: "다른 이름으로 저장"
                enabled: false  // 아직 구현되지 않음
            }
        }
        
        Menu {
            title: "실행"
            MenuItem {
                text: "실행"
                onTriggered: if (_treeBusinessLogic) _treeBusinessLogic.executeSelectedItems()
            }
        }
        
        Menu {
            title: "디버그"
            MenuItem {
                text: "디버그 패널 표시"
                checkable: true
                checked: debugPanel.visible
                onTriggered: debugPanel.visible = !debugPanel.visible
            }
            MenuItem {
                text: "상태 정보 출력"
                onTriggered: logModelData()
            }
        }
    }
}