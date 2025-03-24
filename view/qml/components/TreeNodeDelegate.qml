import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import "../style"

// 사용자 정의 트리 노드 위임자
Rectangle {
    id: nodeDelegate
    height: 40
    color: isSelected ? Style.itemSelectedColor : 
           (mouseArea.containsMouse ? Style.itemHoverColor : Style.itemBackgroundColor)
    
    // 속성
    property var itemData: null
    property bool isSelected: itemData && itemData.isSelected ? itemData.isSelected : false
    property int indentation: 20
    
    // 시그널
    signal itemClicked()
    signal expandToggled()
    
    // 트리 노드 콘텐츠
    RowLayout {
        anchors.fill: parent
        anchors.leftMargin: (itemData && itemData.depth ? itemData.depth : 0) * indentation + 5
        anchors.rightMargin: 5
        spacing: 10
        
        // 확장/축소 표시기
        Item {
            width: 16
            height: 16
            visible: itemData && itemData.hasChildren ? itemData.hasChildren : false
            
            Text {
                anchors.centerIn: parent
                text: (itemData && itemData.isExpanded !== undefined) ? (itemData.isExpanded ? "▼" : "▶") : "▶"
                font.pixelSize: 10
                color: Style.textColor
            }
            
            MouseArea {
                anchors.fill: parent
                onClicked: {
                    expandToggled()
                }
            }
        }
        
        // 텍스트 라벨
        Label {
            text: itemData ? itemData.name || "" : ""
            Layout.fillWidth: true
            elide: Text.ElideRight
        }
        
        // 입력 타입 라벨
        Label {
            text: itemData ? itemData.inputType || "" : ""
            visible: text !== ""
        }
        
        // 서브 액션 라벨
        Label {
            text: itemData ? itemData.subAction || "" : ""
            visible: text !== ""
        }
        
        // 서브 콘텐츠 라벨
        Label {
            text: itemData ? itemData.subContent || "" : ""
            visible: text !== ""
            elide: Text.ElideRight
            Layout.maximumWidth: 150
        }
    }
    
    // 마우스 이벤트 영역
    MouseArea {
        id: mouseArea
        anchors.fill: parent
        hoverEnabled: true
        
        onClicked: {
            itemClicked()
        }
    }
} 