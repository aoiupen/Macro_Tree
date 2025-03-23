import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import "../style"

Item {
    id: root
    width: buttonsLayout.width
    height: buttonsLayout.height
    
    // 시그널 정의
    signal addGroup()
    signal addInstance()
    signal execute()
    
    // 버튼 레이아웃
    RowLayout {
        id: buttonsLayout
        spacing: Style.padding
        
        Button {
            text: "그룹 추가"
            onClicked: root.addGroup()
            
            background: Rectangle {
                color: parent.pressed ? Style.buttonPressedColor : 
                       parent.hovered ? Style.buttonHoverColor : Style.buttonColor
                radius: 4
            }
            
            contentItem: Text {
                text: parent.text
                color: "white"
                horizontalAlignment: Text.AlignHCenter
                verticalAlignment: Text.AlignVCenter
            }
            
            padding: Style.padding
        }
        
        Button {
            text: "인스턴스 추가"
            onClicked: root.addInstance()
            
            background: Rectangle {
                color: parent.pressed ? Style.buttonPressedColor : 
                       parent.hovered ? Style.buttonHoverColor : Style.buttonColor
                radius: 4
            }
            
            contentItem: Text {
                text: parent.text
                color: "white"
                horizontalAlignment: Text.AlignHCenter
                verticalAlignment: Text.AlignVCenter
            }
            
            padding: Style.padding
        }
        
        Button {
            text: "실행"
            onClicked: root.execute()
            
            background: Rectangle {
                color: parent.pressed ? Qt.darker(Style.secondaryColor, 1.2) : 
                       parent.hovered ? Qt.darker(Style.secondaryColor, 1.1) : Style.secondaryColor
                radius: 4
            }
            
            contentItem: Text {
                text: parent.text
                color: "white"
                horizontalAlignment: Text.AlignHCenter
                verticalAlignment: Text.AlignVCenter
            }
            
            padding: Style.padding
        }
    }
}
