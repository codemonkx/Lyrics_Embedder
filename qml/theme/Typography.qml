pragma Singleton
import QtQuick

QtObject {
    readonly property string fontFamily: "Inter, Cantarell, Segoe UI, sans-serif"
    readonly property string monoFontFamily: "Courier New, Consolas, monospace"

    readonly property int fontSizeCaption: 10
    readonly property int fontSizeSmall: 11
    readonly property int fontSizeBody: 12
    readonly property int fontSizeTitle: 14
    readonly property int fontSizeHeader: 18

    readonly property int fontWeightNormal: Font.Normal
    readonly property int fontWeightMedium: Font.Medium
    readonly property int fontWeightBold: Font.Bold
    readonly property int fontWeightBlack: Font.Black
}
