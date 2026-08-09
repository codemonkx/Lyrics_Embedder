import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "../components"

Item {
    id: settingsPage

    ScrollView {
        anchors.fill: parent
        anchors.margins: 20
        contentWidth: parent.width - 40

        ColumnLayout {
            width: parent.width
            spacing: 20

            Text {
                text: ":: PREFERENCES & CONFIGURATION ::"
                font.pixelSize: 16
                font.weight: Font.Black
                color: "#F2F2F2"
            }

            // Group 1: Music Folders
            GlassCard {
                Layout.fillWidth: true
                Layout.preferredHeight: 140

                ColumnLayout {
                    anchors.fill: parent
                    anchors.margins: 16
                    spacing: 12

                    Text {
                        text: ":: MUSIC & LYRICS DIRECTORIES ::"
                        font.pixelSize: 11
                        font.weight: Font.Bold
                        color: "#FF002B"
                    }

                    RowLayout {
                        Layout.fillWidth: true
                        Text { text: "Music Directory:"; font.pixelSize: 12; color: "#F2F2F2"; Layout.preferredWidth: 120 }
                        TextField {
                            id: musicDirInput
                            Layout.fillWidth: true
                            text: configManager.get("music_dir", "")
                            color: "#F2F2F2"
                            background: Rectangle { color: "#0B0C0E"; radius: 4; border.color: "#272A2F" }
                            onEditingFinished: configManager.set("music_dir", musicDirInput.text)
                        }
                    }

                    RowLayout {
                        Layout.fillWidth: true
                        Text { text: "Lyrics Directory:"; font.pixelSize: 12; color: "#F2F2F2"; Layout.preferredWidth: 120 }
                        TextField {
                            id: lyricsDirInput
                            Layout.fillWidth: true
                            text: configManager.get("lyrics_dir", "")
                            color: "#F2F2F2"
                            background: Rectangle { color: "#0B0C0E"; radius: 4; border.color: "#272A2F" }
                            onEditingFinished: configManager.set("lyrics_dir", lyricsDirInput.text)
                        }
                    }
                }
            }

            // Group 2: Watchdog & Safety
            GlassCard {
                Layout.fillWidth: true
                Layout.preferredHeight: 110

                ColumnLayout {
                    anchors.fill: parent
                    anchors.margins: 16
                    spacing: 12

                    Text {
                        text: ":: REAL-TIME MONITORING & SAFETY ::"
                        font.pixelSize: 11
                        font.weight: Font.Bold
                        color: "#FF002B"
                    }

                    CheckBox {
                        text: "Enable Watchdog Real-Time Library Monitoring (Debounced 500ms)"
                        checked: configManager.get("monitoring_enabled", false)
                        onCheckedChanged: configManager.set("monitoring_enabled", checked)
                    }
                }
            }

            // Reset Database Button
            PillButton {
                text: "⚠️ RESET DATABASE & CACHE"
                isDestructive: true
                onClicked: libraryService.resetLibrary()
            }
        }
    }
}
