// qml/main.qml
import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import QtQuick.Window 2.15
import "./components"
import "./views"
import "./style"

ApplicationWindow {
    id: window
    visible: true
    width: 800
    height: 600
    title: "Macro Tree"
    
    // 메인 레이아웃
    MainView {
        anchors.fill: parent
        
        // 트리 뷰
        TreeView {
            id: treeView
            anchors.fill: parent
            treeModel: _treeModel        // Python에서 등록한 모델
            eventHandler: _eventHandler  // Python에서 등록한 이벤트 핸들러
        }
    }
    
    // 메뉴바
    menuBar: MenuBar {
        Menu {
            title: "파일"
            Action {
                text: "저장"
                shortcut: "Ctrl+S"
                onTriggered: _treeBusinessLogic.saveTree()
            }
        }
        
        Menu {
            title: "실행"
            Action {
                text: "실행"
                shortcut: "F5"
                onTriggered: _treeBusinessLogic.executeSelectedItems()
            }
        }
    }
}