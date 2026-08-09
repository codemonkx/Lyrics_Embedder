pragma Singleton
import QtQuick

QtObject {
    readonly property string fontFamily: "Inter, Cantarell, Segoe UI, sans-serif"
    readonly property string monoFontFamily: "Courier New, Consolas, monospace"

    readonly property int fontSizeSmall: 11
    readonly property int fontSizeBody: 13
    readonly property int fontSizeTitle: 16
    readonly property int fontSizeHeader: 22

    readonly property int fontWeightNormal: Font.Normal
    readonly property int fontWeightBold: Font.Bold
    readonly property int fontWeightBlack: Font.Black
}
