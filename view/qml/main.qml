// qml/main.qml
import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
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
    }
}