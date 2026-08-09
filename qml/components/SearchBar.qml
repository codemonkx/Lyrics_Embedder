import QtQuick
import QtQuick.Controls

Rectangle {
    id: searchRoot
    property string text: ""
    signal searchTextChanged(string searchText)

    implicitWidth: 240
    implicitHeight: 32
    radius: 16
    color: "#121417"
    border.color: searchInput.activeFocus ? "#FF002B" : "#272A2F"

    Row {
        anchors.fill: parent
        anchors.leftMargin: 12
        anchors.rightMargin: 12
        spacing: 8

        Text {
            text: "🔍"
            font.pixelSize: 11
            anchors.verticalCenter: parent.verticalCenter
        }

        TextInput {
            id: searchInput
            width: parent.width - 40
            anchors.verticalCenter: parent.verticalCenter
            font.pixelSize: 12
            color: "#F2F2F2"
            selectByMouse: true

            Text {
                text: "Search tracks or lyrics..."
                font.pixelSize: 12
                color: "#62666D"
                visible: searchInput.text.length === 0
                anchors.verticalCenter: parent.verticalCenter
            }

            onTextChanged: {
                searchRoot.text = searchInput.text
                searchRoot.searchTextChanged(searchInput.text)
            }
        }
    }
}
