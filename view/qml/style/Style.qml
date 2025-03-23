pragma Singleton
import QtQuick 2.15

QtObject {
    // 기본 색상
    readonly property color backgroundColor: "#f5f5f5"
    readonly property color headerColor: "#e0e0e0"
    readonly property color primaryColor: "#2196F3"
    readonly property color secondaryColor: "#4CAF50"
    readonly property color textColor: "#212121"
    readonly property color lightTextColor: "#757575"
    
    // 패딩 및 마진
    readonly property int smallPadding: 4
    readonly property int padding: 8
    readonly property int largePadding: 16
    
    // 폰트 크기
    readonly property int smallFontSize: 12
    readonly property int normalFontSize: 14
    readonly property int largeFontSize: 16
    readonly property int headerFontSize: 18
    
    // 컴포넌트 스타일
    readonly property color buttonColor: primaryColor
    readonly property color buttonHoverColor: Qt.darker(primaryColor, 1.1)
    readonly property color buttonPressedColor: Qt.darker(primaryColor, 1.2)
    
    // 아이템 스타일
    readonly property color itemBackgroundColor: "#ffffff"
    readonly property color itemSelectedColor: Qt.alpha(primaryColor, 0.2)
    readonly property color itemHoverColor: Qt.alpha(primaryColor, 0.1)
} 