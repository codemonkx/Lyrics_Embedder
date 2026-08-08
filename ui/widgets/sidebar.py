from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QFrame, QVBoxLayout, QPushButton, QLabel, QButtonGroup
)
from ui.theme import (
    BG_SURFACE, BORDER_SUBTLE, TEXT_SECONDARY
)

class GNOMESidebar(QFrame):
    """
    GNOME Libadwaita-style sidebar navigation component.
    """
    page_changed = Signal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("sidebarFrame")
        self.setFixedWidth(200)
        self.setAttribute(Qt.WA_StyledBackground, True)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 16, 12, 16)
        layout.setSpacing(6)

        # Section Header
        lbl_nav = QLabel("NAVIGATION")
        lbl_nav.setStyleSheet(f"font-size: 8pt; font-weight: 700; color: {TEXT_SECONDARY}; letter-spacing: 0.8px;")
        layout.addWidget(lbl_nav)
        layout.addSpacing(4)

        # Navigation Buttons
        self.btn_library = QPushButton("🎵  Library")
        self.btn_library.setProperty("class", "navRowActive")
        self.btn_library.setCheckable(True)
        self.btn_library.setChecked(True)

        self.btn_audio = QPushButton("🔬  Audio Inspector")
        self.btn_audio.setProperty("class", "navRow")
        self.btn_audio.setCheckable(True)

        self.btn_reports = QPushButton("📊  Reports")
        self.btn_reports.setProperty("class", "navRow")
        self.btn_reports.setCheckable(True)

        self.btn_settings = QPushButton("⚙️  Settings")
        self.btn_settings.setProperty("class", "navRow")
        self.btn_settings.setCheckable(True)

        self.nav_group = QButtonGroup(self)
        self.nav_group.addButton(self.btn_library, 0)
        self.nav_group.addButton(self.btn_audio, 1)
        self.nav_group.addButton(self.btn_reports, 2)
        self.nav_group.addButton(self.btn_settings, 3)
        self.nav_group.setExclusive(True)

        self.nav_group.idClicked.connect(self.on_nav_clicked)

        layout.addWidget(self.btn_library)
        layout.addWidget(self.btn_audio)
        layout.addWidget(self.btn_reports)
        layout.addWidget(self.btn_settings)

        layout.addStretch()

    def set_active_page(self, index: int):
        btns = [self.btn_library, self.btn_audio, self.btn_reports, self.btn_settings]
        for i, btn in enumerate(btns):
            if i == index:
                btn.setChecked(True)
                btn.setProperty("class", "navRowActive")
            else:
                btn.setChecked(False)
                btn.setProperty("class", "navRow")
            btn.style().unpolish(btn)
            btn.style().polish(btn)

    def on_nav_clicked(self, page_index: int):
        self.set_active_page(page_index)
        self.page_changed.emit(page_index)
