import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "../components"

Item {
    id: libraryPage

    property var selectedTrack: null

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 16
        spacing: 12

        // 1. Compact Library Summary Header
        LibraryHeader {
            Layout.fillWidth: true
        }

        // 2. Main Content Split: High-Density Track Table + Contextual Inspector
        RowLayout {
            Layout.fillWidth: true
            Layout.fillHeight: true
            spacing: 12

            // High-Density Track List Table
            TrackTable {
                id: trackTable
                Layout.fillWidth: true
                Layout.fillHeight: true
                selectedTrack: libraryPage.selectedTrack
                onTrackSelected: function(t) {
                    libraryPage.selectedTrack = t
                }
            }

            // Contextual Track Inspector Drawer
            TrackInspector {
                id: trackInspector
                Layout.fillHeight: true
                track: libraryPage.selectedTrack
            }
        }
    }
}
