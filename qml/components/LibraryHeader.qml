import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Rectangle {
    id: headerRoot
    implicitHeight: 48
    color: "#121417"
    border.color: "#272A2F"
    border.width: 1
    radius: 6

    property int totalCount: libraryService ? libraryService.totalTracks : 0
    property int matchedCount: libraryService ? libraryService.matchedTracks : 0
    property int unmatchedCount: libraryService ? libraryService.unmatchedTracks : 0
    property int suspiciousCount: libraryService ? libraryService.suspiciousTracks : 0

    RowLayout {
        anchors.fill: parent
        anchors.leftMargin: 16
        anchors.rightMargin: 16
        spacing: 16

        // Page Title & Summary
        RowLayout {
            spacing: 10
            Text {
                text: "LIBRARY"
                font.pixelSize: 14
                font.weight: Font.Black
                font.letterSpacing: 1.0
                color: "#F2F2F2"
            }

            Text {
                text: "•"
                font.pixelSize: 12
                color: "#62666D"
            }

            Text {
                text: headerRoot.totalCount.toLocaleString() + " tracks  ·  " +
                      headerRoot.matchedCount.toLocaleString() + " matched  ·  " +
                      headerRoot.unmatchedCount.toLocaleString() + " unmatched" +
                      (headerRoot.suspiciousCount > 0 ? ("  ·  " + headerRoot.suspiciousCount + " need review") : "")
                font.pixelSize: 12
                color: "#92969D"
            }
        }

        Item { Layout.fillWidth: true }

        // Primary Scan Action
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
}
