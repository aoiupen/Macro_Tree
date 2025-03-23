import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import "../components"
import "../style"

Item {
    id: mainView
    
    // default property를 사용해 자식 요소들을 contentArea에 배치
    default property alias content: contentArea.children
    
    // 메인 영역
    Rectangle {
        id: contentArea
        anchors.fill: parent
        color: Style.backgroundColor
        
        // 여기에 TreeView와 같은 자식 요소들이 배치됨
    }
    
    // 상태바
    Rectangle {
        id: statusBar
        anchors {
            left: parent.left
            right: parent.right
            bottom: parent.bottom
        }
        height: 24
        color: Style.headerColor
        
        Label {
            anchors.verticalCenter: parent.verticalCenter
            anchors.left: parent.left
            anchors.leftMargin: 10
            text: "상태: 준비됨"
            color: Style.textColor
        }
    }
}
