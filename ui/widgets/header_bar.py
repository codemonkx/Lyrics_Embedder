import os
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QLabel, QPushButton, QLineEdit, QFrame, QMenu
)
from PySide6.QtGui import QIcon, QAction

from ui.theme import (
    BG_SURFACE, BORDER_SUBTLE, TEXT_PRIMARY, TEXT_SECONDARY, ACCENT_BLUE
)
from ui.widgets.about_dialog import GNOMEAboutDialog

class GNOMEHeaderBar(QFrame):
    """
    Adwaita-style HeaderBar component with window dragging, Hamburger menu, search filter, and window controls.
    """
    page_changed = Signal(int)
    search_changed = Signal(str)

    def __init__(self, parent_win):
        super().__init__(parent_win)
        self.parent_win = parent_win
        self.setObjectName("headerFrame")
        self.setFixedHeight(48)
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setStyleSheet(f"""
            QFrame#headerFrame {{
                background-color: {BG_SURFACE};
                border-bottom: 1px solid {BORDER_SUBTLE};
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
            }}
        """)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 0, 16, 0)
        layout.setSpacing(12)

        # 1. Left Section: Logo & App Title
        logo_icon_lbl = QLabel()
        icon_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "assets", "app_icon.png")
        if os.path.exists(icon_path):
            logo_icon_lbl.setPixmap(QIcon(icon_path).pixmap(20, 20))
        layout.addWidget(logo_icon_lbl)

        app_title = QLabel("LyricForge")
        app_title.setStyleSheet(f"font-weight: 700; font-size: 11pt; color: {TEXT_PRIMARY}; border: none;")
        layout.addWidget(app_title)

        ver_badge = QLabel("v1.2")
        ver_badge.setStyleSheet(f"font-size: 8pt; color: {TEXT_SECONDARY}; background: #2d2d2d; border-radius: 4px; padding: 2px 6px; font-weight: 600;")
        layout.addWidget(ver_badge)

        layout.addStretch()

        # 2. Center Section: Active Page Title
        self.page_title_lbl = QLabel("Library")
        self.page_title_lbl.setStyleSheet(f"font-weight: 600; font-size: 10pt; color: {TEXT_PRIMARY}; border: none;")
        layout.addWidget(self.page_title_lbl)

        layout.addStretch()

        # 3. Right Section: Search Bar, Menu & Actions
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Search tracks...")
        self.search_bar.setFixedWidth(180)
        self.search_bar.setClearButtonEnabled(True)
        self.search_bar.textChanged.connect(self.search_changed.emit)
        layout.addWidget(self.search_bar)

        # Hamburger Menu Button
        self.btn_menu = QPushButton("≡")
        self.btn_menu.setFixedSize(30, 26)
        self.btn_menu.setStyleSheet(f"""
            QPushButton {{
                border: 1px solid {BORDER_SUBTLE}; background-color: #2d2d2d;
                color: {TEXT_PRIMARY}; font-size: 11pt; font-weight: bold; border-radius: 6px;
            }}
            QPushButton:hover {{ background-color: #353535; }}
        """)
        self.btn_menu.clicked.connect(self.show_main_menu)
        layout.addWidget(self.btn_menu)

        # Window Controls (Minimize, Close)
        btn_min = QPushButton("—")
        btn_min.setFixedSize(26, 24)
        btn_min.setStyleSheet(f"""
            QPushButton {{
                border: none; background: transparent; color: {TEXT_SECONDARY};
                font-size: 9pt; font-weight: bold; border-radius: 4px;
            }}
            QPushButton:hover {{ color: {TEXT_PRIMARY}; background-color: #353535; }}
        """)
        btn_min.clicked.connect(self.parent_win.showMinimized)
        layout.addWidget(btn_min)

        btn_close = QPushButton("✕")
        btn_close.setFixedSize(26, 24)
        btn_close.setStyleSheet(f"""
            QPushButton {{
                border: none; background: transparent; color: {TEXT_SECONDARY};
                font-size: 9pt; font-weight: bold; border-radius: 4px;
            }}
            QPushButton:hover {{ color: #ffffff; background-color: #e01b24; }}
        """)
        btn_close.clicked.connect(self.parent_win.close)
        layout.addWidget(btn_close)

        self.drag_position = None

    def set_page_title(self, title: str):
        self.page_title_lbl.setText(title)

    def show_main_menu(self):
        menu = QMenu(self)
        
        act_music = menu.addAction("📁 Open Music Folder...")
        act_lyrics = menu.addAction("📁 Open Lyrics Folder...")
        menu.addSeparator()
        
        act_report = menu.addAction("📊 Export Report (HTML)...")
        act_prefs = menu.addAction("⚙️ Preferences...")
        menu.addSeparator()
        
        act_about = menu.addAction("ℹ️ About LyricForge")

        pos = self.btn_menu.mapToGlobal(self.btn_menu.rect().bottomLeft())
        action = menu.exec(pos)

        if action == act_music:
            self.parent_win.browse_folder("music")
        elif action == act_lyrics:
            self.parent_win.browse_folder("lyrics")
        elif action == act_report:
            self.parent_win.export_report("html")
        elif action == act_prefs:
            self.parent_win.show_settings_popup()
        elif action == act_about:
            dlg = GNOMEAboutDialog(self.parent_win)
            dlg.exec()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_position = event.globalPosition().toPoint() - self.parent_win.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton and self.drag_position is not None:
            self.parent_win.move(event.globalPosition().toPoint() - self.drag_position)
            event.accept()
