import os
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QLabel, QPushButton, QLineEdit, QFrame, QMenu, QButtonGroup
)
from PySide6.QtGui import QIcon

from ui.theme import (
    BG_SURFACE, BORDER_SUBTLE, TEXT_PRIMARY, TEXT_SECONDARY, ACCENT_RED
)
from ui.widgets.about_dialog import GNOMEAboutDialog

class GNOMEHeaderBar(QFrame):
    """
    Nothing Tech Commercial Product HeaderBar component with ViewSwitcher, search filter, Hamburger menu, and window controls.
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

        # 1. Left Section: Red LED Dot & Nothing Title
        lbl_red_dot = QLabel("🔴")
        lbl_red_dot.setStyleSheet(f"font-size: 10pt; color: {ACCENT_RED}; border: none;")
        layout.addWidget(lbl_red_dot)

        app_title = QLabel("NOTHING // LYRICFORGE PRO")
        app_title.setStyleSheet(f"font-weight: 900; font-size: 10.5pt; color: {TEXT_PRIMARY}; letter-spacing: 1.5px; border: none;")
        layout.addWidget(app_title)

        ver_badge = QLabel("v1.2 PRO")
        ver_badge.setStyleSheet(f"font-size: 7.5pt; color: {ACCENT_RED}; background: #1a1e28; border: 1px solid #3d141b; border-radius: 4px; padding: 2px 6px; font-weight: 800;")
        layout.addWidget(ver_badge)

        layout.addStretch()

        # 2. Center Section: Nothing Tech Segmented ViewSwitcher
        switcher_frame = QFrame()
        switcher_frame.setStyleSheet(f"""
            QFrame {{
                background-color: #14171d;
                border: 1px solid {BORDER_SUBTLE};
                border-radius: 8px;
            }}
        """)
        switcher_lay = QHBoxLayout(switcher_frame)
        switcher_lay.setContentsMargins(3, 3, 3, 3)
        switcher_lay.setSpacing(2)

        self.btn_seg_library = QPushButton("LIBRARY")
        self.btn_seg_library.setProperty("class", "viewSegmentActive")
        self.btn_seg_library.setCheckable(True)
        self.btn_seg_library.setChecked(True)

        self.btn_seg_audio = QPushButton("AUDIO INSPECTOR")
        self.btn_seg_audio.setProperty("class", "viewSegment")
        self.btn_seg_audio.setCheckable(True)

        self.btn_seg_reports = QPushButton("REPORTS")
        self.btn_seg_reports.setProperty("class", "viewSegment")
        self.btn_seg_reports.setCheckable(True)

        self.btn_seg_settings = QPushButton("PREFERENCES")
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
        self.search_bar.setPlaceholderText("SEARCH TRACKS...")
        self.search_bar.setFixedWidth(180)
        self.search_bar.setClearButtonEnabled(True)
        self.search_bar.textChanged.connect(self.search_changed.emit)
        layout.addWidget(self.search_bar)

        # Hamburger Menu Button
        self.btn_menu = QPushButton("≡")
        self.btn_menu.setFixedSize(32, 28)
        self.btn_menu.setStyleSheet(f"""
            QPushButton {{
                border: 1px solid {BORDER_SUBTLE}; background-color: #1a1e27;
                color: {TEXT_PRIMARY}; font-size: 12pt; font-weight: bold; border-radius: 6px;
            }}
            QPushButton:hover {{ background-color: #262c39; }}
        """)
        self.btn_menu.clicked.connect(self.show_main_menu)
        layout.addWidget(self.btn_menu)

        # Window Controls (Minimize, Maximize/Restore, Close)
        btn_min = QPushButton("—")
        btn_min.setFixedSize(26, 24)
        btn_min.setToolTip("Minimize")
        btn_min.setStyleSheet(f"""
            QPushButton {{
                border: none; background: transparent; color: {TEXT_SECONDARY};
                font-size: 9pt; font-weight: bold; border-radius: 4px;
            }}
            QPushButton:hover {{ color: {TEXT_PRIMARY}; background-color: #262c39; }}
        """)
        btn_min.clicked.connect(self.parent_win.showMinimized)
        layout.addWidget(btn_min)

        self.btn_max = QPushButton("☐")
        self.btn_max.setFixedSize(26, 24)
        self.btn_max.setToolTip("Maximize / Restore")
        self.btn_max.setStyleSheet(f"""
            QPushButton {{
                border: none; background: transparent; color: {TEXT_SECONDARY};
                font-size: 10pt; font-weight: bold; border-radius: 4px;
            }}
            QPushButton:hover {{ color: {TEXT_PRIMARY}; background-color: #262c39; }}
        """)
        self.btn_max.clicked.connect(self.parent_win.toggle_maximize)
        layout.addWidget(self.btn_max)

        btn_close = QPushButton("✕")
        btn_close.setFixedSize(26, 24)
        btn_close.setToolTip("Close")
        btn_close.setStyleSheet(f"""
            QPushButton {{
                border: none; background: transparent; color: {TEXT_SECONDARY};
                font-size: 9pt; font-weight: bold; border-radius: 4px;
            }}
            QPushButton:hover {{ color: #ffffff; background-color: {ACCENT_RED}; }}
        """)
        btn_close.clicked.connect(self.parent_win.close)
        layout.addWidget(btn_close)

        self.drag_position = None

    def update_max_button_icon(self, is_maximized: bool):
        self.btn_max.setText("❐" if is_maximized else "☐")

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
        
        act_music = menu.addAction("📁 OPEN MUSIC FOLDER...")
        act_lyrics = menu.addAction("📁 OPEN LYRICS FOLDER...")
        menu.addSeparator()
        
        act_report = menu.addAction("📊 EXPORT REPORT (HTML)...")
        act_prefs = menu.addAction("⚙️ PREFERENCES...")
        menu.addSeparator()
        
        act_about = menu.addAction("ℹ️ ABOUT LYRICFORGE PRO")

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

    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.parent_win.toggle_maximize()
            event.accept()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_position = event.globalPosition().toPoint() - self.parent_win.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton and self.drag_position is not None:
            if not self.parent_win.isMaximized():
                self.parent_win.move(event.globalPosition().toPoint() - self.drag_position)
            event.accept()
