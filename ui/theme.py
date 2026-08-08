"""
LyricForge GNOME / Adwaita Design System & Theme
Stunning dark color palette, typography tokens, and Qt Style Sheets (QSS).
"""

# Color Palette Tokens (Adwaita Dark)
BG_BASE = "#181818"          # Deep dark neutral base background
BG_SURFACE = "#202020"       # Secondary surface (HeaderBar, Sidebar)
BG_CARD = "#262626"          # Card / Elevated Surface
BG_ELEVATED = BG_CARD
BG_CARD_HOVER = "#303030"    # Hover surface
BG_ACTIVE = "#383838"        # Active/pressed surface

BORDER_SUBTLE = "#333333"     # Crisp low-contrast border
BORDER_FOCUS = "#3584e4"      # Focus border accent

ACCENT_BLUE = "#3584e4"       # GNOME Blue primary accent
ACCENT_BLUE_HOVER = "#1c71d8"
ACCENT_BLUE_ACTIVE = "#1553a1"

TEXT_PRIMARY = "#ffffff"     # High-contrast off-white
TEXT_SECONDARY = "#a0a0a0"   # Muted gray
TEXT_MUTED = "#707070"       # Subtext / Metadata

COLOR_SUCCESS = "#34d399"    # Vibrant emerald green
COLOR_WARNING = "#fbbf24"    # Warm yellow/amber
COLOR_ERROR = "#f87171"      # Soft red

ADWAITA_DARK_QSS = f"""
/* Global Reset & Typography */
QWidget {{
    color: {TEXT_PRIMARY};
    font-family: "Inter", "Segoe UI", "Cantarell", system-ui, sans-serif;
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
    border-color: #404040;
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
    font-size: 18pt;
    font-weight: 800;
    color: {TEXT_PRIMARY};
}}

QLabel.pageSubtitle {{
    font-size: 10pt;
    color: {TEXT_SECONDARY};
}}

QLabel.sectionTitle {{
    font-size: 9pt;
    font-weight: 700;
    color: {TEXT_SECONDARY};
    letter-spacing: 0.8px;
    text-transform: uppercase;
}}

QLabel.mutedLabel {{
    color: {TEXT_MUTED};
    font-size: 9pt;
}}

/* Buttons */
QPushButton {{
    background-color: {BG_CARD};
    border: 1px solid {BORDER_SUBTLE};
    border-radius: 8px;
    padding: 7px 16px;
    color: {TEXT_PRIMARY};
    font-weight: 600;
    font-size: 10pt;
    min-height: 22px;
}}

QPushButton:hover {{
    background-color: {BG_CARD_HOVER};
    border-color: #444444;
}}

QPushButton:pressed {{
    background-color: {BG_ACTIVE};
}}

QPushButton:disabled {{
    background-color: #202020;
    border-color: {BORDER_SUBTLE};
    color: {TEXT_MUTED};
}}

/* Primary Button (GNOME Blue) */
QPushButton#primaryButton, QPushButton.primaryButton {{
    background-color: {ACCENT_BLUE};
    border: 1px solid {ACCENT_BLUE_HOVER};
    color: #ffffff;
    font-weight: 700;
    border-radius: 8px;
}}

QPushButton#primaryButton:hover, QPushButton.primaryButton:hover {{
    background-color: {ACCENT_BLUE_HOVER};
    border-color: #185fb4;
}}

QPushButton#primaryButton:pressed, QPushButton.primaryButton:pressed {{
    background-color: {ACCENT_BLUE_ACTIVE};
}}

QPushButton#primaryButton:disabled, QPushButton.primaryButton:disabled {{
    background-color: #1f3659;
    border-color: #1b2c45;
    color: #4a6a94;
}}

/* Destructive Button (GNOME Red) */
QPushButton#destructiveButton, QPushButton.destructiveButton {{
    background-color: {COLOR_ERROR};
    border: 1px solid #dc2626;
    color: #ffffff;
    font-weight: 700;
    border-radius: 8px;
}}

QPushButton#destructiveButton:hover, QPushButton.destructiveButton:hover {{
    background-color: #dc2626;
}}

QPushButton#destructiveButton:pressed, QPushButton.destructiveButton:pressed {{
    background-color: #b91c1c;
}}

/* Sidebar Navigation Buttons */
QPushButton.navRow {{
    background-color: transparent;
    border: none;
    border-radius: 8px;
    padding: 10px 14px;
    text-align: left;
    color: {TEXT_SECONDARY};
    font-weight: 600;
    font-size: 10pt;
}}

QPushButton.navRow:hover {{
    background-color: {BG_CARD_HOVER};
    color: {TEXT_PRIMARY};
}}

QPushButton.navRowActive {{
    background-color: {BG_CARD};
    border: 1px solid {BORDER_SUBTLE};
    border-left: 3.5px solid {ACCENT_BLUE};
    border-radius: 8px;
    padding: 10px 14px;
    text-align: left;
    color: {TEXT_PRIMARY};
    font-weight: 700;
    font-size: 10pt;
}}

/* Header View Switcher Segmented Buttons */
QPushButton.viewSegment {{
    background-color: transparent;
    border: none;
    border-radius: 6px;
    padding: 5px 12px;
    color: {TEXT_SECONDARY};
    font-weight: 600;
    font-size: 9.5pt;
}}

QPushButton.viewSegment:hover {{
    background-color: #2a2a2a;
    color: {TEXT_PRIMARY};
}}

QPushButton.viewSegmentActive {{
    background-color: #333333;
    border: 1px solid #444444;
    border-radius: 6px;
    padding: 5px 12px;
    color: {TEXT_PRIMARY};
    font-weight: 700;
    font-size: 9.5pt;
}}

/* Input Fields */
QLineEdit {{
    background-color: #1f1f1f;
    border: 1px solid {BORDER_SUBTLE};
    border-radius: 8px;
    padding: 6px 12px;
    color: {TEXT_PRIMARY};
    selection-background-color: {ACCENT_BLUE};
    font-size: 10pt;
}}

QLineEdit:focus {{
    border: 1px solid {BORDER_FOCUS};
    background-color: #242424;
}}

QTextEdit {{
    background-color: #1a1a1a;
    border: 1px solid {BORDER_SUBTLE};
    border-radius: 8px;
    color: {TEXT_PRIMARY};
    padding: 10px;
    selection-background-color: {ACCENT_BLUE};
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
    font-weight: 600;
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
    selection-background-color: {ACCENT_BLUE};
    color: {TEXT_PRIMARY};
    padding: 4px;
}}

/* Table Widget (GNOME List Style) */
QTableWidget {{
    background-color: transparent;
    alternate-background-color: #1c1c1c;
    gridline-color: transparent;
    border: none;
    outline: none;
}}

QTableWidget::item {{
    border-bottom: 1px solid #282828;
    padding: 8px 12px;
    color: {TEXT_PRIMARY};
    font-size: 10pt;
}}

QTableWidget::item:hover {{
    background-color: #282828;
}}

QTableWidget::item:selected {{
    background-color: #24354a;
    color: #ffffff;
}}

QTableWidget::indicator {{
    width: 16px;
    height: 16px;
    border: 1px solid #4a4a4a;
    border-radius: 4px;
    background-color: #222222;
}}

QTableWidget::indicator:checked {{
    background-color: {ACCENT_BLUE};
    border-color: {ACCENT_BLUE};
    image: url(data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAyNCAyNCIgd2lkdGg9IjE2IiBmaWxsPSJub25lIiBzdHJva2U9IiNmZmZmZmYiIHN0cm9rZS13aWR0aD0iMyIgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIiBzdHJva2UtbGluZWpvaW49InJvdW5kIj48cG9seWxpbmUgcG9pbnRzPSIyMCA2IDkgMTcgNCAxMiIvPjwvc3ZnPg==);
}}

QHeaderView::section {{
    background-color: {BG_SURFACE};
    color: {TEXT_SECONDARY};
    padding: 8px 12px;
    border: none;
    border-bottom: 1px solid {BORDER_SUBTLE};
    font-weight: 700;
    font-size: 9pt;
    text-transform: uppercase;
    letter-spacing: 0.8px;
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
    border: 1px solid #4a4a4a;
    border-radius: 4px;
    background-color: #222222;
}}

QCheckBox::indicator:checked {{
    background-color: {ACCENT_BLUE};
    border-color: {ACCENT_BLUE};
    image: url(data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAyNCAyNCIgd2lkdGg9IjE2IiBmaWxsPSJub25lIiBzdHJva2U9IiNmZmZmZmYiIHN0cm9rZS13aWR0aD0iMyIgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIiBzdHJva2UtbGluZWpvaW49InJvdW5kIj48cG9seWxpbmUgcG9pbnRzPSIyMCA2IDkgMTcgNCAxMiIvPjwvc3ZnPg==);
}}

QSlider::groove:horizontal {{
    border: none;
    height: 5px;
    background: {BORDER_SUBTLE};
    border-radius: 2.5px;
}}

QSlider::sub-page:horizontal {{
    background: {ACCENT_BLUE};
    border-radius: 2.5px;
}}

QSlider::handle:horizontal {{
    background: #ffffff;
    border: 1px solid {BORDER_SUBTLE};
    width: 16px;
    height: 16px;
    margin: -5.5px 0;
    border-radius: 8px;
}}

QSlider::handle:horizontal:hover {{
    background: #ffffff;
    border-color: {ACCENT_BLUE};
}}

/* Progress Bar */
QProgressBar {{
    border: none;
    border-radius: 4px;
    background-color: #1a1a1a;
    text-align: center;
    color: transparent;
    height: 8px;
}}

QProgressBar::chunk {{
    background-color: {ACCENT_BLUE};
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
    background: #383838;
    min-height: 28px;
    border-radius: 4px;
}}

QScrollBar::handle:vertical:hover {{
    background: #4a4a4a;
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
    background: #383838;
    min-width: 28px;
    border-radius: 4px;
}}

QScrollBar::handle:horizontal:hover {{
    background: #4a4a4a;
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
    font-size: 10pt;
    font-weight: 500;
}}

QMenu::item:selected {{
    background-color: {ACCENT_BLUE};
    color: #ffffff;
}}

QMenu::separator {{
    height: 1px;
    background-color: {BORDER_SUBTLE};
    margin: 4px 8px;
}}
"""
