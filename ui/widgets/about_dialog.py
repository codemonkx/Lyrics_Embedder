import os
from PySide6.QtCore import Qt, QUrl
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame
)
from PySide6.QtGui import QIcon, QDesktopServices

from ui.theme import (
    BG_SURFACE, BG_ELEVATED, BORDER_SUBTLE, TEXT_PRIMARY, TEXT_SECONDARY, ACCENT_RED
)

class GNOMEAboutDialog(QDialog):
    """
    Nothing OS-inspired About Modal Dialog.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("About LyricForge")
        self.setFixedSize(380, 430)
        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground, True)

        main_card = QFrame(self)
        main_card.setGeometry(0, 0, 380, 430)
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

        # Logo Icon with Red LED Dot
        lbl_icon = QLabel()
        icon_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "assets", "app_icon.png")
        if os.path.exists(icon_path):
            lbl_icon.setPixmap(QIcon(icon_path).pixmap(64, 64))
        else:
            lbl_icon.setText("🔴")
            lbl_icon.setStyleSheet(f"font-size: 36pt; color: {ACCENT_RED};")
        lbl_icon.setAlignment(Qt.AlignCenter)
        layout.addWidget(lbl_icon)

        # App Title (Nothing OS Style)
        lbl_title = QLabel("NOTHING // LYRICFORGE")
        lbl_title.setStyleSheet(f"font-size: 13pt; font-weight: 900; color: {TEXT_PRIMARY}; letter-spacing: 1.5px;")
        lbl_title.setAlignment(Qt.AlignCenter)
        layout.addWidget(lbl_title)

        # Version Badge
        lbl_ver = QLabel("VERSION 1.2.0 (NOTHING OS EDITION)")
        lbl_ver.setStyleSheet(f"font-size: 8pt; color: {ACCENT_RED}; font-weight: 800; letter-spacing: 1px;")
        lbl_ver.setAlignment(Qt.AlignCenter)
        layout.addWidget(lbl_ver)

        # Description
        lbl_desc = QLabel(
            "High-tech stealth lyrics matcher, tag embedder, and audio spectral verification utility engineered for modern desktop environments."
        )
        lbl_desc.setStyleSheet(f"font-size: 9pt; color: {TEXT_SECONDARY}; line-height: 18px;")
        lbl_desc.setWordWrap(True)
        lbl_desc.setAlignment(Qt.AlignCenter)
        layout.addWidget(lbl_desc)

        layout.addSpacing(8)

        # Credits & GitHub Link
        btn_github = QPushButton("🌐 VIEW ON GITHUB")
        btn_github.setStyleSheet(f"""
            QPushButton {{
                background-color: #1a080a;
                border: 1px solid {ACCENT_RED};
                border-radius: 8px;
                padding: 7px 16px;
                color: {ACCENT_RED};
                font-weight: 800;
                font-size: 8.5pt;
                letter-spacing: 1px;
            }}
            QPushButton:hover {{ background-color: {ACCENT_RED}; color: #ffffff; }}
        """)
        btn_github.clicked.connect(lambda: QDesktopServices.openUrl(QUrl("https://github.com/codemonkx/Lyrics_Embedder")))
        layout.addWidget(btn_github, 0, Qt.AlignCenter)

        layout.addStretch()

        # Close Button
        btn_close = QPushButton("CLOSE")
        btn_close.setMinimumWidth(110)
        btn_close.clicked.connect(self.accept)
        layout.addWidget(btn_close, 0, Qt.AlignCenter)
