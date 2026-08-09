import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Rectangle {
    id: headerRoot
    implicitHeight: pathBanner.visible ? 84 : 48
    color: "#121417"
    border.color: "#272A2F"
    border.width: 1
    radius: 6

    property int totalCount: libraryService ? libraryService.totalTracks : 0
    property int matchedCount: libraryService ? libraryService.matchedTracks : 0
    property int unmatchedCount: libraryService ? libraryService.unmatchedTracks : 0
    property int suspiciousCount: libraryService ? libraryService.suspiciousTracks : 0
    property string musicPath: libraryService ? libraryService.musicDir : ""
    property string lyricsPath: libraryService ? libraryService.lyricsDir : ""

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 10
        spacing: 8

        // Top Row: Title + Stats Summary + Direct Folder Actions
        RowLayout {
            Layout.fillWidth: true
            spacing: 12

            RowLayout {
                spacing: 8
                Text {
                    text: "LIBRARY"
                    font.pixelSize: 13
                    font.weight: Font.Black
                    font.letterSpacing: 1.0
                    color: "#F2F2F2"
                }

                Text { text: "•"; font.pixelSize: 10; color: "#62666D" }

                Text {
                    text: headerRoot.totalCount.toLocaleString() + " tracks  ·  " +
                          headerRoot.matchedCount.toLocaleString() + " matched  ·  " +
                          headerRoot.unmatchedCount.toLocaleString() + " unmatched" +
                          (headerRoot.suspiciousCount > 0 ? ("  ·  " + headerRoot.suspiciousCount + " need review") : "")
                    font.pixelSize: 11
                    color: "#92969D"
                }
            }

            Item { Layout.fillWidth: true }

            // Direct Folder Pickers
            PillButton {
                text: "📁 MUSIC FOLDER"
                onClicked: {
                    if (typeof libraryService !== "undefined" && libraryService) {
                        libraryService.browseFolder("music")
                    }
                }
            }

            PillButton {
                text: "📝 LYRICS FOLDER"
                onClicked: {
                    if (typeof libraryService !== "undefined" && libraryService) {
                        libraryService.browseFolder("lyrics")
                    }
                }
            }

            PillButton {
                text: "🔴 SCAN LIBRARY"
                isPrimary: true
                onClicked: {
                    if (typeof libraryService !== "undefined" && libraryService && typeof configManager !== "undefined" && configManager) {
                        libraryService.startScan(
                            configManager.get("music_dir", ""),
                            configManager.get("lyrics_dir", ""),
                            configManager.get("threshold", 60.0),
                            configManager.get("verify_audio", true)
                        )
                    }
                }
            }
        }

        // Active Folder Paths Banner Row
        Rectangle {
            id: pathBanner
            Layout.fillWidth: true
            Layout.preferredHeight: 26
            color: "#0B0C0E"
            border.color: "#272A2F"
            radius: 4
            visible: headerRoot.musicPath.length > 0 || headerRoot.lyricsPath.length > 0

            RowLayout {
                anchors.fill: parent
                anchors.leftMargin: 10
                anchors.rightMargin: 10
                spacing: 12

                Text {
                    text: "📁 Music: " + (headerRoot.musicPath ? headerRoot.musicPath : "Not Configured")
                    font.pixelSize: 10
                    font.weight: Font.Medium
                    color: headerRoot.musicPath ? "#34D399" : "#62666D"
                    elide: Text.ElideMiddle
                    Layout.fillWidth: true
                }

                Text { text: "|" ; color: "#272A2F" }

                Text {
                    text: "📝 Lyrics: " + (headerRoot.lyricsPath ? headerRoot.lyricsPath : "Not Configured")
                    font.pixelSize: 10
                    font.weight: Font.Medium
                    color: headerRoot.lyricsPath ? "#34D399" : "#62666D"
                    elide: Text.ElideMiddle
                    Layout.fillWidth: true
                }
            }
        }
    }
}
