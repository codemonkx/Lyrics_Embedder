import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Rectangle {
    id: sidebar
    width: 190
    color: "#0B0C0E"
    border.color: "#272A2F"
    border.width: 1

    signal pageSelected(int index)
    property int currentIndex: 0

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 12
        spacing: 8

        // Navigation Items List
        ColumnLayout {
            Layout.fillWidth: true
            spacing: 2

            // Section 1: LIBRARY
            Text {
                text: "LIBRARY"
                font.pixelSize: 9
                font.weight: Font.Bold
                font.letterSpacing: 1.0
                color: "#62666D"
                Layout.leftMargin: 8
                Layout.topMargin: 4
                Layout.bottomMargin: 4
            }

            Rectangle {
                Layout.fillWidth: true
                Layout.preferredHeight: 34
                radius: 4
                color: sidebar.currentIndex === 0 ? "#181B1F" : (nav1Mouse.containsMouse ? "#121417" : "transparent")

                Rectangle {
                    anchors.left: parent.left
                    width: 2; height: parent.height
                    color: "#FF002B"
                    visible: sidebar.currentIndex === 0
                }

                RowLayout {
                    anchors.fill: parent
                    anchors.leftMargin: 12
                    spacing: 8
                    Text { text: "📁"; font.pixelSize: 11 }
                    Text {
                        text: "All Music"
                        font.pixelSize: 12
                        font.weight: sidebar.currentIndex === 0 ? Font.Bold : Font.Normal
                        color: sidebar.currentIndex === 0 ? "#F2F2F2" : "#92969D"
                    }
                }
                MouseArea {
                    id: nav1Mouse
                    anchors.fill: parent
                    hoverEnabled: true
                    onClicked: sidebar.pageSelected(0)
                }
            }

            // Section 2: TOOLS
            Text {
                text: "TOOLS"
                font.pixelSize: 9
                font.weight: Font.Bold
                font.letterSpacing: 1.0
                color: "#62666D"
                Layout.leftMargin: 8
                Layout.topMargin: 12
                Layout.bottomMargin: 4
            }

            Rectangle {
                Layout.fillWidth: true
                Layout.preferredHeight: 34
                radius: 4
                color: sidebar.currentIndex === 1 ? "#181B1F" : (nav2Mouse.containsMouse ? "#121417" : "transparent")

                Rectangle {
                    anchors.left: parent.left
                    width: 2; height: parent.height
                    color: "#FF002B"
                    visible: sidebar.currentIndex === 1
                }

                RowLayout {
                    anchors.fill: parent
                    anchors.leftMargin: 12
                    spacing: 8
                    Text { text: "🔬"; font.pixelSize: 11 }
                    Text {
                        text: "Audio Analysis"
                        font.pixelSize: 12
                        font.weight: sidebar.currentIndex === 1 ? Font.Bold : Font.Normal
                        color: sidebar.currentIndex === 1 ? "#F2F2F2" : "#92969D"
                    }
                }
                MouseArea {
                    id: nav2Mouse
                    anchors.fill: parent
                    hoverEnabled: true
                    onClicked: sidebar.pageSelected(1)
                }
            }

            Rectangle {
                Layout.fillWidth: true
                Layout.preferredHeight: 34
                radius: 4
                color: sidebar.currentIndex === 2 ? "#181B1F" : (nav3Mouse.containsMouse ? "#121417" : "transparent")

                Rectangle {
                    anchors.left: parent.left
                    width: 2; height: parent.height
                    color: "#FF002B"
                    visible: sidebar.currentIndex === 2
                }

                RowLayout {
                    anchors.fill: parent
                    anchors.leftMargin: 12
                    spacing: 8
                    Text { text: "📊"; font.pixelSize: 11 }
                    Text {
                        text: "Reports & Logs"
                        font.pixelSize: 12
                        font.weight: sidebar.currentIndex === 2 ? Font.Bold : Font.Normal
                        color: sidebar.currentIndex === 2 ? "#F2F2F2" : "#92969D"
                    }
                }
                MouseArea {
                    id: nav3Mouse
                    anchors.fill: parent
                    hoverEnabled: true
                    onClicked: sidebar.pageSelected(2)
                }
            }

            // Section 3: SYSTEM
            Text {
                text: "SYSTEM"
                font.pixelSize: 9
                font.weight: Font.Bold
                font.letterSpacing: 1.0
                color: "#62666D"
                Layout.leftMargin: 8
                Layout.topMargin: 12
                Layout.bottomMargin: 4
            }

            Rectangle {
                Layout.fillWidth: true
                Layout.preferredHeight: 34
                radius: 4
                color: sidebar.currentIndex === 3 ? "#181B1F" : (nav4Mouse.containsMouse ? "#121417" : "transparent")

                Rectangle {
                    anchors.left: parent.left
                    width: 2; height: parent.height
                    color: "#FF002B"
                    visible: sidebar.currentIndex === 3
                }

                RowLayout {
                    anchors.fill: parent
                    anchors.leftMargin: 12
                    spacing: 8
                    Text { text: "⚙️"; font.pixelSize: 11 }
                    Text {
                        text: "Settings"
                        font.pixelSize: 12
                        font.weight: sidebar.currentIndex === 3 ? Font.Bold : Font.Normal
                        color: sidebar.currentIndex === 3 ? "#F2F2F2" : "#92969D"
                    }
                }
                MouseArea {
                    id: nav4Mouse
                    anchors.fill: parent
                    hoverEnabled: true
                    onClicked: sidebar.pageSelected(3)
                }
            }
        }

        Item { Layout.fillHeight: true }

        // Version badge
        Text {
            text: "LyricForge v2.0"
            font.pixelSize: 9
            font.weight: Font.Bold
            color: "#62666D"
            Layout.alignment: Qt.AlignHCenter
        }
    }
}
