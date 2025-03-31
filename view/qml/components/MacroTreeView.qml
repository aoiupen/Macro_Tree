// qml/components/MacroTreeView.qml
import QtQuick 6.0
import QtQuick.Controls 6.0
import QtQuick.Layouts 6.0
import "../style"

// 사용자 정의 트리 뷰 구현
Item {
    id: root
    
    // 필요한 속성들
    property var treeModel: null
    property var eventHandler: null
    
    // 모델 디버그 정보
    property int modelCount: treeModel ? treeModel.count : 0
    property bool modelValid: treeModel !== null
    
    // 디버그 로그 함수
    function logModelInfo() {
        console.log("MacroTreeView 모델 정보:");
        console.log("- 모델이 유효함: " + modelValid);
        console.log("- 항목 개수: " + modelCount);
        
        if (treeModel) {
            console.log("- 모델 타입: " + typeof treeModel);
            // 모델의 첫 번째 항목 확인 (있는 경우)
            if (modelCount > 0) {
                var item = treeModel.get(0);
                if (item) {
                    console.log("- 첫 번째 항목 정보:");
                    for (var prop in item) {
                        console.log("  * " + prop + ": " + item[prop]);
                    }
                } else {
                    console.log("- 첫 번째 항목을 가져올 수 없음");
                }
            }
        }
    }
    
    // 모델 변경 감지
    onTreeModelChanged: {
        console.log("트리 모델이 변경됨");
        logModelInfo();
    }
    
    // 트리 모델 변경 시그널 연결
    Connections {
        target: eventHandler
        function onTreeChanged() {
            console.log("이벤트 핸들러 트리 변경 시그널 수신");
            treeListView.forceLayout();
            logModelInfo();
        }
    }
    
    // 모델 디버그 정보 출력
    Rectangle {
        id: debugInfo
        visible: false // 필요시 true로 변경
        anchors.top: parent.top
        anchors.left: parent.left
        anchors.right: parent.right
        height: 30
        color: "lightgray"
        
        Text {
            anchors.fill: parent
            text: "모델: " + (modelValid ? "유효함" : "유효하지 않음") + " | 항목 수: " + modelCount
            verticalAlignment: Text.AlignVCenter
            horizontalAlignment: Text.AlignHCenter
        }
    }
    
    // 계층형 데이터를 위한 ListView 기반 구현
    ScrollView {
        id: scrollView
        anchors.top: debugInfo.visible ? debugInfo.bottom : parent.top
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.bottom: parent.bottom
        clip: true
        
        ListView {
            id: treeListView
            anchors.fill: parent
            model: root.treeModel
            
            // 데이터 없을 때 표시할 메시지
            Text {
                anchors.centerIn: parent
                visible: !root.modelValid || root.modelCount === 0
                text: !root.modelValid ? "트리 모델이 설정되지 않았습니다" : "데이터가 없습니다"
                color: "gray"
            }
            
            delegate: TreeNodeDelegate {
                width: treeListView.width
                
                // QAbstractListModel의 역할 기반 데이터 매핑
                itemData: {
                    // QML에서 model을 통해 접근하는 방식
                    return {
                        "name": model.name || "",
                        "id": model.id || "",
                        "depth": model.depth || 0,
                        "hasChildren": model.hasChildren || false,
                        "isExpanded": model.isExpanded || false,
                        "isSelected": model.isSelected || false,
                        "inputType": model.inputType || "",
                        "subAction": model.subAction || "",
                        "subContent": model.subContent || "",
                        "index": model.index
                    }
                }
                
                // 디버그 - 모델 데이터 로깅
                Component.onCompleted: {
                    if (model) {
                        console.log("노드 위임자 생성: " + (model.name || "이름 없음") + 
                                    " (인덱스: " + (model.index || "?") + ")");
                    } else {
                        console.log("모델 데이터 없이 노드 위임자 생성됨");
                    }
                }
                
                // 이벤트 연결
                onItemClicked: {
                    console.log("항목 클릭: " + (model ? (model.name || "이름 없음") : "알 수 없음"));
                    if (eventHandler) {
                        eventHandler.selectItem(model.index);
                    }
                }
                
                onExpandToggled: {
                    if (model && model.hasChildren) {
                        console.log("확장 토글: " + (model.name || "이름 없음"));
                        if (eventHandler) {
                            eventHandler.toggleExpand(model.id);
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
            console.log("그룹 추가 요청");
            if (treeModel && treeModel.addGroup) {
                treeModel.addGroup();
            }
        }
        
        onAddInstance: {
            console.log("인스턴스 추가 요청");
            if (treeModel && treeModel.addInstance) {
                treeModel.addInstance();
            }
        }
        
        onExecute: {
            console.log("실행 요청");
            if (treeModel && treeModel.executeSelectedItems) {
                treeModel.executeSelectedItems();
            }
        }
    }
    
    // 컴포넌트 초기화 시 로그 출력
    Component.onCompleted: {
        console.log("MacroTreeView 초기화 완료");
        logModelInfo();
    }
}