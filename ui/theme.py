"""
LyricForge Nothing Tech Commercial Product Design System & Theme
Stealth matte charcoal palette (#0b0c0e), signature Nothing Red accents (#ff002b), dot-matrix typography tokens, and commercial QSS stylesheet.
"""

# Color Palette Tokens (Nothing Tech Commercial)
BG_BASE = "#0b0c0e"          # Stealth Matte Charcoal base background
BG_SURFACE = "#101216"       # Secondary surface (HeaderBar, Sidebar)
BG_CARD = "#16181d"          # Elevated Glass Container
BG_CARD_HOVER = "#1f2229"    # Hover surface
BG_ACTIVE = "#262a33"        # Active/pressed surface
BG_ELEVATED = BG_CARD

BORDER_SUBTLE = "#292d38"     # Crisp 1px subtle border
BORDER_FOCUS = "#ff002b"      # Focus border Nothing Red accent

ACCENT_RED = "#ff002b"        # Signature Nothing Red accent
ACCENT_RED_HOVER = "#ff1a3c"
ACCENT_RED_ACTIVE = "#d90024"

ACCENT_BLUE = "#38bdf8"       # Secondary accent
TEXT_PRIMARY = "#ffffff"     # High-contrast white
TEXT_SECONDARY = "#8a8d9b"   # Muted slate gray
TEXT_MUTED = "#585b6b"       # Subtext / Metadata

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
    border-color: #3b4150;
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
    border-color: #3f4657;
}}

QPushButton:pressed {{
    background-color: {BG_ACTIVE};
}}

QPushButton:disabled {{
    background-color: #121418;
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
    border-color: #ff3352;
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
    background-color: #1c0a0c;
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
    background-color: #222630;
    color: {TEXT_PRIMARY};
}}

QPushButton.viewSegmentActive {{
    background-color: #222630;
    border: 1px solid #383e4e;
    border-radius: 6px;
    padding: 5px 12px;
    color: {TEXT_PRIMARY};
    font-weight: 800;
    font-size: 9pt;
    letter-spacing: 0.5px;
}}

/* Input Fields */
QLineEdit {{
    background-color: #0e1014;
    border: 1px solid {BORDER_SUBTLE};
    border-radius: 8px;
    padding: 6px 12px;
    color: {TEXT_PRIMARY};
    selection-background-color: {ACCENT_RED};
    font-size: 10pt;
}}

QLineEdit:focus {{
    border: 1px solid {BORDER_FOCUS};
    background-color: #14171d;
}}

QTextEdit {{
    background-color: #0b0d10;
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
    alternate-background-color: #0f1115;
    gridline-color: transparent;
    border: none;
    outline: none;
}}

QTableWidget::item {{
    border-bottom: 1px solid #1e222b;
    padding: 8px 12px;
    color: {TEXT_PRIMARY};
    font-size: 9.5pt;
}}

QTableWidget::item:hover {{
    background-color: #1d212a;
}}

QTableWidget::item:selected {{
    background-color: #2e1015;
    color: #ffffff;
}}

QTableWidget::indicator {{
    width: 16px;
    height: 16px;
    border: 1px solid #3f4657;
    border-radius: 4px;
    background-color: #121418;
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
    border: 1px solid #3f4657;
    border-radius: 4px;
    background-color: #121418;
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
    background-color: #0e1014;
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
    background: #282d38;
    min-height: 28px;
    border-radius: 4px;
}}

QScrollBar::handle:vertical:hover {{
    background: #3b4252;
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
    background: #282d38;
    min-width: 28px;
    border-radius: 4px;
}}

QScrollBar::handle:horizontal:hover {{
    background: #3b4252;
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
