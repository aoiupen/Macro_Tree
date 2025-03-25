// qml/components/TreeItem.qml
import QtQuick 6.0
import QtQuick.Controls 6.0
import QtQuick.Layouts 6.0

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
        
        // 테스트 이미지
        Image {
            source: "qrc:/images/test.png"
            width: 16
            height: 16
            fillMode: Image.PreserveAspectFit
            Layout.alignment: Qt.AlignVCenter
        }
        
        // 텍스트 라벨
        Label {
            text: root.text
            Layout.fillWidth: true
            elide: Text.ElideRight
        }
        
        // 입력 타입 라벨
        RowLayout {
            spacing: 5
            visible: root.inputType !== ""
            Layout.alignment: Qt.AlignVCenter
            
            Image {
                id: inputTypeIcon
                source: {
                    var imgSource = ""
                    if (root.inputType === "mouse") {
                        imgSource = "qrc:/images/mouse.png"
                        console.log("마우스 이미지 경로:", imgSource)
                    }
                    else if (root.inputType === "keyboard") {
                        imgSource = "qrc:/images/key.png"
                        console.log("키보드 이미지 경로:", imgSource)
                    }
                    return imgSource
                }
                visible: source !== ""
                width: 16
                height: 16
                fillMode: Image.PreserveAspectFit
                Layout.alignment: Qt.AlignVCenter
                
                // 이미지 로딩 상태에 따른 처리
                onStatusChanged: {
                    console.log("이미지 상태:", status, "소스:", source)
                    if (status === Image.Error) {
                        console.log("이미지 로드 실패:", source)
                    }
                }
            }
            
            Label {
                text: root.inputType
                Layout.alignment: Qt.AlignVCenter
            }
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