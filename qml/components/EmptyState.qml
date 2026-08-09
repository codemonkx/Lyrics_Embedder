import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Item {
    id: emptyRoot
    property string iconSymbol: "🔴"
    property string title: "NO MUSIC LIBRARY SCANNED"
    property string subtitle: "Select your local music library and lyrics directory to start automatic matching and audio inspection."
    signal actionClicked()

    implicitWidth: 420
    implicitHeight: 280

    Column {
        anchors.centerIn: parent
        spacing: 12
        width: Math.min(parent.width - 40, 440)

        Text {
            text: emptyRoot.iconSymbol
            font.pixelSize: 32
            anchors.horizontalCenter: parent.horizontalCenter
        }

        Text {
            text: emptyRoot.title
            font.pixelSize: 13
            font.weight: Font.Black
            font.letterSpacing: 1.0
            color: "#F2F2F2"
            anchors.horizontalCenter: parent.horizontalCenter
        }

        Text {
            text: emptyRoot.subtitle
            font.pixelSize: 11
            color: "#92969D"
            horizontalAlignment: Text.AlignHCenter
            wrapMode: Text.WordWrap
            width: parent.width
            anchors.horizontalCenter: parent.horizontalCenter
        }

        Item { width: 1; height: 4 }

        Row {
            spacing: 12
            anchors.horizontalCenter: parent.horizontalCenter

            PillButton {
                text: "📁 SELECT MUSIC FOLDER"
                isPrimary: true
                onClicked: {
                    if (typeof libraryService !== "undefined" && libraryService) {
                        libraryService.browseFolder("music")
                    }
                }
            }

            PillButton {
                text: "📝 SELECT LYRICS FOLDER"
                onClicked: {
                    if (typeof libraryService !== "undefined" && libraryService) {
                        libraryService.browseFolder("lyrics")
                    }
                }
            }
        }
    }
}
