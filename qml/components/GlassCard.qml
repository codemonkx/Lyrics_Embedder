import QtQuick
import QtQuick.Controls

Rectangle {
    id: root
    color: "#121417"
    border.color: "#272A2F"
    border.width: 1
    radius: 8

    Behavior on border.color {
        ColorAnimation { duration: 150 }
    }
}
