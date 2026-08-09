import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "../components"

Item {
    id: libraryPage

    property var selectedTrack: null

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 20
        spacing: 16

        // 1. Metric Capsules Header Row
        RowLayout {
            Layout.fillWidth: true
            spacing: 12

            GlassCard {
                Layout.fillWidth: true
                Layout.preferredHeight: 70
                Column {
                    anchors.centerIn: parent
                    spacing: 2
                    Text { text: "01 // TOTAL TRACKS"; font.pixelSize: 9; font.weight: Font.Bold; color: "#FF002B" }
                    Text { text: libraryService.totalTracks.toString(); font.pixelSize: 20; font.weight: Font.Black; color: "#F2F2F2" }
                }
            }

            GlassCard {
                Layout.fillWidth: true
                Layout.preferredHeight: 70
                Column {
                    anchors.centerIn: parent
                    spacing: 2
                    Text { text: "02 // MATCHED LYRICS"; font.pixelSize: 9; font.weight: Font.Bold; color: "#FF002B" }
                    Text { text: libraryService.matchedTracks.toString(); font.pixelSize: 20; font.weight: Font.Black; color: "#34D399" }
                }
            }

            GlassCard {
                Layout.fillWidth: true
                Layout.preferredHeight: 70
                Column {
                    anchors.centerIn: parent
                    spacing: 2
                    Text { text: "03 // UNMATCHED"; font.pixelSize: 9; font.weight: Font.Bold; color: "#FF002B" }
                    Text { text: libraryService.unmatchedTracks.toString(); font.pixelSize: 20; font.weight: Font.Black; color: "#62666D" }
                }
            }

            GlassCard {
                Layout.fillWidth: true
                Layout.preferredHeight: 70
                Column {
                    anchors.centerIn: parent
                    spacing: 2
                    Text { text: "04 // NEEDS REVIEW"; font.pixelSize: 9; font.weight: Font.Bold; color: "#FF002B" }
                    Text { text: libraryService.suspiciousTracks.toString(); font.pixelSize: 20; font.weight: Font.Black; color: "#FBBF24" }
                }
            }
        }

        // 2. Toolbar Row (Search + Action Buttons)
        RowLayout {
            Layout.fillWidth: true
            spacing: 12

            Text {
                text: ":: LIBRARY ::"
                font.pixelSize: 16
                font.weight: Font.Black
                color: "#F2F2F2"
            }

            Item { Layout.fillWidth: true }

            SearchBar {
                id: searchBar
            }

            PillButton {
                text: "🔴 SCAN LIBRARY"
                isPrimary: true
                onClicked: {
                    libraryService.startScan(
                        configManager.get("music_dir", ""),
                        configManager.get("lyrics_dir", ""),
                        configManager.get("threshold", 60.0),
                        configManager.get("verify_audio", True)
                    )
                }
            }
        }

        // 3. Tracks List View & Detail Drawer Split
        RowLayout {
            Layout.fillWidth: true
            Layout.fillHeight: true
            spacing: 16

            // Left Side: Tracks ListView
            GlassCard {
                Layout.fillWidth: true
                Layout.fillHeight: true

                ListView {
                    id: tracksListView
                    anchors.fill: parent
                    anchors.margins: 8
                    clip: true
                    model: libraryService.tracks

                    delegate: Rectangle {
                        width: tracksListView.width
                        height: 44
                        radius: 4
                        color: modelData === libraryPage.selectedTrack ? "#181B1F" : (rowMouse.containsMouse ? "#121417" : "transparent")
                        border.color: modelData === libraryPage.selectedTrack ? "#FF002B" : "transparent"

                        RowLayout {
                            anchors.fill: parent
                            anchors.leftMargin: 12
                            anchors.rightMargin: 12
                            spacing: 12

                            Text {
                                text: modelData.title || modelData.file_path.split(/[\\/]/).pop()
                                font.pixelSize: 12
                                font.weight: Font.Bold
                                color: "#F2F2F2"
                                Layout.fillWidth: true
                                elide: Text.ElideRight
                            }

                            Text {
                                text: modelData.artist || "Unknown Artist"
                                font.pixelSize: 11
                                color: "#92969D"
                                Layout.preferredWidth: 140
                                elide: Text.ElideRight
                            }

                            Rectangle {
                                width: 80; height: 22; radius: 11
                                color: modelData.lyric_id ? "#132A1C" : "#2A0910"
                                border.color: modelData.lyric_id ? "#34D399" : "#FF002B"

                                Text {
                                    anchors.centerIn: parent
                                    text: modelData.lyric_id ? "MATCHED" : "MISSING"
                                    font.pixelSize: 9
                                    font.weight: Font.Bold
                                    color: modelData.lyric_id ? "#34D399" : "#F87171"
                                }
                            }
                        }

                        MouseArea {
                            id: rowMouse
                            anchors.fill: parent
                            hoverEnabled: true
                            onClicked: libraryPage.selectedTrack = modelData
                        }
                    }

                    EmptyState {
                        anchors.centerIn: parent
                        visible: tracksListView.count === 0
                    }
                }
            }

            // Right Side: Track Detail Panel
            GlassCard {
                Layout.preferredWidth: 340
                Layout.fillHeight: true

                ScrollView {
                    anchors.fill: parent
                    anchors.margins: 16
                    contentWidth: parent.width - 32

                    ColumnLayout {
                        width: parent.width
                        spacing: 16

                        Text {
                            text: ":: TRACK DETAILS ::"
                            font.pixelSize: 11
                            font.weight: Font.Bold
                            font.letterSpacing: 1.0
                            color: "#92969D"
                        }

                        GlassCard {
                            Layout.fillWidth: true
                            Layout.preferredHeight: 90
                            color: "#0B0C0E"

                            ColumnLayout {
                                anchors.fill: parent
                                anchors.margins: 12
                                spacing: 4

                                Text {
                                    text: libraryPage.selectedTrack ? (libraryPage.selectedTrack.title || "Selected Track") : "No Track Selected"
                                    font.pixelSize: 13
                                    font.weight: Font.Bold
                                    color: "#F2F2F2"
                                    elide: Text.ElideRight
                                    Layout.fillWidth: true
                                }

                                Text {
                                    text: libraryPage.selectedTrack ? (libraryPage.selectedTrack.artist + " — " + libraryPage.selectedTrack.album) : "Select a track from the library"
                                    font.pixelSize: 11
                                    color: "#92969D"
                                    elide: Text.ElideRight
                                    Layout.fillWidth: true
                                }
                            }
                        }

                        // Spectrum View Component Bridge
                        SpectrumView {
                            Layout.fillWidth: true
                            Layout.preferredHeight: 180
                            filePath: libraryPage.selectedTrack ? libraryPage.selectedTrack.file_path : ""
                        }

                        // Action Buttons
                        PillButton {
                            text: "🔴 EMBED TRACK LYRICS"
                            isPrimary: true
                            enabled: libraryPage.selectedTrack !== null && libraryPage.selectedTrack.lyric_id !== null
                            Layout.fillWidth: true
                            onClicked: {
                                if (libraryPage.selectedTrack) {
                                    lyricService.embedSelectedTracks([libraryPage.selectedTrack.id])
                                }
                            }
                        }
                    }
                }
            }
        }
    }
}
