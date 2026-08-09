import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "../components"

Item {
    id: settingsPage

    ScrollView {
        anchors.fill: parent
        anchors.margins: 16
        contentWidth: parent.width - 32

        ColumnLayout {
            width: parent.width
            spacing: 16

            // Header
            RowLayout {
                Layout.fillWidth: true
                spacing: 12

                Text {
                    text: "SYSTEM PREFERENCES"
                    font.pixelSize: 14
                    font.weight: Font.Black
                    font.letterSpacing: 1.0
                    color: "#F2F2F2"
                }

                Text { text: "•"; color: "#62666D" }

                Text {
                    text: "Configure library folders, real-time filesystem monitoring, and database management"
                    font.pixelSize: 12
                    color: "#92969D"
                }
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
                        text: "MUSIC & LYRICS DIRECTORIES"
                        font.pixelSize: 10
                        font.weight: Font.Bold
                        color: "#FF002B"
                    }

                    RowLayout {
                        Layout.fillWidth: true
                        spacing: 12

                        Text { text: "Music Directory:"; font.pixelSize: 12; color: "#F2F2F2"; Layout.preferredWidth: 120 }
                        
                        TextField {
                            id: musicDirInput
                            Layout.fillWidth: true
                            text: typeof configManager !== "undefined" && configManager ? configManager.get("music_dir", "") : ""
                            color: "#F2F2F2"
                            background: Rectangle { color: "#0B0C0E"; radius: 4; border.color: "#272A2F" }
                            onEditingFinished: {
                                if (typeof configManager !== "undefined" && configManager) {
                                    configManager.set("music_dir", musicDirInput.text)
                                }
                            }
                        }

                        PillButton {
                            text: "📁 BROWSE"
                            onClicked: {
                                if (typeof libraryService !== "undefined" && libraryService) {
                                    libraryService.browseFolder("music")
                                }
                            }
                        }
                    }

                    RowLayout {
                        Layout.fillWidth: true
                        spacing: 12

                        Text { text: "Lyrics Directory:"; font.pixelSize: 12; color: "#F2F2F2"; Layout.preferredWidth: 120 }
                        
                        TextField {
                            id: lyricsDirInput
                            Layout.fillWidth: true
                            text: typeof configManager !== "undefined" && configManager ? configManager.get("lyrics_dir", "") : ""
                            color: "#F2F2F2"
                            background: Rectangle { color: "#0B0C0E"; radius: 4; border.color: "#272A2F" }
                            onEditingFinished: {
                                if (typeof configManager !== "undefined" && configManager) {
                                    configManager.set("lyrics_dir", lyricsDirInput.text)
                                }
                            }
                        }

                        PillButton {
                            text: "📝 BROWSE"
                            onClicked: {
                                if (typeof libraryService !== "undefined" && libraryService) {
                                    libraryService.browseFolder("lyrics")
                                }
                            }
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
                        text: "REAL-TIME MONITORING & SAFETY"
                        font.pixelSize: 10
                        font.weight: Font.Bold
                        color: "#FF002B"
                    }

                    CheckBox {
                        text: "Enable Watchdog Real-Time Library Monitoring (Debounced 500ms)"
                        checked: typeof configManager !== "undefined" && configManager ? configManager.get("monitoring_enabled", false) : false
                        onCheckedChanged: {
                            if (typeof configManager !== "undefined" && configManager) {
                                configManager.set("monitoring_enabled", checked)
                            }
                        }
                    }
                }
            }

            // Reset Database Button
            PillButton {
                text: "⚠️ RESET DATABASE & CACHE"
                isDestructive: true
                onClicked: {
                    if (typeof libraryService !== "undefined" && libraryService) {
                        libraryService.resetLibrary()
                    }
                }
            }
        }
    }
}
