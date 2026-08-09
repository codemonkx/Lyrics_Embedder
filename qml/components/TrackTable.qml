import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Rectangle {
    id: tableRoot
    property var tracksModel: libraryService ? libraryService.tracks : []
    property var selectedTrack: null
    signal trackSelected(var track)

    color: "#121417"
    border.color: "#272A2F"
    border.width: 1
    radius: 6

    ColumnLayout {
        anchors.fill: parent
        spacing: 0

        // Column Headers Bar
        Rectangle {
            Layout.fillWidth: true
            Layout.preferredHeight: 32
            color: "#0B0C0E"
            border.color: "#272A2F"
            border.width: 1

            RowLayout {
                anchors.fill: parent
                anchors.leftMargin: 16
                anchors.rightMargin: 16
                spacing: 12

                Text { text: "TITLE"; font.pixelSize: 10; font.weight: Font.Bold; color: "#62666D"; Layout.fillWidth: true }
                Text { text: "ARTIST"; font.pixelSize: 10; font.weight: Font.Bold; color: "#62666D"; Layout.preferredWidth: 160 }
                Text { text: "ALBUM"; font.pixelSize: 10; font.weight: Font.Bold; color: "#62666D"; Layout.preferredWidth: 140 }
                Text { text: "FORMAT"; font.pixelSize: 10; font.weight: Font.Bold; color: "#62666D"; Layout.preferredWidth: 80 }
                Text { text: "TIME"; font.pixelSize: 10; font.weight: Font.Bold; color: "#62666D"; Layout.preferredWidth: 60 }
                Text { text: "LYRICS"; font.pixelSize: 10; font.weight: Font.Bold; color: "#62666D"; Layout.preferredWidth: 90 }
            }
        }

        // ListView rows
        ListView {
            id: listView
            Layout.fillWidth: true
            Layout.fillHeight: true
            clip: true
            model: tableRoot.tracksModel

            delegate: Rectangle {
                width: listView.width
                height: 38
                color: modelData === tableRoot.selectedTrack ? "#181B1F" : (rowMouse.containsMouse ? "#15181D" : "transparent")

                Rectangle {
                    anchors.bottom: parent.bottom
                    width: parent.width
                    height: 1
                    color: "#181B1F"
                }

                Rectangle {
                    anchors.left: parent.left
                    width: 3
                    height: parent.height
                    color: "#FF002B"
                    visible: modelData === tableRoot.selectedTrack
                }

                RowLayout {
                    anchors.fill: parent
                    anchors.leftMargin: 16
                    anchors.rightMargin: 16
                    spacing: 12

                    // Title
                    Text {
                        text: modelData.title || (modelData.file_path ? modelData.file_path.split(/[\\/]/).pop() : "Untitled")
                        font.pixelSize: 12
                        font.weight: Font.Medium
                        color: "#F2F2F2"
                        Layout.fillWidth: true
                        elide: Text.ElideRight
                    }

                    // Artist
                    Text {
                        text: modelData.artist || "Unknown Artist"
                        font.pixelSize: 11
                        color: "#92969D"
                        Layout.preferredWidth: 160
                        elide: Text.ElideRight
                    }

                    // Album
                    Text {
                        text: modelData.album || "Unknown Album"
                        font.pixelSize: 11
                        color: "#92969D"
                        Layout.preferredWidth: 140
                        elide: Text.ElideRight
                    }

                    // Format Badge
                    Text {
                        text: modelData.file_path ? modelData.file_path.split('.').pop().toUpperCase() : "AUDIO"
                        font.pixelSize: 10
                        font.weight: Font.Bold
                        color: "#62666D"
                        Layout.preferredWidth: 80
                    }

                    // Time
                    Text {
                        text: {
                            var dur = modelData.duration || 0
                            var m = Math.floor(dur / 60)
                            var s = Math.floor(dur % 60)
                            return m + ":" + (s < 10 ? "0" : "") + s
                        }
                        font.pixelSize: 11
                        color: "#92969D"
                        Layout.preferredWidth: 60
                    }

                    // Lyrics Status Badge
                    StatusBadge {
                        statusText: modelData.lyric_id ? "MATCHED" : "MISSING"
                        statusType: modelData.lyric_id ? "matched" : "missing"
                        Layout.preferredWidth: 90
                    }
                }

                MouseArea {
                    id: rowMouse
                    anchors.fill: parent
                    hoverEnabled: true
                    onClicked: {
                        tableRoot.selectedTrack = modelData
                        tableRoot.trackSelected(modelData)
                    }
                }
            }

            EmptyState {
                anchors.centerIn: parent
                visible: listView.count === 0
            }
        }
    }
}
