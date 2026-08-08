from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QFrame, QVBoxLayout, QLabel, QPushButton
)
from ui.theme import (
    BG_ELEVATED, BORDER_SUBTLE, TEXT_PRIMARY, TEXT_SECONDARY
)

class GNOMEEmptyState(QFrame):
    """
    GNOME-style empty state container widget.
    """
    action_clicked = Signal()

    def __init__(self, icon_symbol: str, title: str, description: str, button_text: str = "", parent=None):
        super().__init__(parent)
        self.setObjectName("emptyStateOverlay")
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setStyleSheet(f"""
            QFrame#emptyStateOverlay {{
                background-color: {BG_ELEVATED};
                border: 1px solid {BORDER_SUBTLE};
                border-radius: 8px;
            }}
            QLabel {{ border: none; background: transparent; }}
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 48, 32, 48)
        layout.setSpacing(12)
        layout.setAlignment(Qt.AlignCenter)

        # Icon Symbol
        lbl_icon = QLabel(icon_symbol)
        lbl_icon.setStyleSheet("font-size: 32pt; color: #5e5c64; background: transparent;")
        lbl_icon.setAlignment(Qt.AlignCenter)
        layout.addWidget(lbl_icon)

        # Title
        self.lbl_title = QLabel(title)
        self.lbl_title.setStyleSheet(f"font-size: 12pt; font-weight: 700; color: {TEXT_PRIMARY};")
        self.lbl_title.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.lbl_title)

        # Description
        self.lbl_desc = QLabel(description)
        self.lbl_desc.setStyleSheet(f"font-size: 9pt; color: {TEXT_SECONDARY}; line-height: 18px;")
        self.lbl_desc.setAlignment(Qt.AlignCenter)
        self.lbl_desc.setWordWrap(True)
        self.lbl_desc.setMaximumWidth(400)
        layout.addWidget(self.lbl_desc)

        # Action Button
        self.btn_action = QPushButton(button_text)
        self.btn_action.setObjectName("primaryButton")
        self.btn_action.setMinimumHeight(32)
        self.btn_action.clicked.connect(self.action_clicked.emit)
        if not button_text:
            self.btn_action.setVisible(False)
        layout.addWidget(self.btn_action, 0, Qt.AlignCenter)
