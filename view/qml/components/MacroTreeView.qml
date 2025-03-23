// qml/components/MacroTreeView.qml
import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import "../style"

// 사용자 정의 트리 뷰 구현
Item {
    id: root
    
    // 필요한 속성들
    property var treeModel: null
    property var eventHandler: null
    
    // 트리 모델 변경 시그널 연결
    Connections {
        target: eventHandler
        function onTreeChanged() {
            treeListView.forceLayout()
        }
    }
    
    // 계층형 데이터를 위한 ListView 기반 구현
    ScrollView {
        id: scrollView
        anchors.fill: parent
        clip: true
        
        ListView {
            id: treeListView
            anchors.fill: parent
            model: root.treeModel
            
            delegate: TreeNodeDelegate {
                width: treeListView.width
                
                // 모델 데이터 전달
                itemData: model
                
                // 이벤트 연결
                onItemClicked: {
                    if (eventHandler) {
                        eventHandler.selectItem(model.index)
                    }
                }
                
                onExpandToggled: {
                    if (model && model.hasChildren) {
                        if (eventHandler) {
                            eventHandler.toggleExpand(model.index)
                        }
                    }
                }
            }
        }
    }
    
    // 트리 조작 버튼들
    ActionButtons {
        anchors.right: parent.right
        anchors.bottom: parent.bottom
        
        onAddGroup: {
            if (treeModel && treeModel.addGroup) {
                treeModel.addGroup()
            }
        }
        
        onAddInstance: {
            if (treeModel && treeModel.addInstance) {
                treeModel.addInstance()
            }
        }
        
        onExecute: {
            if (treeModel && treeModel.executeSelectedItems) {
                treeModel.executeSelectedItems()
            }
        }
    }
}