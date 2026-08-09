import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Rectangle {
    id: filterBarRoot
    implicitHeight: 38
    color: "#0B0C0E"
    border.color: "#272A2F"
    border.width: 1
    radius: 6

    property int activeFilter: 0 // 0: All, 1: Matched, 2: Unmatched, 3: Suspicious
    signal filterChanged(int index)

    RowLayout {
        anchors.fill: parent
        anchors.leftMargin: 10
        anchors.rightMargin: 10
        spacing: 8

        // Filter Tabs
        Row {
            spacing: 4

            // Filter 0: All Tracks
            Rectangle {
                width: filter0Row.implicitWidth + 20; height: 26; radius: 13
                color: filterBarRoot.activeFilter === 0 ? "#181B1F" : (f0Mouse.containsMouse ? "#121417" : "transparent")
                border.color: filterBarRoot.activeFilter === 0 ? "#FF002B" : "transparent"

                Behavior on color { NumberAnimation { duration: 120 } }

                Row {
                    id: filter0Row
                    anchors.centerIn: parent
                    spacing: 6
                    Text {
                        text: "ALL TRACKS"
                        font.pixelSize: 10
                        font.weight: filterBarRoot.activeFilter === 0 ? Font.Bold : Font.Medium
                        color: filterBarRoot.activeFilter === 0 ? "#F2F2F2" : "#92969D"
                    }
                }
                MouseArea {
                    id: f0Mouse
                    anchors.fill: parent
                    hoverEnabled: true
                    onClicked: {
                        filterBarRoot.activeFilter = 0
                        filterBarRoot.filterChanged(0)
                    }
                }
            }

            // Filter 1: Matched
            Rectangle {
                width: filter1Row.implicitWidth + 20; height: 26; radius: 13
                color: filterBarRoot.activeFilter === 1 ? "#132A1C" : (f1Mouse.containsMouse ? "#121417" : "transparent")
                border.color: filterBarRoot.activeFilter === 1 ? "#34D399" : "transparent"

                Behavior on color { NumberAnimation { duration: 120 } }

                Row {
                    id: filter1Row
                    anchors.centerIn: parent
                    spacing: 6
                    Rectangle { width: 6; height: 6; radius: 3; color: "#34D399"; anchors.verticalCenter: parent.verticalCenter }
                    Text {
                        text: "MATCHED"
                        font.pixelSize: 10
                        font.weight: filterBarRoot.activeFilter === 1 ? Font.Bold : Font.Medium
                        color: filterBarRoot.activeFilter === 1 ? "#34D399" : "#92969D"
                    }
                }
                MouseArea {
                    id: f1Mouse
                    anchors.fill: parent
                    hoverEnabled: true
                    onClicked: {
                        filterBarRoot.activeFilter = 1
                        filterBarRoot.filterChanged(1)
                    }
                }
            }

            // Filter 2: Unmatched
            Rectangle {
                width: filter2Row.implicitWidth + 20; height: 26; radius: 13
                color: filterBarRoot.activeFilter === 2 ? "#2A0910" : (f2Mouse.containsMouse ? "#121417" : "transparent")
                border.color: filterBarRoot.activeFilter === 2 ? "#F87171" : "transparent"

                Behavior on color { NumberAnimation { duration: 120 } }

                Row {
                    id: filter2Row
                    anchors.centerIn: parent
                    spacing: 6
                    Rectangle { width: 6; height: 6; radius: 3; color: "#F87171"; anchors.verticalCenter: parent.verticalCenter }
                    Text {
                        text: "UNMATCHED"
                        font.pixelSize: 10
                        font.weight: filterBarRoot.activeFilter === 2 ? Font.Bold : Font.Medium
                        color: filterBarRoot.activeFilter === 2 ? "#F87171" : "#92969D"
                    }
                }
                MouseArea {
                    id: f2Mouse
                    anchors.fill: parent
                    hoverEnabled: true
                    onClicked: {
                        filterBarRoot.activeFilter = 2
                        filterBarRoot.filterChanged(2)
                    }
                }
            }

            // Filter 3: Needs Review / Anomalies
            Rectangle {
                width: filter3Row.implicitWidth + 20; height: 26; radius: 13
                color: filterBarRoot.activeFilter === 3 ? "#332200" : (f3Mouse.containsMouse ? "#121417" : "transparent")
                border.color: filterBarRoot.activeFilter === 3 ? "#FBBF24" : "transparent"

                Behavior on color { NumberAnimation { duration: 120 } }

                Row {
                    id: filter3Row
                    anchors.centerIn: parent
                    spacing: 6
                    Rectangle { width: 6; height: 6; radius: 3; color: "#FBBF24"; anchors.verticalCenter: parent.verticalCenter }
                    Text {
                        text: "NEEDS REVIEW"
                        font.pixelSize: 10
                        font.weight: filterBarRoot.activeFilter === 3 ? Font.Bold : Font.Medium
                        color: filterBarRoot.activeFilter === 3 ? "#FBBF24" : "#92969D"
                    }
                }
                MouseArea {
                    id: f3Mouse
                    anchors.fill: parent
                    hoverEnabled: true
                    onClicked: {
                        filterBarRoot.activeFilter = 3
                        filterBarRoot.filterChanged(3)
                    }
                }
            }
        }

        Item { Layout.fillWidth: true }
    }
}
