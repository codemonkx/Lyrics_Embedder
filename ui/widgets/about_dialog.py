import os
from PySide6.QtCore import Qt, QUrl
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame
)
from PySide6.QtGui import QIcon, QDesktopServices

from ui.theme import (
    BG_SURFACE, BG_ELEVATED, BORDER_SUBTLE, TEXT_PRIMARY, TEXT_SECONDARY, ACCENT_BLUE
)

class GNOMEAboutDialog(QDialog):
    """
    Adwaita-inspired About Modal Dialog.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("About LyricForge")
        self.setFixedSize(360, 420)
        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground, True)

        main_card = QFrame(self)
        main_card.setGeometry(0, 0, 360, 420)
        main_card.setStyleSheet(f"""
            QFrame {{
                background-color: {BG_SURFACE};
                border: 1px solid {BORDER_SUBTLE};
                border-radius: 12px;
            }}
            QLabel {{ border: none; background: transparent; }}
        """)

        layout = QVBoxLayout(main_card)
        layout.setContentsMargins(24, 28, 24, 24)
        layout.setSpacing(12)
        layout.setAlignment(Qt.AlignCenter)

        # Logo Icon
        lbl_icon = QLabel()
        icon_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "assets", "app_icon.png")
        if os.path.exists(icon_path):
            lbl_icon.setPixmap(QIcon(icon_path).pixmap(64, 64))
        else:
            lbl_icon.setText("🎵")
            lbl_icon.setStyleSheet("font-size: 36pt;")
        lbl_icon.setAlignment(Qt.AlignCenter)
        layout.addWidget(lbl_icon)

        # App Title
        lbl_title = QLabel("LyricForge")
        lbl_title.setStyleSheet(f"font-size: 15pt; font-weight: 700; color: {TEXT_PRIMARY};")
        lbl_title.setAlignment(Qt.AlignCenter)
        layout.addWidget(lbl_title)

        # Version Badge
        lbl_ver = QLabel("Version 1.2.0 (GNOME Edition)")
        lbl_ver.setStyleSheet(f"font-size: 8pt; color: {TEXT_SECONDARY}; font-weight: 600;")
        lbl_ver.setAlignment(Qt.AlignCenter)
        layout.addWidget(lbl_ver)

        # Description
        lbl_desc = QLabel(
            "Smart synchronized lyrics matcher, tag embedder, and lossless audio spectral verification utility for Linux and desktop systems."
        )
        lbl_desc.setStyleSheet(f"font-size: 9pt; color: {TEXT_SECONDARY}; line-height: 18px;")
        lbl_desc.setWordWrap(True)
        lbl_desc.setAlignment(Qt.AlignCenter)
        layout.addWidget(lbl_desc)

        layout.addSpacing(8)

        # Credits & GitHub Link
        btn_github = QPushButton("🌐 View on GitHub")
        btn_github.setStyleSheet(f"""
            QPushButton {{
                background-color: {BG_ELEVATED};
                border: 1px solid {BORDER_SUBTLE};
                border-radius: 6px;
                padding: 6px 12px;
                color: {ACCENT_BLUE};
                font-weight: 600;
                font-size: 9pt;
            }}
            QPushButton:hover {{ background-color: #353535; }}
        """)
        btn_github.clicked.connect(lambda: QDesktopServices.openUrl(QUrl("https://github.com/codemonkx/Lyrics_Embedder")))
        layout.addWidget(btn_github, 0, Qt.AlignCenter)

        layout.addStretch()

        # Close Button
        btn_close = QPushButton("Close")
        btn_close.setMinimumWidth(100)
        btn_close.clicked.connect(self.accept)
        layout.addWidget(btn_close, 0, Qt.AlignCenter)
