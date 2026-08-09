import sys
from PySide6.QtCore import QObject, QEvent, QPoint

if sys.platform == "win32":
    import ctypes
    from ctypes import wintypes

class WindowsNativeEventFilter(QObject):
    """
    Win32 Native Event Filter enabling OS hit-testing (WM_NCHITTEST)
    for 100% smooth mouse border resizing and Snap Assist on frameless windows.
    """
    BORDER_MARGIN = 10

    def __init__(self, window, parent=None):
        super().__init__(parent)
        self.window = window

    def nativeEventFilter(self, eventType, message):
        if sys.platform == "win32":
            try:
                if eventType in (b"windows_generic_MSG", "windows_generic_MSG"):
                    msg = ctypes.wintypes.MSG.from_address(int(message))
                    WM_NCHITTEST = 0x0084
                    if msg.message == WM_NCHITTEST and not self.window.isMaximized():
                        x = ctypes.c_short(msg.lParam & 0xFFFF).value
                        y = ctypes.c_short((msg.lParam >> 16) & 0xFFFF).value
                        
                        local_pos = self.window.mapFromGlobal(QPoint(x, y))
                        lx, ly = local_pos.x(), local_pos.y()
                        w, h = self.window.width(), self.window.height()
                        m = self.BORDER_MARGIN
                        
                        if lx < m and ly < m: return True, 13
                        elif lx > w - m and ly < m: return True, 14
                        elif lx < m and ly > h - m: return True, 16
                        elif lx > w - m and ly > h - m: return True, 17
                        elif lx < m: return True, 10
                        elif lx > w - m: return True, 11
                        elif ly < m: return True, 12
                        elif ly > h - m: return True, 15
            except Exception:
                pass
        return False, 0
