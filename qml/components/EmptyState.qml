import QtQuick
import QtQuick.Controls

Item {
    id: emptyRoot
    property string iconSymbol: "🔴"
    property string title: "NO MUSIC LIBRARY SCANNED"
    property string subtitle: "Select your music library folder to scan audio tracks and match lyrics."
    property string buttonText: "CHOOSE MUSIC FOLDER"
    signal actionClicked()

    implicitWidth: 400
    implicitHeight: 300

    Column {
        anchors.centerIn: parent
        spacing: 14
        width: Math.min(parent.width - 40, 420)

        Text {
            text: emptyRoot.iconSymbol
            font.pixelSize: 36
            anchors.horizontalCenter: parent.horizontalCenter
        }

        Text {
            text: emptyRoot.title
            font.pixelSize: 13
            font.weight: Font.Black
            font.letterSpacing: 1.2
            color: "#F2F2F2"
            anchors.horizontalCenter: parent.horizontalCenter
        }

        Text {
            text: emptyRoot.subtitle
            font.pixelSize: 12
            color: "#92969D"
            horizontalAlignment: Text.AlignHCenter
            wrapMode: Text.WordWrap
            width: parent.width
            anchors.horizontalCenter: parent.horizontalCenter
        }

        Item { width: 1; height: 8 }

        PillButton {
            text: emptyRoot.buttonText
            isPrimary: true
            anchors.horizontalCenter: parent.horizontalCenter
            onClicked: emptyRoot.actionClicked()
        }
    }
}
