// qml/components/TreeView.qml
import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

Item {
    id: root
    
    // 필요한 속성들
    property var treeModel: null
    property var eventHandler: null
    
    // 트리 모델 변경 시그널 연결
    Connections {
        target: eventHandler
        function onTreeChanged() {
            treeView.forceLayout()
        }
    }
    
    // 실제 트리 뷰 구현
    TreeView {
        id: treeView
        anchors.fill: parent
        model: root.treeModel
        
        delegate: TreeItem {
            text: model.name
            inputType: model.inputType
            subAction: model.subAction
            subContent: model.subContent
            
            onClicked: {
                eventHandler.selectItem(model.index)
            }
            
            onMoveRequested: {
                eventHandler.moveItem(sourceIndex, targetIndex)
            }
        }
    }
    
    // 트리 조작 버튼들
    ActionButtons {
        anchors.right: parent.right
        anchors.bottom: parent.bottom
        
        onAddGroup: {
            treeModel.addGroup()
        }
        
        onAddInstance: {
            treeModel.addInstance()
        }
        
        onExecute: {
            treeModel.executeSelectedItems()
        }
    }
}