import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "../components"

Item {
    id: analysisPage

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 20
        spacing: 16

        RowLayout {
            Layout.fillWidth: true
            Text {
                text: ":: AUDIO INTEGRITY & SPECTRAL INSPECTOR ::"
                font.pixelSize: 16
                font.weight: Font.Black
                color: "#F2F2F2"
            }
            Item { Layout.fillWidth: true }
            PillButton {
                text: "🔴 RUN FULL AUDIO INTEGRITY SCAN"
                isPrimary: true
                onClicked: {
                    libraryService.startScan(
                        configManager.get("music_dir", ""),
                        "",
                        0.0,
                        true
                    )
                }
            }
        }

        GlassCard {
            Layout.fillWidth: true
            Layout.fillHeight: true

            ListView {
                anchors.fill: parent
                anchors.margins: 12
                clip: true
                model: libraryService.tracks

                delegate: Rectangle {
                    width: parent.width
                    height: 50
                    color: index % 2 === 0 ? "#121417" : "#0B0C0E"
                    radius: 4

                    RowLayout {
                        anchors.fill: parent
                        anchors.leftMargin: 12
                        anchors.rightMargin: 12
                        spacing: 16

                        Text {
                            text: modelData.file_path.split(/[\\/]/).pop()
                            font.pixelSize: 12
                            font.weight: Font.Bold
                            color: "#F2F2F2"
                            Layout.fillWidth: true
                            elide: Text.ElideRight
                        }

                        Text {
                            text: modelData.sample_rate ? (modelData.sample_rate + " Hz") : "-"
                            font.pixelSize: 11
                            color: "#92969D"
                            Layout.preferredWidth: 80
                        }

                        Text {
                            text: modelData.spectral_cutoff ? (Math.round(modelData.spectral_cutoff) + " Hz") : "-"
                            font.pixelSize: 11
                            color: "#F2F2F2"
                            Layout.preferredWidth: 90
                        }

                        Rectangle {
                            width: 110; height: 24; radius: 12
                            color: modelData.legit === 1 ? "#132A1C" : (modelData.legit === 0 ? "#332200" : "#181B1F")
                            border.color: modelData.legit === 1 ? "#34D399" : (modelData.legit === 0 ? "#FBBF24" : "#272A2F")

                            Text {
                                anchors.centerIn: parent
                                text: modelData.legit === 1 ? "GENUINE" : (modelData.legit === 0 ? "POSSIBLE LOSSLESS ANOMALY" : "UNVERIFIED")
                                font.pixelSize: 8
                                font.weight: Font.Bold
                                color: modelData.legit === 1 ? "#34D399" : (modelData.legit === 0 ? "#FBBF24" : "#92969D")
                            }
                        }
                    }
                }
            }
        }
    }
}
