import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "../components"

Item {
    id: reportsPage

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 20
        spacing: 16

        Text {
            text: ":: REPORTS & LOGS ::"
            font.pixelSize: 16
            font.weight: Font.Black
            color: "#F2F2F2"
        }

        GlassCard {
            Layout.fillWidth: true
            Layout.preferredHeight: 90

            ColumnLayout {
                anchors.fill: parent
                anchors.margins: 16
                spacing: 8

                Text {
                    text: ":: EXPORT LIBRARY SUMMARY REPORT ::"
                    font.pixelSize: 11
                    font.weight: Font.Bold
                    color: "#92969D"
                }

                RowLayout {
                    spacing: 12
                    PillButton { text: "📄 EXPORT HTML REPORT" }
                    PillButton { text: "📝 EXPORT TXT SUMMARY" }
                    PillButton { text: "⚙️ EXPORT JSON DATA" }
                }
            }
        }

        GlassCard {
            Layout.fillWidth: true
            Layout.fillHeight: true

            ColumnLayout {
                anchors.fill: parent
                anchors.margins: 16
                spacing: 8

                Text {
                    text: ":: PROCESS LOG CONSOLE ::"
                    font.pixelSize: 11
                    font.weight: Font.Bold
                    color: "#92969D"
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
                        background: Rectangle { color: "#0B0C0E"; radius: 4 }
                        text: "[LOG START] Initialized LyricForge Pro Application Engine...\nReady."
                    }
                }
            }
        }
    }
}
