import os
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QLabel, QPushButton, QLineEdit, QFrame, QMenu, QButtonGroup
)
from PySide6.QtGui import QIcon

from ui.theme import (
    BG_SURFACE, BORDER_SUBTLE, TEXT_PRIMARY, TEXT_SECONDARY, ACCENT_BLUE
)
from ui.widgets.about_dialog import GNOMEAboutDialog

class GNOMEHeaderBar(QFrame):
    """
    Adwaita-style HeaderBar component with Libadwaita ViewSwitcher, search filter, Hamburger menu, and window controls.
    """
    page_changed = Signal(int)
    search_changed = Signal(str)

    def __init__(self, parent_win):
        super().__init__(parent_win)
        self.parent_win = parent_win
        self.setObjectName("headerFrame")
        self.setFixedHeight(52)
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setStyleSheet(f"""
            QFrame#headerFrame {{
                background-color: {BG_SURFACE};
                border-bottom: 1px solid {BORDER_SUBTLE};
                border-top-left-radius: 12px;
                border-top-right-radius: 12px;
            }}
        """)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 0, 16, 0)
        layout.setSpacing(12)

        # 1. Left Section: Logo & App Title
        logo_icon_lbl = QLabel()
        icon_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "assets", "app_icon.png")
        if os.path.exists(icon_path):
            logo_icon_lbl.setPixmap(QIcon(icon_path).pixmap(24, 24))
        else:
            logo_icon_lbl.setText("🎵")
            logo_icon_lbl.setStyleSheet("font-size: 14pt;")
        layout.addWidget(logo_icon_lbl)

        app_title = QLabel("LyricForge")
        app_title.setStyleSheet(f"font-weight: 800; font-size: 12pt; color: {TEXT_PRIMARY}; border: none;")
        layout.addWidget(app_title)

        ver_badge = QLabel("v1.2")
        ver_badge.setStyleSheet(f"font-size: 8pt; color: {TEXT_SECONDARY}; background: #2a2a2a; border: 1px solid {BORDER_SUBTLE}; border-radius: 4px; padding: 2px 6px; font-weight: 600;")
        layout.addWidget(ver_badge)

        layout.addStretch()

        # 2. Center Section: Libadwaita ViewSwitcher Segmented Control
        switcher_frame = QFrame()
        switcher_frame.setStyleSheet(f"""
            QFrame {{
                background-color: #191919;
                border: 1px solid {BORDER_SUBTLE};
                border-radius: 8px;
            }}
        """)
        switcher_lay = QHBoxLayout(switcher_frame)
        switcher_lay.setContentsMargins(3, 3, 3, 3)
        switcher_lay.setSpacing(2)

        self.btn_seg_library = QPushButton("Library")
        self.btn_seg_library.setProperty("class", "viewSegmentActive")
        self.btn_seg_library.setCheckable(True)
        self.btn_seg_library.setChecked(True)

        self.btn_seg_audio = QPushButton("Audio Inspector")
        self.btn_seg_audio.setProperty("class", "viewSegment")
        self.btn_seg_audio.setCheckable(True)

        self.btn_seg_reports = QPushButton("Reports")
        self.btn_seg_reports.setProperty("class", "viewSegment")
        self.btn_seg_reports.setCheckable(True)

        self.btn_seg_settings = QPushButton("Settings")
        self.btn_seg_settings.setProperty("class", "viewSegment")
        self.btn_seg_settings.setCheckable(True)

        self.seg_group = QButtonGroup(self)
        self.seg_group.addButton(self.btn_seg_library, 0)
        self.seg_group.addButton(self.btn_seg_audio, 1)
        self.seg_group.addButton(self.btn_seg_reports, 2)
        self.seg_group.addButton(self.btn_seg_settings, 3)
        self.seg_group.setExclusive(True)

        self.seg_group.idClicked.connect(self.on_segment_clicked)

        switcher_lay.addWidget(self.btn_seg_library)
        switcher_lay.addWidget(self.btn_seg_audio)
        switcher_lay.addWidget(self.btn_seg_reports)
        switcher_lay.addWidget(self.btn_seg_settings)

        layout.addWidget(switcher_frame)

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
        self.btn_menu.setFixedSize(32, 28)
        self.btn_menu.setStyleSheet(f"""
            QPushButton {{
                border: 1px solid {BORDER_SUBTLE}; background-color: #282828;
                color: {TEXT_PRIMARY}; font-size: 12pt; font-weight: bold; border-radius: 6px;
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

    def set_active_segment(self, index: int):
        btns = [self.btn_seg_library, self.btn_seg_audio, self.btn_seg_reports, self.btn_seg_settings]
        for i, btn in enumerate(btns):
            if i == index:
                btn.setChecked(True)
                btn.setProperty("class", "viewSegmentActive")
            else:
                btn.setChecked(False)
                btn.setProperty("class", "viewSegment")
            btn.style().unpolish(btn)
            btn.style().polish(btn)

    def on_segment_clicked(self, page_index: int):
        self.set_active_segment(page_index)
        self.page_changed.emit(page_index)

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
