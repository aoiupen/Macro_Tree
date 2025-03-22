// qml/components/TreeItem.qml
import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

Item {
    id: root
    width: ListView.view ? ListView.view.width : 200
    height: 40
    
    // 속성 정의
    property string text: ""
    property string inputType: ""
    property string subAction: ""
    property string subContent: ""
    property bool expanded: false
    property int depth: 0
    property bool isSelected: false
    
    // 시그널 정의
    signal clicked()
    signal doubleClicked()
    signal moveRequested(int sourceIndex, int targetIndex)
    signal toggleExpand()
    
    // 배경 영역
    Rectangle {
        id: background
        anchors.fill: parent
        color: isSelected ? "#e0e0ff" : (mouseArea.containsMouse ? "#f0f0f0" : "transparent")
        border.width: isSelected ? 1 : 0
        border.color: "#c0c0c0"
    }
    
    // 들여쓰기 처리
    Item {
        id: indentation
        width: depth * 20
        height: parent.height
    }
    
    // 확장 아이콘
    Button {
        id: expandButton
        anchors.left: indentation.right
        anchors.verticalCenter: parent.verticalCenter
        width: 20
        height: 20
        text: expanded ? "▼" : "▶"
        visible: hasChildren
        flat: true
        property bool hasChildren: false // 이 속성은 모델에서 설정해야 함
        
        onClicked: {
            root.toggleExpand()
        }
    }
    
    // 메인 콘텐츠 영역
    RowLayout {
        anchors.left: expandButton.right
        anchors.right: parent.right
        anchors.verticalCenter: parent.verticalCenter
        anchors.leftMargin: 5
        anchors.rightMargin: 5
        spacing: 10
        
        // 텍스트 라벨
        Label {
            text: root.text
            Layout.fillWidth: true
            elide: Text.ElideRight
        }
        
        // 입력 타입 라벨
        Label {
            text: root.inputType
            visible: root.inputType !== ""
        }
        
        // 서브 액션 라벨
        Label {
            text: root.subAction
            visible: root.subAction !== ""
        }
        
        // 서브 콘텐츠 라벨
        Label {
            text: root.subContent
            visible: root.subContent !== ""
            elide: Text.ElideRight
            Layout.maximumWidth: 150
        }
    }
    
    // 마우스 이벤트 처리
    MouseArea {
        id: mouseArea
        anchors.fill: parent
        hoverEnabled: true
        
        onClicked: {
            root.clicked()
        }
        
        onDoubleClicked: {
            root.doubleClicked()
        }
    }
}