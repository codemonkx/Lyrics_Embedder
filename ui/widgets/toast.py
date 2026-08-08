from PySide6.QtCore import Qt, QTimer, QPropertyAnimation, QRectF
from PySide6.QtWidgets import (
    QFrame, QHBoxLayout, QLabel, QWidget
)
from ui.theme import (
    BG_ELEVATED, BORDER_SUBTLE, TEXT_PRIMARY, ACCENT_BLUE
)

class GNOMEToast(QFrame):
    """
    Floating GNOME-style toast notification widget.
    """
    def __init__(self, parent: QWidget):
        super().__init__(parent)
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setStyleSheet(f"""
            GNOMEToast {{
                background-color: #242424;
                border: 1px solid #454545;
                border-radius: 8px;
            }}
            QLabel {{ border: none; background: transparent; color: {TEXT_PRIMARY}; font-size: 10pt; font-weight: 500; }}
        """)
        self.setFixedHeight(40)
        self.hide()

        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 0, 16, 0)
        layout.setSpacing(10)

        self.lbl_icon = QLabel("ℹ")
        self.lbl_icon.setStyleSheet(f"color: {ACCENT_BLUE}; font-weight: bold; font-size: 11pt;")
        
        self.lbl_text = QLabel("")
        
        layout.addWidget(self.lbl_icon)
        layout.addWidget(self.lbl_text)

        self.timer = QTimer(self)
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.hide_toast)

    def show_message(self, message: str, icon: str = "ℹ", duration_ms: int = 3500):
        self.lbl_icon.setText(icon)
        self.lbl_text.setText(message)
        self.adjustSize()
        
        parent = self.parentWidget()
        if parent:
            w = max(240, self.width() + 24)
            x = (parent.width() - w) // 2
            y = parent.height() - 70
            self.setGeometry(x, y, w, 40)
        
        self.raise_()
        self.show()
        self.timer.start(duration_ms)

    def hide_toast(self):
        self.hide()
