import QtQuick
import QtQuick.Controls

Rectangle {
    id: toastRoot
    property string message: ""
    property string toastType: "info" // "info", "success", "warning", "error"
    property bool active: false

    implicitWidth: toastContent.implicitWidth + 32
    implicitHeight: 36
    radius: 18

    color: {
        if (toastType === "success") return "#132A1C"
        if (toastType === "warning") return "#332200"
        if (toastType === "error") return "#2A0910"
        return "#181B1F"
    }

    border.color: {
        if (toastType === "success") return "#34D399"
        if (toastType === "warning") return "#FBBF24"
        if (toastType === "error") return "#F87171"
        return "#FF002B"
    }

    opacity: active ? 1.0 : 0.0
    scale: active ? 1.0 : 0.9

    Behavior on opacity { NumberAnimation { duration: 200 } }
    Behavior on scale { NumberAnimation { duration: 200; easing.type: Easing.OutBack } }

    Row {
        id: toastContent
        anchors.centerIn: parent
        spacing: 8

        Text {
            text: {
                if (toastRoot.toastType === "success") return "✓"
                if (toastRoot.toastType === "warning") return "⚠️"
                if (toastRoot.toastType === "error") return "✕"
                return "ℹ️"
            }
            font.pixelSize: 11
            color: {
                if (toastRoot.toastType === "success") return "#34D399"
                if (toastRoot.toastType === "warning") return "#FBBF24"
                if (toastRoot.toastType === "error") return "#F87171"
                return "#FF002B"
            }
        }

        Text {
            text: toastRoot.message
            font.pixelSize: 11
            font.weight: Font.Medium
            color: "#F2F2F2"
        }
    }

    function show(msg, type, durationMs) {
        toastRoot.message = msg
        toastRoot.toastType = type || "info"
        toastRoot.active = true
        autoHideTimer.interval = durationMs || 3000
        autoHideTimer.restart()
    }

    Timer {
        id: autoHideTimer
        repeat: false
        onTriggered: toastRoot.active = false
    }
}
