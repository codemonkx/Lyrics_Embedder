import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "../components"

Item {
    id: analysisPage

    property var selectedTrack: null
    property var analysisResult: null

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 16
        spacing: 12

        // Header
        RowLayout {
            Layout.fillWidth: true
            spacing: 12

            Text {
                text: "AUDIO SPECTRAL ANALYSIS"
                font.pixelSize: 14
                font.weight: Font.Black
                font.letterSpacing: 1.0
                color: "#F2F2F2"
            }

            Text { text: "•"; color: "#62666D" }

            Text {
                text: "Inspect Nyquist cutoff frequencies and lossy transcode anomalies"
                font.pixelSize: 12
                color: "#92969D"
            }

            Item { Layout.fillWidth: true }

            PillButton {
                text: "🔴 RUN SPECTRAL INSPECTION"
                isPrimary: true
                onClicked: {
                    if (typeof libraryService !== "undefined" && libraryService && typeof configManager !== "undefined" && configManager) {
                        libraryService.startScan(configManager.get("music_dir", ""), "", 0.0, true)
                    }
                }
            }
        }

        // Main Body: Audio Inspector Split (Track List vs Spectrum & Scientific Evidence)
        RowLayout {
            Layout.fillWidth: true
            Layout.fillHeight: true
            spacing: 12

            // Left Side: Tracks Inspector List
            GlassCard {
                Layout.preferredWidth: 360
                Layout.fillHeight: true

                ListView {
                    id: analysisListView
                    anchors.fill: parent
                    anchors.margins: 8
                    clip: true
                    model: typeof libraryService !== "undefined" && libraryService ? libraryService.tracks : []

                    delegate: Rectangle {
                        width: analysisListView.width
                        height: 40
                        color: modelData === analysisPage.selectedTrack ? "#181B1F" : (rowM.containsMouse ? "#15181D" : "transparent")
                        radius: 4

                        RowLayout {
                            anchors.fill: parent
                            anchors.leftMargin: 10
                            anchors.rightMargin: 10
                            spacing: 8

                            Text {
                                text: modelData.title || (modelData.file_path ? modelData.file_path.split(/[\\/]/).pop() : "Untitled")
                                font.pixelSize: 11
                                font.weight: Font.Bold
                                color: "#F2F2F2"
                                Layout.fillWidth: true
                                elide: Text.ElideRight
                            }

                            StatusBadge {
                                statusText: modelData.legit === 1 ? "GENUINE" : (modelData.legit === 0 ? "ANOMALY" : "UNVERIFIED")
                                statusType: modelData.legit === 1 ? "matched" : (modelData.legit === 0 ? "warning" : "neutral")
                                Layout.preferredWidth: 90
                            }
                        }

                        MouseArea {
                            id: rowM
                            anchors.fill: parent
                            hoverEnabled: true
                            onClicked: {
                                analysisPage.selectedTrack = modelData
                                if (typeof analysisService !== "undefined" && analysisService) {
                                    analysisPage.analysisResult = analysisService.analyzeFile(modelData.file_path)
                                }
                            }
                        }
                    }
                }
            }

            // Right Side: Large Spectrum View & Evidence Breakdown
            GlassCard {
                Layout.fillWidth: true
                Layout.fillHeight: true

                ColumnLayout {
                    anchors.fill: parent
                    anchors.margins: 16
                    spacing: 14

                    // Large Interactive Spectrum Provider Graph
                    SpectrumView {
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                        filePath: analysisPage.selectedTrack ? analysisPage.selectedTrack.file_path : ""
                    }

                    // Empirical Observation vs Interpretation Evidence Panel
                    Rectangle {
                        Layout.fillWidth: true
                        Layout.preferredHeight: 120
                        color: "#0B0C0E"
                        border.color: "#272A2F"
                        radius: 6

                        ColumnLayout {
                            anchors.fill: parent
                            anchors.margins: 12
                            spacing: 6

                            Text {
                                text: "SPECTRAL EVIDENCE BREAKDOWN"
                                font.pixelSize: 10
                                font.weight: Font.Bold
                                color: "#62666D"
                            }

                            RowLayout {
                                spacing: 8
                                Text { text: "OBSERVATION:"; font.pixelSize: 11; font.weight: Font.Bold; color: "#FF002B" }
                                Text {
                                    text: analysisPage.analysisResult ? (analysisPage.analysisResult.observation || "No analysis run.") : "Select a track to inspect frequency cutoff profile."
                                    font.pixelSize: 11
                                    color: "#F2F2F2"
                                    Layout.fillWidth: true
                                    elide: Text.ElideRight
                                }
                            }

                            RowLayout {
                                spacing: 8
                                Text { text: "INTERPRETATION:"; font.pixelSize: 11; font.weight: Font.Bold; color: "#34D399" }
                                Text {
                                    text: analysisPage.analysisResult ? (analysisPage.analysisResult.interpretation || "No interpretation.") : "System will analyze attenuation and brickwall drop points."
                                    font.pixelSize: 11
                                    color: "#F2F2F2"
                                    Layout.fillWidth: true
                                    elide: Text.ElideRight
                                }
                            }

                            RowLayout {
                                spacing: 8
                                Text { text: "CONFIDENCE RATING:"; font.pixelSize: 11; font.weight: Font.Bold; color: "#FBBF24" }
                                Text {
                                    text: analysisPage.analysisResult ? (analysisPage.analysisResult.confidence + "% confidence level") : "-"
                                    font.pixelSize: 11
                                    color: "#FBBF24"
                                }
                            }
                        }
                    }
                }
            }
        }
    }
}
