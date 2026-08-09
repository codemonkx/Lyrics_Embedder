import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Rectangle {
    id: sidebar
    width: 220
    color: "#0B0C0E"
    border.color: "#272A2F"
    border.width: 1

    signal pageSelected(int index)
    property int currentIndex: 0

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 16
        spacing: 12

        // Brand Title Header
        RowLayout {
            spacing: 8
            Rectangle {
                width: 8; height: 8
                radius: 4
                color: "#FF002B"
            }
            Text {
                text: ":: LYRICFORGE PRO ::"
                font.pixelSize: 11
                font.weight: Font.Black
                font.letterSpacing: 1.5
                color: "#F2F2F2"
            }
        }

        Item { Layout.preferredHeight: 12 }

        // Navigation Items List
        ColumnLayout {
            Layout.fillWidth: true
            spacing: 4

            // Section 1: Library
            Text {
                text: ":: LIBRARY ::"
                font.pixelSize: 10
                font.weight: Font.Bold
                font.letterSpacing: 1.0
                color: "#62666D"
                Layout.leftMargin: 8
                Layout.topMargin: 8
                Layout.bottomMargin: 4
            }

            Rectangle {
                Layout.fillWidth: true
                Layout.preferredHeight: 36
                radius: 6
                color: sidebar.currentIndex === 0 ? "#181B1F" : (nav1Mouse.containsMouse ? "#121417" : "transparent")
                border.color: sidebar.currentIndex === 0 ? "#FF002B" : "transparent"

                RowLayout {
                    anchors.fill: parent
                    anchors.leftMargin: 12
                    spacing: 10
                    Text { text: "🔴"; font.pixelSize: 10 }
                    Text {
                        text: "All Tracks"
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

            // Section 2: Audio Analysis
            Text {
                text: ":: ANALYSIS ::"
                font.pixelSize: 10
                font.weight: Font.Bold
                font.letterSpacing: 1.0
                color: "#62666D"
                Layout.leftMargin: 8
                Layout.topMargin: 12
                Layout.bottomMargin: 4
            }

            Rectangle {
                Layout.fillWidth: true
                Layout.preferredHeight: 36
                radius: 6
                color: sidebar.currentIndex === 1 ? "#181B1F" : (nav2Mouse.containsMouse ? "#121417" : "transparent")
                border.color: sidebar.currentIndex === 1 ? "#FF002B" : "transparent"

                RowLayout {
                    anchors.fill: parent
                    anchors.leftMargin: 12
                    spacing: 10
                    Text { text: "🔬"; font.pixelSize: 11 }
                    Text {
                        text: "Audio Inspector"
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

            // Section 3: Reports & Logs
            Text {
                text: ":: REPORTS & LOGS ::"
                font.pixelSize: 10
                font.weight: Font.Bold
                font.letterSpacing: 1.0
                color: "#62666D"
                Layout.leftMargin: 8
                Layout.topMargin: 12
                Layout.bottomMargin: 4
            }

            Rectangle {
                Layout.fillWidth: true
                Layout.preferredHeight: 36
                radius: 6
                color: sidebar.currentIndex === 2 ? "#181B1F" : (nav3Mouse.containsMouse ? "#121417" : "transparent")
                border.color: sidebar.currentIndex === 2 ? "#FF002B" : "transparent"

                RowLayout {
                    anchors.fill: parent
                    anchors.leftMargin: 12
                    spacing: 10
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

            // Section 4: Preferences
            Text {
                text: ":: PREFERENCES ::"
                font.pixelSize: 10
                font.weight: Font.Bold
                font.letterSpacing: 1.0
                color: "#62666D"
                Layout.leftMargin: 8
                Layout.topMargin: 12
                Layout.bottomMargin: 4
            }

            Rectangle {
                Layout.fillWidth: true
                Layout.preferredHeight: 36
                radius: 6
                color: sidebar.currentIndex === 3 ? "#181B1F" : (nav4Mouse.containsMouse ? "#121417" : "transparent")
                border.color: sidebar.currentIndex === 3 ? "#FF002B" : "transparent"

                RowLayout {
                    anchors.fill: parent
                    anchors.leftMargin: 12
                    spacing: 10
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

        // Version badge at bottom
        Text {
            text: "v2.0.0 PRO"
            font.pixelSize: 10
            font.weight: Font.Bold
            color: "#62666D"
            Layout.alignment: Qt.AlignHCenter
        }
    }
}
