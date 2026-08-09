import QtQuick
import QtQuick.Controls

Rectangle {
    id: statusRoot
    property string statusText: "UNMATCHED"
    property string statusType: "missing" // "matched", "missing", "warning", "neutral"

    implicitWidth: badgeRow.implicitWidth + 16
    implicitHeight: 22
    radius: 11

    color: {
        if (statusType === "matched") return "#132A1C"
        if (statusType === "warning") return "#332200"
        if (statusType === "missing") return "#2A0910"
        return "#181B1F"
    }

    border.color: {
        if (statusType === "matched") return "#34D399"
        if (statusType === "warning") return "#FBBF24"
        if (statusType === "missing") return "#F87171"
        return "#272A2F"
    }

    Row {
        id: badgeRow
        anchors.centerIn: parent
        spacing: 6

        Rectangle {
            width: 6; height: 6
            radius: 3
            anchors.verticalCenter: parent.verticalCenter
            color: {
                if (statusType === "matched") return "#34D399"
                if (statusType === "warning") return "#FBBF24"
                if (statusType === "missing") return "#F87171"
                return "#92969D"
            }
        }

        Text {
            text: statusRoot.statusText
            font.pixelSize: 9
            font.weight: Font.Bold
            font.letterSpacing: 0.5
            anchors.verticalCenter: parent.verticalCenter
            color: {
                if (statusType === "matched") return "#34D399"
                if (statusType === "warning") return "#FBBF24"
                if (statusType === "missing") return "#F87171"
                return "#92969D"
            }
        }
    }
}
