import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "components"
import "pages"

ApplicationWindow {
    id: window
    width: 1260
    height: 800
    minimumWidth: 960
    minimumHeight: 600
    visible: true
    title: "LyricForge Pro"
    flags: Qt.Window | Qt.FramelessWindowHint | Qt.WindowMinMaxButtonsHint | Qt.WindowSystemMenuHint

    background: Rectangle {
        color: "#0B0C0E"
        radius: window.visibility === Window.Maximized ? 0 : 8
        border.color: "#272A2F"
        border.width: 1
    }

    // Global Keyboard Shortcuts (Ctrl+K, Ctrl+F, Ctrl+R, Esc)
    Shortcut {
        sequence: "Ctrl+K"
        onActivated: searchInputGlobal.forceActiveFocus()
    }
    Shortcut {
        sequence: "Ctrl+F"
        onActivated: searchInputGlobal.forceActiveFocus()
    }
    Shortcut {
        sequence: "Ctrl+R"
        onActivated: {
            if (typeof libraryService !== "undefined" && libraryService && typeof configManager !== "undefined" && configManager) {
                toastNotification.show("Scanning music library...", "info", 3000)
                libraryService.startScan(
                    configManager.get("music_dir", ""),
                    configManager.get("lyrics_dir", ""),
                    configManager.get("threshold", 60.0),
                    configManager.get("verify_audio", true)
                )
            }
        }
    }
    Shortcut {
        sequence: "Escape"
        onActivated: {
            if (libraryPage.selectedTrack) libraryPage.selectedTrack = null
        }
    }

    ColumnLayout {
        anchors.fill: parent
        spacing: 0

        // Custom Frameless HeaderBar (Draggable via window.startSystemMove())
        Rectangle {
            Layout.fillWidth: true
            Layout.preferredHeight: 44
            color: "#0B0C0E"
            border.color: "#272A2F"
            border.width: 1

            MouseArea {
                anchors.fill: parent
                onPressed: window.startSystemMove()
                onDoubleClicked: {
                    if (window.visibility === Window.Maximized) window.showNormal()
                    else window.showMaximized()
                }
            }

            RowLayout {
                anchors.fill: parent
                anchors.leftMargin: 16
                anchors.rightMargin: 16
                spacing: 12

                Rectangle { width: 8; height: 8; radius: 4; color: "#FF002B" }

                Text {
                    text: "NOTHING // LYRICFORGE PRO"
                    font.pixelSize: 11
                    font.weight: Font.Black
                    font.letterSpacing: 1.5
                    color: "#F2F2F2"
                }

                Rectangle {
                    width: 60; height: 18; radius: 9
                    color: "#181B1F"
                    border.color: "#272A2F"
                    Text {
                        anchors.centerIn: parent
                        text: "v2.0 PRO"
                        font.pixelSize: 8
                        font.weight: Font.Bold
                        color: "#92969D"
                    }
                }

                Item { Layout.fillWidth: true }

                // Search Bar Input (Ctrl+K)
                Rectangle {
                    width: 220; height: 28; radius: 14
                    color: "#121417"
                    border.color: searchInputGlobal.activeFocus ? "#FF002B" : "#272A2F"

                    Row {
                        anchors.fill: parent
                        anchors.leftMargin: 10
                        anchors.rightMargin: 10
                        spacing: 6

                        Text { text: "🔍"; font.pixelSize: 10; anchors.verticalCenter: parent.verticalCenter }

                        TextInput {
                            id: searchInputGlobal
                            width: parent.width - 40
                            anchors.verticalCenter: parent.verticalCenter
                            font.pixelSize: 11
                            color: "#F2F2F2"
                            selectByMouse: true

                            Text {
                                text: "Search (Ctrl+K)..."
                                font.pixelSize: 11
                                color: "#62666D"
                                visible: searchInputGlobal.text.length === 0
                                anchors.verticalCenter: parent.verticalCenter
                            }
                        }
                    }
                }

                // Window Control Buttons
                RowLayout {
                    spacing: 4

                    Button {
                        implicitWidth: 32; implicitHeight: 28
                        background: Rectangle { color: parent.hovered ? "#181B1F" : "transparent"; radius: 4 }
                        contentItem: Text { text: "—"; color: "#92969D"; horizontalAlignment: Text.AlignHCenter; verticalAlignment: Text.AlignVCenter }
                        onClicked: window.showMinimized()
                    }

                    Button {
                        implicitWidth: 32; implicitHeight: 28
                        background: Rectangle { color: parent.hovered ? "#181B1F" : "transparent"; radius: 4 }
                        contentItem: Text { text: window.visibility === Window.Maximized ? "❐" : "☐"; color: "#92969D"; horizontalAlignment: Text.AlignHCenter; verticalAlignment: Text.AlignVCenter }
                        onClicked: {
                            if (window.visibility === Window.Maximized) window.showNormal()
                            else window.showMaximized()
                        }
                    }

                    Button {
                        implicitWidth: 32; implicitHeight: 28
                        background: Rectangle { color: parent.hovered ? "#FF002B" : "transparent"; radius: 4 }
                        contentItem: Text { text: "✕"; color: parent.hovered ? "#FFFFFF" : "#92969D"; horizontalAlignment: Text.AlignHCenter; verticalAlignment: Text.AlignVCenter }
                        onClicked: window.close()
                    }
                }
            }
        }

        // Workspace Container (Sidebar + Stacked Pages)
        RowLayout {
            Layout.fillWidth: true
            Layout.fillHeight: true
            spacing: 0

            Sidebar {
                id: mainSidebar
                Layout.fillHeight: true
                currentIndex: stackLayout.currentIndex
                onPageSelected: function(index) {
                    stackLayout.currentIndex = index
                }
            }

            StackLayout {
                id: stackLayout
                Layout.fillWidth: true
                Layout.fillHeight: true
                currentIndex: 0

                LibraryPage { id: libraryPage }
                AnalysisPage { id: analysisPage }
                ReportsPage { id: reportsPage }
                SettingsPage { id: settingsPage }
            }
        }
    }

    // Floating Toast Notification Overlay
    ToastNotification {
        id: toastNotification
        anchors.bottom: parent.bottom
        anchors.right: parent.right
        anchors.margins: 24
        z: 999
    }

    // 8-Directional Frameless Border Edge Resize Handles
    MouseArea {
        anchors.top: parent.top
        anchors.left: parent.left
        anchors.right: parent.right
        height: 6
        cursorShape: Qt.SizeVerCursor
        onPressed: window.startSystemResize(Qt.TopEdge)
    }
    MouseArea {
        anchors.bottom: parent.bottom
        anchors.left: parent.left
        anchors.right: parent.right
        height: 6
        cursorShape: Qt.SizeVerCursor
        onPressed: window.startSystemResize(Qt.BottomEdge)
    }
    MouseArea {
        anchors.top: parent.top
        anchors.bottom: parent.bottom
        anchors.left: parent.left
        width: 6
        cursorShape: Qt.SizeHorCursor
        onPressed: window.startSystemResize(Qt.LeftEdge)
    }
    MouseArea {
        anchors.top: parent.top
        anchors.bottom: parent.bottom
        anchors.right: parent.right
        width: 6
        cursorShape: Qt.SizeHorCursor
        onPressed: window.startSystemResize(Qt.RightEdge)
    }
    MouseArea {
        anchors.top: parent.top
        anchors.left: parent.left
        width: 10; height: 10
        cursorShape: Qt.SizeFDiagCursor
        onPressed: window.startSystemResize(Qt.TopEdge | Qt.LeftEdge)
    }
    MouseArea {
        anchors.top: parent.top
        anchors.right: parent.right
        width: 10; height: 10
        cursorShape: Qt.SizeBDiagCursor
        onPressed: window.startSystemResize(Qt.TopEdge | Qt.RightEdge)
    }
    MouseArea {
        anchors.bottom: parent.bottom
        anchors.left: parent.left
        width: 10; height: 10
        cursorShape: Qt.SizeBDiagCursor
        onPressed: window.startSystemResize(Qt.BottomEdge | Qt.LeftEdge)
    }
    MouseArea {
        anchors.bottom: parent.bottom
        anchors.right: parent.right
        width: 10; height: 10
        cursorShape: Qt.SizeFDiagCursor
        onPressed: window.startSystemResize(Qt.BottomEdge | Qt.RightEdge)
    }
}
