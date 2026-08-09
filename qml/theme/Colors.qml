pragma Singleton
import QtQuick

QtObject {
    readonly property color bgBase: "#0B0C0E"
    readonly property color bgSurface: "#121417"
    readonly property color bgElevated: "#181B1F"
    readonly property color borderSubtle: "#272A2F"
    readonly property color borderFocus: "#3D424D"

    readonly property color accentRed: "#FF002B"
    readonly property color accentRedHover: "#D40024"
    readonly property color accentRedDim: "#2A0910"

    readonly property color textPrimary: "#F2F2F2"
    readonly property color textSecondary: "#92969D"
    readonly property color textMuted: "#62666D"

    readonly property color success: "#34D399"
    readonly property color successBg: "#132A1C"
    
    readonly property color warning: "#FBBF24"
    readonly property color warningBg: "#332200"

    readonly property color error: "#F87171"
    readonly property color errorBg: "#2A0910"
}
