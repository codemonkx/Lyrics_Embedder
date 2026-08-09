import QtQuick
import QtQuick.Controls

Button {
    id: control
    property bool isPrimary: false
    property bool isDestructive: false

    implicitWidth: Math.max(buttonText.implicitWidth + 28, 80)
    implicitHeight: 34

    background: Rectangle {
        radius: 17
        color: {
            if (!control.enabled) return "#181B1F"
            if (control.isPrimary) return control.down ? "#D40024" : (control.hovered ? "#FF1A40" : "#FF002B")
            if (control.isDestructive) return control.down ? "#991B1B" : (control.hovered ? "#DC2626" : "#EF4444")
            return control.down ? "#272A2F" : (control.hovered ? "#1E2228" : "#121417")
        }
        border.color: {
            if (!control.enabled) return "#272A2F"
            if (control.isPrimary || control.isDestructive) return "transparent"
            return control.hovered ? "#3D424D" : "#272A2F"
        }

        Behavior on color { ColorAnimation { duration: 120 } }
    }

    contentItem: Text {
        id: buttonText
        text: control.text
        font.pixelSize: 12
        font.weight: Font.Bold
        font.letterSpacing: 0.5
        color: {
            if (!control.enabled) return "#62666D"
            if (control.isPrimary || control.isDestructive) return "#FFFFFF"
            return control.hovered ? "#FFFFFF" : "#F2F2F2"
        }
        horizontalAlignment: Text.AlignHCenter
        verticalAlignment: Text.AlignVCenter
    }
}
