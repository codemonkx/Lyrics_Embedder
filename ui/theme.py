"""
LyricForge Nothing OS Design System & Theme
Iconic stealth OLED black palette, dot-matrix typography tokens, Nothing Red accents (#ff002b), and QSS stylesheet.
"""

# Color Palette Tokens (Nothing OS)
BG_BASE = "#000000"          # Stealth OLED Pure Black base background
BG_SURFACE = "#0a0a0a"       # Secondary surface (HeaderBar, Sidebar)
BG_CARD = "#121212"          # Card / Elevated Container
BG_CARD_HOVER = "#1a1a1a"    # Hover surface
BG_ACTIVE = "#222222"        # Active/pressed surface
BG_ELEVATED = BG_CARD

BORDER_SUBTLE = "#262626"     # Crisp 1px subtle border
BORDER_FOCUS = "#ff002b"      # Focus border Nothing Red accent

ACCENT_RED = "#ff002b"        # Signature Nothing Red accent
ACCENT_RED_HOVER = "#e50027"
ACCENT_RED_ACTIVE = "#cc0022"

ACCENT_BLUE = "#3584e4"       # Secondary accent
TEXT_PRIMARY = "#ffffff"     # High-contrast white
TEXT_SECONDARY = "#888888"   # Muted gray
TEXT_MUTED = "#555555"       # Subtext / Metadata

COLOR_SUCCESS = "#34d399"    # Emerald Green
COLOR_WARNING = "#fbbf24"    # Amber Yellow
COLOR_ERROR = "#ff002b"      # Nothing Red

NOTHING_OS_QSS = f"""
/* Global Reset & Typography */
QWidget {{
    color: {TEXT_PRIMARY};
    font-family: "Inter", "Segoe UI", "Cantarell", monospace, sans-serif;
    font-size: 10pt;
    background: transparent;
}}

QMainWindow {{
    background-color: {BG_BASE};
}}

QWidget#central {{
    background-color: {BG_BASE};
    border: 1px solid {BORDER_SUBTLE};
    border-radius: 12px;
}}

/* Tooltips */
QToolTip {{
    background-color: {BG_CARD};
    color: {TEXT_PRIMARY};
    border: 1px solid {BORDER_SUBTLE};
    border-radius: 6px;
    padding: 6px 10px;
    font-size: 9pt;
}}

/* Frames & Panels */
QFrame#sidebarFrame {{
    background-color: {BG_SURFACE};
    border-right: 1px solid {BORDER_SUBTLE};
    border-top-left-radius: 0px;
    border-bottom-left-radius: 12px;
}}

QFrame#headerFrame {{
    background-color: {BG_SURFACE};
    border-bottom: 1px solid {BORDER_SUBTLE};
    border-top-left-radius: 12px;
    border-top-right-radius: 12px;
}}

QFrame#cardFrame, QWidget.adwCard {{
    background-color: {BG_CARD};
    border: 1px solid {BORDER_SUBTLE};
    border-radius: 10px;
}}

QFrame#cardFrame:hover {{
    border-color: #383838;
}}

/* Scroll Areas */
QScrollArea {{
    border: none;
    background-color: transparent;
}}

QScrollArea > QWidget > QWidget {{
    background-color: transparent;
}}

/* Typography Classes */
QLabel.pageTitle {{
    font-size: 16pt;
    font-weight: 800;
    color: {TEXT_PRIMARY};
    letter-spacing: 1px;
}}

QLabel.pageSubtitle {{
    font-size: 9.5pt;
    color: {TEXT_SECONDARY};
}}

QLabel.sectionTitle {{
    font-size: 8.5pt;
    font-weight: 800;
    color: {TEXT_SECONDARY};
    letter-spacing: 1.5px;
    text-transform: uppercase;
}}

QLabel.mutedLabel {{
    color: {TEXT_MUTED};
    font-size: 9pt;
}}

/* Capsule Buttons */
QPushButton {{
    background-color: {BG_CARD};
    border: 1px solid {BORDER_SUBTLE};
    border-radius: 8px;
    padding: 7px 16px;
    color: {TEXT_PRIMARY};
    font-weight: 700;
    font-size: 9.5pt;
    min-height: 22px;
    letter-spacing: 0.5px;
}}

QPushButton:hover {{
    background-color: {BG_CARD_HOVER};
    border-color: #444444;
}}

QPushButton:pressed {{
    background-color: {BG_ACTIVE};
}}

QPushButton:disabled {{
    background-color: #121212;
    border-color: {BORDER_SUBTLE};
    color: {TEXT_MUTED};
}}

/* Primary Nothing Red Button */
QPushButton#primaryButton, QPushButton.primaryButton {{
    background-color: {ACCENT_RED};
    border: 1px solid {ACCENT_RED_HOVER};
    color: #ffffff;
    font-weight: 800;
    border-radius: 8px;
    letter-spacing: 0.8px;
}}

QPushButton#primaryButton:hover, QPushButton.primaryButton:hover {{
    background-color: {ACCENT_RED_HOVER};
    border-color: #ff2a4b;
}}

QPushButton#primaryButton:pressed, QPushButton.primaryButton:pressed {{
    background-color: {ACCENT_RED_ACTIVE};
}}

QPushButton#primaryButton:disabled {{
    background-color: #3d0d14;
    border-color: #2b080d;
    color: #8c3844;
}}

/* Destructive Button */
QPushButton#destructiveButton, QPushButton.destructiveButton {{
    background-color: #1a080a;
    border: 1px solid {ACCENT_RED};
    color: {ACCENT_RED};
    font-weight: 700;
    border-radius: 8px;
}}

QPushButton#destructiveButton:hover, QPushButton.destructiveButton:hover {{
    background-color: {ACCENT_RED};
    color: #ffffff;
}}

/* Sidebar Navigation Buttons */
QPushButton.navRow {{
    background-color: transparent;
    border: none;
    border-radius: 8px;
    padding: 10px 14px;
    text-align: left;
    color: {TEXT_SECONDARY};
    font-weight: 700;
    font-size: 9.5pt;
    letter-spacing: 0.5px;
}}

QPushButton.navRow:hover {{
    background-color: {BG_CARD_HOVER};
    color: {TEXT_PRIMARY};
}}

QPushButton.navRowActive {{
    background-color: {BG_CARD};
    border: 1px solid {BORDER_SUBTLE};
    border-left: 3.5px solid {ACCENT_RED};
    border-radius: 8px;
    padding: 10px 14px;
    text-align: left;
    color: {TEXT_PRIMARY};
    font-weight: 800;
    font-size: 9.5pt;
    letter-spacing: 0.5px;
}}

/* Header View Switcher Segmented Buttons */
QPushButton.viewSegment {{
    background-color: transparent;
    border: none;
    border-radius: 6px;
    padding: 5px 12px;
    color: {TEXT_SECONDARY};
    font-weight: 700;
    font-size: 9pt;
    letter-spacing: 0.5px;
}}

QPushButton.viewSegment:hover {{
    background-color: #222222;
    color: {TEXT_PRIMARY};
}}

QPushButton.viewSegmentActive {{
    background-color: #222222;
    border: 1px solid #383838;
    border-radius: 6px;
    padding: 5px 12px;
    color: {TEXT_PRIMARY};
    font-weight: 800;
    font-size: 9pt;
    letter-spacing: 0.5px;
}}

/* Input Fields */
QLineEdit {{
    background-color: #0c0c0c;
    border: 1px solid {BORDER_SUBTLE};
    border-radius: 8px;
    padding: 6px 12px;
    color: {TEXT_PRIMARY};
    selection-background-color: {ACCENT_RED};
    font-size: 10pt;
}}

QLineEdit:focus {{
    border: 1px solid {BORDER_FOCUS};
    background-color: #141414;
}}

QTextEdit {{
    background-color: #080808;
    border: 1px solid {BORDER_SUBTLE};
    border-radius: 8px;
    color: {TEXT_PRIMARY};
    padding: 10px;
    selection-background-color: {ACCENT_RED};
    font-size: 10pt;
}}

QTextEdit:focus {{
    border: 1px solid {BORDER_FOCUS};
}}

/* Combo Box */
QComboBox {{
    background-color: {BG_CARD};
    border: 1px solid {BORDER_SUBTLE};
    border-radius: 8px;
    padding: 5px 12px;
    color: {TEXT_PRIMARY};
    font-weight: 700;
    font-size: 9.5pt;
}}

QComboBox:hover {{
    background-color: {BG_CARD_HOVER};
}}

QComboBox::drop-down {{
    border: none;
    width: 24px;
}}

QComboBox QAbstractItemView {{
    background-color: {BG_SURFACE};
    border: 1px solid {BORDER_SUBTLE};
    border-radius: 8px;
    selection-background-color: {ACCENT_RED};
    color: {TEXT_PRIMARY};
    padding: 4px;
}}

/* Table Widget (Nothing OS Style) */
QTableWidget {{
    background-color: transparent;
    alternate-background-color: #0d0d0d;
    gridline-color: transparent;
    border: none;
    outline: none;
}}

QTableWidget::item {{
    border-bottom: 1px solid #1c1c1c;
    padding: 8px 12px;
    color: {TEXT_PRIMARY};
    font-size: 9.5pt;
}}

QTableWidget::item:hover {{
    background-color: #1a1a1a;
}}

QTableWidget::item:selected {{
    background-color: #2b0b10;
    color: #ffffff;
}}

QTableWidget::indicator {{
    width: 16px;
    height: 16px;
    border: 1px solid #3d3d3d;
    border-radius: 4px;
    background-color: #121212;
}}

QTableWidget::indicator:checked {{
    background-color: {ACCENT_RED};
    border-color: {ACCENT_RED};
    image: url(data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAyNCAyNCIgd2lkdGg9IjE2IiBmaWxsPSJub25lIiBzdHJva2U9IiNmZmZmZmYiIHN0cm9rZS13aWR0aD0iMyIgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIiBzdHJva2UtbGluZWpvaW49InJvdW5kIj48cG9seWxpbmUgcG9pbnRzPSIyMCA2IDkgMTcgNCAxMiIvPjwvc3ZnPg==);
}}

QHeaderView::section {{
    background-color: {BG_SURFACE};
    color: {TEXT_SECONDARY};
    padding: 8px 12px;
    border: none;
    border-bottom: 1px solid {BORDER_SUBTLE};
    font-weight: 800;
    font-size: 8.5pt;
    text-transform: uppercase;
    letter-spacing: 1px;
}}

/* Checkboxes & Sliders */
QCheckBox {{
    spacing: 10px;
    color: {TEXT_PRIMARY};
    font-size: 10pt;
}}

QCheckBox::indicator {{
    width: 18px;
    height: 18px;
    border: 1px solid #3d3d3d;
    border-radius: 4px;
    background-color: #121212;
}}

QCheckBox::indicator:checked {{
    background-color: {ACCENT_RED};
    border-color: {ACCENT_RED};
    image: url(data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAyNCAyNCIgd2lkdGg9IjE2IiBmaWxsPSJub25lIiBzdHJva2U9IiNmZmZmZmYiIHN0cm9rZS13aWR0aD0iMyIgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIiBzdHJva2UtbGluZWpvaW49InJvdW5kIj48cG9seWxpbmUgcG9pbnRzPSIyMCA2IDkgMTcgNCAxMiIvPjwvc3ZnPg==);
}}

QSlider::groove:horizontal {{
    border: none;
    height: 4px;
    background: {BORDER_SUBTLE};
    border-radius: 2px;
}}

QSlider::sub-page:horizontal {{
    background: {ACCENT_RED};
    border-radius: 2px;
}}

QSlider::handle:horizontal {{
    background: #ffffff;
    border: 1px solid {BORDER_SUBTLE};
    width: 16px;
    height: 16px;
    margin: -6px 0;
    border-radius: 8px;
}}

QSlider::handle:horizontal:hover {{
    background: #ffffff;
    border-color: {ACCENT_RED};
}}

/* Progress Bar */
QProgressBar {{
    border: none;
    border-radius: 4px;
    background-color: #0c0c0c;
    text-align: center;
    color: transparent;
    height: 8px;
}}

QProgressBar::chunk {{
    background-color: {ACCENT_RED};
    border-radius: 4px;
}}

/* Scrollbars */
QScrollBar:vertical {{
    border: none;
    background: transparent;
    width: 8px;
    margin: 0px;
}}

QScrollBar::handle:vertical {{
    background: #2a2a2a;
    min-height: 28px;
    border-radius: 4px;
}}

QScrollBar::handle:vertical:hover {{
    background: #444444;
}}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    border: none;
    background: none;
}}

QScrollBar:horizontal {{
    border: none;
    background: transparent;
    height: 8px;
    margin: 0px;
}}

QScrollBar::handle:horizontal {{
    background: #2a2a2a;
    min-width: 28px;
    border-radius: 4px;
}}

QScrollBar::handle:horizontal:hover {{
    background: #444444;
}}

QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
    border: none;
    background: none;
}}

/* Context Menu */
QMenu {{
    background-color: {BG_SURFACE};
    border: 1px solid {BORDER_SUBTLE};
    border-radius: 8px;
    padding: 6px;
}}

QMenu::item {{
    padding: 7px 18px;
    color: {TEXT_PRIMARY};
    border-radius: 6px;
    font-size: 9.5pt;
    font-weight: 600;
}}

QMenu::item:selected {{
    background-color: {ACCENT_RED};
    color: #ffffff;
}}

QMenu::separator {{
    height: 1px;
    background-color: {BORDER_SUBTLE};
    margin: 4px 8px;
}}
"""
