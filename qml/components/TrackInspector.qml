import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Rectangle {
    id: inspectorRoot
    property var track: null
    property bool isVisible: track !== null

    implicitWidth: 340
    color: "#121417"
    border.color: "#272A2F"
    border.width: 1
    radius: 6

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 16
        spacing: 16

        // Header Title
        RowLayout {
            Layout.fillWidth: true
            Text {
                text: "TECHNICAL INSPECTOR"
                font.pixelSize: 11
                font.weight: Font.Bold
                font.letterSpacing: 1.0
                color: "#62666D"
            }
            Item { Layout.fillWidth: true }
            Button {
                implicitWidth: 24; implicitHeight: 24
                background: Rectangle { color: parent.hovered ? "#181B1F" : "transparent"; radius: 4 }
                contentItem: Text { text: "✕"; color: "#92969D"; horizontalAlignment: Text.AlignHCenter; verticalAlignment: Text.AlignVCenter }
                onClicked: inspectorRoot.track = null
            }
        }

        // Empty state when no track selected
        Column {
            Layout.fillWidth: true
            Layout.fillHeight: true
            visible: inspectorRoot.track === null
            spacing: 12
            anchors.centerIn: parent

            Text {
                text: "Select a track from the library list to inspect metadata, lyrics, and audio spectrum profile."
                font.pixelSize: 11
                color: "#62666D"
                horizontalAlignment: Text.AlignHCenter
                wrapMode: Text.WordWrap
                width: parent.width - 32
            }
        }

        // Active Track Metadata Content
        ScrollView {
            Layout.fillWidth: true
            Layout.fillHeight: true
            visible: inspectorRoot.track !== null
            clip: true
            contentWidth: parent.width - 12

            ColumnLayout {
                width: parent.width
                spacing: 14

                // Hero Track Banner Card
                Rectangle {
                    Layout.fillWidth: true
                    Layout.preferredHeight: 74
                    color: "#0B0C0E"
                    border.color: "#272A2F"
                    radius: 6

                    RowLayout {
                        anchors.fill: parent
                        anchors.margins: 12
                        spacing: 12

                        Text { text: "🔴"; font.pixelSize: 22 }

                        ColumnLayout {
                            Layout.fillWidth: true
                            spacing: 2

                            Text {
                                text: inspectorRoot.track ? (inspectorRoot.track.title || "Untitled") : ""
                                font.pixelSize: 13
                                font.weight: Font.Bold
                                color: "#F2F2F2"
                                elide: Text.ElideRight
                                Layout.fillWidth: true
                            }

                            Text {
                                text: inspectorRoot.track ? ((inspectorRoot.track.artist || "Unknown Artist") + " — " + (inspectorRoot.track.album || "Unknown Album")) : ""
                                font.pixelSize: 11
                                color: "#92969D"
                                elide: Text.ElideRight
                                Layout.fillWidth: true
                            }
                        }
                    }
                }

                // Specs Grid
                Rectangle {
                    Layout.fillWidth: true
                    Layout.preferredHeight: 110
                    color: "#0B0C0E"
                    border.color: "#272A2F"
                    radius: 6

                    GridLayout {
                        anchors.fill: parent
                        anchors.margins: 12
                        columns: 2
                        columnSpacing: 16
                        rowSpacing: 8

                        Text { text: "FORMAT"; font.pixelSize: 10; color: "#62666D" }
                        Text {
                            text: inspectorRoot.track ? (inspectorRoot.track.file_path ? inspectorRoot.track.file_path.split('.').pop().toUpperCase() : "-") : "-"
                            font.pixelSize: 11; font.weight: Font.Bold; color: "#F2F2F2"
                        }

                        Text { text: "SAMPLE RATE"; font.pixelSize: 10; color: "#62666D" }
                        Text {
                            text: inspectorRoot.track && inspectorRoot.track.sample_rate ? (inspectorRoot.track.sample_rate + " Hz") : "-"
                            font.pixelSize: 11; color: "#F2F2F2"
                        }

                        Text { text: "BIT DEPTH"; font.pixelSize: 10; color: "#62666D" }
                        Text {
                            text: inspectorRoot.track && inspectorRoot.track.bits_per_sample ? (inspectorRoot.track.bits_per_sample + "-bit") : "-"
                            font.pixelSize: 11; color: "#F2F2F2"
                        }

                        Text { text: "DURATION"; font.pixelSize: 10; color: "#62666D" }
                        Text {
                            text: {
                                if (!inspectorRoot.track) return "-"
                                var dur = inspectorRoot.track.duration || 0
                                return Math.floor(dur / 60) + ":" + (Math.floor(dur % 60) < 10 ? "0" : "") + Math.floor(dur % 60)
                            }
                            font.pixelSize: 11; color: "#F2F2F2"
                        }
                    }
                }

                // Spectrum Visualization Provider Container
                SpectrumView {
                    Layout.fillWidth: true
                    Layout.preferredHeight: 160
                    filePath: inspectorRoot.track ? inspectorRoot.track.file_path : ""
                }

                // Action Hierarchy (Primary red accent for main action, secondary for rest)
                ColumnLayout {
                    Layout.fillWidth: true
                    spacing: 8

                    PillButton {
                        text: "🔴 EMBED TRACK LYRICS"
                        isPrimary: true
                        enabled: inspectorRoot.track !== null && inspectorRoot.track.lyric_id !== null
                        Layout.fillWidth: true
                        onClicked: {
                            if (inspectorRoot.track && typeof lyricService !== "undefined") {
                                lyricService.embedSelectedTracks([inspectorRoot.track.id])
                            }
                        }
                    }

                    PillButton {
                        text: "🔬 INSPECT AUDIO FFT"
                        enabled: inspectorRoot.track !== null
                        Layout.fillWidth: true
                        onClicked: {
                            if (inspectorRoot.track && typeof analysisService !== "undefined") {
                                analysisService.analyzeFile(inspectorRoot.track.file_path)
                            }
                        }
                    }
                }
            }
        }
    }
}
