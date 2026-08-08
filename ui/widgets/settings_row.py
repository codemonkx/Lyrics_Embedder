from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame, QHBoxLayout, QVBoxLayout, QLabel, QWidget
)
from ui.theme import (
    BG_ELEVATED, BORDER_SUBTLE, TEXT_PRIMARY, TEXT_SECONDARY
)

class GNOMESettingsRow(QFrame):
    """
    Libadwaita-inspired preference setting row widget.
    Displays a title, description, and right-aligned control widget.
    """
    def __init__(self, title: str, description: str = "", control_widget: QWidget = None, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setStyleSheet(f"""
            GNOMESettingsRow {{
                background-color: {BG_ELEVATED};
                border: 1px solid {BORDER_SUBTLE};
                border-radius: 8px;
            }}
            QLabel {{ border: none; background: transparent; }}
        """)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(16)

        # Left Column: Title + Description
        text_lay = QVBoxLayout()
        text_lay.setSpacing(2)

        lbl_title = QLabel(title)
        lbl_title.setStyleSheet(f"font-size: 10pt; font-weight: 600; color: {TEXT_PRIMARY};")
        text_lay.addWidget(lbl_title)

        if description:
            lbl_desc = QLabel(description)
            lbl_desc.setStyleSheet(f"font-size: 9pt; color: {TEXT_SECONDARY};")
            lbl_desc.setWordWrap(True)
            text_lay.addWidget(lbl_desc)

        layout.addLayout(text_lay, 1)

        # Right Column: Control Widget
        if control_widget:
            layout.addWidget(control_widget, 0, Qt.AlignRight | Qt.AlignVCenter)
