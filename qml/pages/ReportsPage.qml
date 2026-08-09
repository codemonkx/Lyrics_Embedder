import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "../components"

Item {
    id: reportsPage

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 16
        spacing: 12

        // Header
        RowLayout {
            Layout.fillWidth: true
            spacing: 12

            Text {
                text: "REPORTS & PROCESS LOGS"
                font.pixelSize: 14
                font.weight: Font.Black
                font.letterSpacing: 1.0
                color: "#F2F2F2"
            }

            Text { text: "•"; color: "#62666D" }

            Text {
                text: "Export library statistics and monitor real-time background threads"
                font.pixelSize: 12
                color: "#92969D"
            }
        }

        // Export Actions Card
        GlassCard {
            Layout.fillWidth: true
            Layout.preferredHeight: 84

            ColumnLayout {
                anchors.fill: parent
                anchors.margins: 12
                spacing: 6

                Text {
                    text: "EXPORT LIBRARY SUMMARY"
                    font.pixelSize: 10
                    font.weight: Font.Bold
                    color: "#62666D"
                }

                RowLayout {
                    spacing: 12
                    PillButton { text: "📄 EXPORT HTML REPORT" }
                    PillButton { text: "📝 EXPORT TXT SUMMARY" }
                    PillButton { text: "⚙️ EXPORT JSON DATA" }
                }
            }
        }

        // Process Log Console
        GlassCard {
            Layout.fillWidth: true
            Layout.fillHeight: true

            ColumnLayout {
                anchors.fill: parent
                anchors.margins: 12
                spacing: 8

                Text {
                    text: "LIVE PROCESS LOG STREAM"
                    font.pixelSize: 10
                    font.weight: Font.Bold
                    color: "#62666D"
                }

                ScrollView {
                    Layout.fillWidth: true
                    Layout.fillHeight: true

                    TextArea {
                        id: logArea
                        readOnly: true
                        font.family: "Courier New, monospace"
                        font.pixelSize: 11
                        color: "#34D399"
                        background: Rectangle { color: "#0B0C0E"; radius: 4; border.color: "#272A2F" }
                        text: "[LOG START] Initialized LyricForge Pro Engine...\n[SYSTEM] Ready."
                    }
                }
            }
        }
    }
}
