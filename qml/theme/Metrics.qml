pragma Singleton
import QtQuick

QtObject {
    readonly property int gridBase: 8
    readonly property int marginSmall: 8
    readonly property int marginMedium: 16
    readonly property int marginLarge: 24

    readonly property int radiusSmall: 4
    readonly property int radiusMedium: 6
    readonly property int radiusLarge: 8
    readonly property int radiusPill: 16

    readonly property int rowHeightCompact: 36
    readonly property int rowHeightNormal: 42

    readonly property int animDurationFast: 120
    readonly property int animDurationNormal: 200
    readonly property int animDurationSlow: 300
}
