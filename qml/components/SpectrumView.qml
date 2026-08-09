import QtQuick
import QtQuick.Controls

GlassCard {
    id: spectrumContainer
    property string filePath: ""
    property bool isLoaded: filePath.length > 0

    implicitWidth: 400
    implicitHeight: 220

    Column {
        anchors.fill: parent
        anchors.margins: 12
        spacing: 8

        Text {
            text: ":: SPECTRAL FREQUENCY SPECTRUM ::"
            font.pixelSize: 11
            font.weight: Font.Bold
            font.letterSpacing: 1.0
            color: "#92969D"
        }

        Image {
            id: spectrumImage
            width: parent.width
            height: parent.height - 28
            fillMode: Image.PreserveAspectFit
            source: spectrumContainer.filePath ? "image://spectrum/" + encodeURIComponent(spectrumContainer.filePath) + "?t=" + Date.now() : ""
            visible: spectrumContainer.filePath.length > 0

            Text {
                anchors.centerIn: parent
                text: "Select a track to inspect FFT audio spectrum graph."
                font.pixelSize: 11
                color: "#62666D"
                visible: spectrumImage.status !== Image.Ready
            }
        }
    }
}
